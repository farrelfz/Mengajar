"""
KIR AI Document Intelligence — Visual Intent Detector.

Analyzes ContentUnits to propose semantic visual intents
(e.g. TEXT_FOCUSED, COMPARATIVE, PROCESS_FLOW) without tying them
to specific CSS or layout implementations.
"""

from __future__ import annotations

from app.ai.client import AICapability, GenerationRequest
from app.core.exceptions import VisualIntentError
from app.core.logging import get_logger
from app.intelligence.output_validator import OutputValidator
from app.intelligence.prompt_loader import PromptLoader, get_prompt_loader
from app.intelligence.schemas import AIVisualIntentOutput, ContentUnit

log = get_logger(__name__)

_DEFAULT_SYSTEM_PROMPT = (
    "You are an expert document design planner.\n"
    "Analyze the content and propose the semantic VISUAL INTENT.\n"
    "Do NOT output CSS or HTML. Only propose conceptual layouts like "
    "PROCESS_FLOW, COMPARATIVE, DATA_TREND, etc.\n"
    "Output valid JSON conforming to the AIVisualIntentOutput schema."
)


class VisualIntentDetector:
    """Detects appropriate visual treatment intents for content units."""

    def __init__(
        self,
        validator: OutputValidator | None = None,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self.validator = validator or OutputValidator()
        self.prompt_loader = prompt_loader or get_prompt_loader()

    @property
    def system_prompt(self) -> str:
        template = self.prompt_loader.get_prompt("visual_intent_detector_v1", _DEFAULT_SYSTEM_PROMPT)
        return template.system_prompt

    async def detect_intents(
        self,
        units: list[ContentUnit],
        job_id: str | None = None,
    ) -> AIVisualIntentOutput:
        """Detect visual intents for a group of units.

        Parameters
        ----------
        units:
            The units to analyze together (often a single section).
        job_id:
            Active pipeline job ID.

        Returns
        -------
        AIVisualIntentOutput
            Structured visual intents mapped to unit_ids.

        Raises
        ------
        VisualIntentError
            If detection fails.
        """
        if not units:
            return AIVisualIntentOutput(intents=[])

        # Serialize units
        units_json = []
        for u in units:
            u_dict = {
                "unit_id": u.unit_id,
                "content_type": u.content_type.value,
                "text": u.normalized_text[:1000]
            }
            if u.research_role:
                u_dict["research_role"] = u.research_role.value
            units_json.append(u_dict)

        user_prompt = (
            "Propose visual intents for the following units. "
            "Evaluate if they form a sequence, comparison, data chart, etc.\n\n"
            f"{units_json}\n"
        )

        request = GenerationRequest(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            required_capability=AICapability.SEMANTIC_REASONING,
            json_mode=True,
            job_id=job_id,
            step="visual_intent_detection",
        )

        try:
            return await self.validator.generate_and_validate(
                request=request,
                schema=AIVisualIntentOutput,
            )
        except Exception as exc:
            log.warning(
                "visual_intent_detector.failure",
                unit_count=len(units),
                error=str(exc),
                job_id=job_id,
            )
            raise VisualIntentError(
                f"Failed to detect visual intents for {len(units)} units",
                job_id=job_id,
                step="visual_intent_detection",
            ) from exc
