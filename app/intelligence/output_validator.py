"""
KIR AI Document Intelligence — Structured Output Validator.

Parses and validates LLM JSON output against Pydantic schemas.
Implements the rule: "LLM output must be treated as UNTRUSTED INPUT".

Includes retry/repair logic.
"""

from __future__ import annotations

import json
import re
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from app.ai.client import AICapability, GenerationRequest
from app.ai.fallback import FallbackChain
from app.config.settings import AppSettings, get_settings
from app.core.exceptions import StructuredOutputError
from app.core.logging import get_logger

log = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

# Regex to extract JSON block if the model wraps it in markdown ```json ... ```
_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", re.DOTALL)


class OutputValidator:
    """Validates raw LLM responses against structured Pydantic contracts."""

    def __init__(
        self,
        fallback_chain: FallbackChain | None = None,
        settings: AppSettings | None = None,
    ) -> None:
        self.fallback_chain = fallback_chain or FallbackChain()
        self.settings = settings or get_settings()

    async def generate_and_validate(
        self,
        request: GenerationRequest,
        schema: type[T],
    ) -> T:
        """Execute a generation request and strictly validate the output.

        If validation fails, it attempts to repair the output via a retry prompt
        up to `max_repair_attempts`.

        Parameters
        ----------
        request:
            The generation request. Should have json_mode=True.
        schema:
            The Pydantic BaseModel class to validate against.

        Returns
        -------
        T
            The validated Pydantic model instance.

        Raises
        ------
        StructuredOutputError
            If output cannot be validated after all repair attempts.
        AIError
            If the provider fails completely.
        """
        max_attempts = self.settings.max_repair_attempts + 1
        current_request = request
        last_error_msg = ""
        raw_output = ""

        for attempt in range(1, max_attempts + 1):
            log.debug(
                "output_validator.generate_attempt",
                attempt=attempt,
                max_attempts=max_attempts,
                job_id=request.job_id,
                step=request.step,
            )

            # 1. Generate
            response = await self.fallback_chain.execute(current_request)
            raw_output = response.content

            # 2. Extract and Parse JSON
            extracted_json = self._extract_json(raw_output)
            
            try:
                parsed_dict = json.loads(extracted_json)
            except json.JSONDecodeError as exc:
                last_error_msg = f"Invalid JSON format: {exc.msg}"
                log.warning(
                    "output_validator.json_decode_error",
                    error=last_error_msg,
                    attempt=attempt,
                    job_id=request.job_id,
                    step=request.step,
                )
                current_request = self._create_repair_request(
                    original_request=request,
                    bad_output=raw_output,
                    error_msg=last_error_msg,
                )
                continue

            # 3. Validate against Pydantic Schema
            try:
                # If parsed_dict is a list, and schema expects a single object, this will fail naturally.
                # If the schema itself is a root model for a list, it will pass.
                # Most of our contracts are single objects containing lists.
                validated_model = schema.model_validate(parsed_dict)
                
                if attempt > 1:
                    log.info(
                        "output_validator.repair_successful",
                        attempt=attempt,
                        job_id=request.job_id,
                        step=request.step,
                    )
                
                return validated_model
            
            except PydanticValidationError as exc:
                last_error_msg = f"Schema validation failed:\n{exc}"
                log.warning(
                    "output_validator.schema_validation_error",
                    errors=exc.errors(),
                    attempt=attempt,
                    job_id=request.job_id,
                    step=request.step,
                )
                current_request = self._create_repair_request(
                    original_request=request,
                    bad_output=raw_output,
                    error_msg=last_error_msg,
                )
                continue

        # Exhausted attempts
        raise StructuredOutputError(
            f"Failed to produce valid structured output after {max_attempts} attempts. Last error: {last_error_msg}",
            raw_output=raw_output,
            repair_attempts=max_attempts - 1,
            job_id=request.job_id,
            step=request.step,
        )

    def _extract_json(self, raw_output: str) -> str:
        """Extract JSON from potential markdown wrappers."""
        raw_output = raw_output.strip()
        
        # Check for ```json ... ``` blocks
        match = _JSON_BLOCK_RE.search(raw_output)
        if match:
            return match.group(1).strip()
            
        # Sometimes models just output the JSON but with leading/trailing text
        # If it looks like it starts with { or [, try to slice it
        start_idx = raw_output.find("{")
        list_start = raw_output.find("[")
        
        if start_idx == -1 and list_start == -1:
            return raw_output  # No obvious JSON bounds, return as is and let json.loads fail
            
        if start_idx != -1 and (list_start == -1 or start_idx < list_start):
            end_idx = raw_output.rfind("}")
            if end_idx != -1 and end_idx > start_idx:
                return raw_output[start_idx : end_idx + 1]
                
        if list_start != -1 and (start_idx == -1 or list_start < start_idx):
            end_idx = raw_output.rfind("]")
            if end_idx != -1 and end_idx > list_start:
                return raw_output[list_start : end_idx + 1]

        return raw_output

    def _create_repair_request(
        self, original_request: GenerationRequest, bad_output: str, error_msg: str
    ) -> GenerationRequest:
        """Create a new request instructing the model to fix its previous output."""
        
        repair_prompt = (
            f"Your previous response failed validation.\n\n"
            f"ERROR DETAILS:\n{error_msg}\n\n"
            f"YOUR PREVIOUS BAD OUTPUT:\n{bad_output}\n\n"
            f"INSTRUCTION:\n"
            f"Fix the output so it is strictly valid JSON and conforms to the required schema. "
            f"Output ONLY the fixed JSON, with no other text."
        )

        return GenerationRequest(
            system_prompt=original_request.system_prompt,
            user_prompt=repair_prompt,
            # Downgrade capability to STRUCTURED_OUTPUT if it was something else, 
            # since now the main task is just fixing syntax/schema.
            required_capability=AICapability.STRUCTURED_OUTPUT,
            max_tokens=original_request.max_tokens,
            temperature=0.1,  # Lower temperature for repair
            json_mode=True,
            job_id=original_request.job_id,
            step=original_request.step,
        )
