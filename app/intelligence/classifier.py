"""
KIR AI Document Intelligence — Semantic Classifier.

Determines the general semantic type (ContentType) of a ContentUnit.
Delegates to the LLM for deep classification.
"""

from __future__ import annotations

from app.ai.client import AICapability, GenerationRequest
from app.core.exceptions import ClassificationError
from app.core.logging import get_logger
from app.intelligence.output_validator import OutputValidator
from app.intelligence.prompt_loader import PromptLoader, get_prompt_loader
from app.intelligence.schemas import AIClassificationOutput, ContentType, ContentUnit

log = get_logger(__name__)

_DEFAULT_SYSTEM_PROMPT = (
    "You are an expert document intelligence AI.\n"
    "Your task is to classify the semantic type of a content unit.\n"
    "Output valid JSON conforming to the AIClassificationOutput schema."
)


class SemanticClassifier:
    """Classifies ContentUnits into general semantic types."""

    def __init__(
        self,
        validator: OutputValidator | None = None,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self.validator = validator or OutputValidator()
        self.prompt_loader = prompt_loader or get_prompt_loader()

    @property
    def system_prompt(self) -> str:
        template = self.prompt_loader.get_prompt("content_intelligence_v1", _DEFAULT_SYSTEM_PROMPT)
        return template.system_prompt

    async def classify(
        self,
        unit: ContentUnit,
        context_before: str = "",
        context_after: str = "",
        job_id: str | None = None,
    ) -> AIClassificationOutput:
        """Determine the general ContentType of a unit.

        Parameters
        ----------
        unit:
            The unit to classify.
        context_before:
            Text of the preceding units for context.
        context_after:
            Text of the succeeding units for context.
        job_id:
            Active pipeline job ID.

        Returns
        -------
        AIClassificationOutput
            Structured classification result.

        Raises
        ------
        ClassificationError
            If classification fails entirely.
        """
        # If it's a known structural type, we can skip LLM for obvious ones
        if unit.content_type == ContentType.TITLE:
            return AIClassificationOutput(
                unit_id=unit.unit_id,
                content_type=ContentType.TITLE,
                reasons=["Structural heading"],
            )

        user_prompt = (
            f"CONTEXT BEFORE:\n{context_before}\n\n"
            f"CONTENT TO CLASSIFY:\n{unit.normalized_text}\n\n"
            f"CONTEXT AFTER:\n{context_after}\n\n"
            f"UNIT ID: {unit.unit_id}\n"
            f"CURRENT HEADING TITLE: {unit.title or 'None'}\n"
        )

        request = GenerationRequest(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            required_capability=AICapability.SEMANTIC_REASONING,
            json_mode=True,
            job_id=job_id,
            step="semantic_classification",
        )

        try:
            result = await self.validator.generate_and_validate(
                request=request,
                schema=AIClassificationOutput,
            )
            
            # Ensure the returned unit_id matches
            if result.unit_id != unit.unit_id:
                result.unit_id = unit.unit_id
                
            return result
            
        except Exception as exc:
            log.warning(
                "classifier.failure",
                unit_id=unit.unit_id,
                error=str(exc),
                job_id=job_id,
            )
            raise ClassificationError(
                f"Failed to classify unit {unit.unit_id}",
                job_id=job_id,
                step="semantic_classification",
            ) from exc
