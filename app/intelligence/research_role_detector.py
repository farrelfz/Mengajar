"""
KIR AI Document Intelligence — Research Role Detector.

Determines the specific KTI BAB 1-5 semantic role of a ContentUnit
when the document genre is RESEARCH_REPORT.
"""

from __future__ import annotations

from app.ai.client import AICapability, GenerationRequest
from app.core.exceptions import ResearchRoleDetectionError
from app.core.logging import get_logger
from app.intelligence.output_validator import OutputValidator
from app.intelligence.prompt_loader import PromptLoader, get_prompt_loader
from app.intelligence.schemas import AIClassificationOutput, ContentUnit

log = get_logger(__name__)

_DEFAULT_SYSTEM_PROMPT = (
    "You are an expert academic research AI analyzing a Karya Tulis Ilmiah (KTI).\n"
    "Your task is to identify the specific research semantic role (e.g. RESEARCH_PROBLEM, "
    "RESEARCH_METHOD, RESEARCH_FINDING, RESEARCH_INTERPRETATION).\n"
    "Pay special attention to distinguishing DATA vs RESULT vs FINDING vs INTERPRETATION vs DISCUSSION.\n"
    "Output valid JSON conforming to the AIClassificationOutput schema."
)


class ResearchRoleDetector:
    """Detects KTI-specific research roles for content units."""

    def __init__(
        self,
        validator: OutputValidator | None = None,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self.validator = validator or OutputValidator()
        self.prompt_loader = prompt_loader or get_prompt_loader()

    @property
    def system_prompt(self) -> str:
        template = self.prompt_loader.get_prompt("research_role_classifier_v1", _DEFAULT_SYSTEM_PROMPT)
        return template.system_prompt

    async def detect(
        self,
        unit: ContentUnit,
        context_before: str = "",
        context_after: str = "",
        job_id: str | None = None,
    ) -> AIClassificationOutput:
        """Determine the research_role and kti_bab for a unit.

        Parameters
        ----------
        unit:
            The unit to classify. Its content_type may already be set.
        context_before:
            Text of preceding units.
        context_after:
            Text of succeeding units.
        job_id:
            Active pipeline job ID.

        Returns
        -------
        AIClassificationOutput
            Structured output with research_role and kti_bab fields populated.

        Raises
        ------
        ResearchRoleDetectionError
            If role detection fails.
        """
        user_prompt = (
            f"GENERAL TYPE: {unit.content_type.value}\n\n"
            f"CONTEXT BEFORE:\n{context_before}\n\n"
            f"CONTENT TO CLASSIFY:\n{unit.normalized_text}\n\n"
            f"CONTEXT AFTER:\n{context_after}\n\n"
            f"UNIT ID: {unit.unit_id}\n"
        )

        request = GenerationRequest(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            required_capability=AICapability.SEMANTIC_REASONING,
            json_mode=True,
            job_id=job_id,
            step="research_role_detection",
        )

        try:
            result = await self.validator.generate_and_validate(
                request=request,
                schema=AIClassificationOutput,
            )
            
            if result.unit_id != unit.unit_id:
                result.unit_id = unit.unit_id
                
            return result
            
        except Exception as exc:
            log.warning(
                "research_role_detector.failure",
                unit_id=unit.unit_id,
                error=str(exc),
                job_id=job_id,
            )
            raise ResearchRoleDetectionError(
                f"Failed to detect research role for unit {unit.unit_id}",
                job_id=job_id,
                step="research_role_detection",
            ) from exc
