"""
KIR AI Document Intelligence — Relationship Extractor.

Extracts semantic relationships between ContentUnits to build
a traceability graph (e.g. Conclusion -> answers -> Research Question).
"""

from __future__ import annotations

from app.ai.client import AICapability, GenerationRequest
from app.core.exceptions import RelationshipError
from app.core.logging import get_logger
from app.intelligence.output_validator import OutputValidator
from app.intelligence.prompt_loader import PromptLoader, get_prompt_loader
from app.intelligence.schemas import AIRelationshipOutput, ContentUnit

log = get_logger(__name__)

_DEFAULT_SYSTEM_PROMPT = (
    "You are an expert document intelligence AI.\n"
    "Your task is to identify relationships between the provided content units.\n"
    "For example: A Conclusion 'answers' a Research Question, or a Finding 'is_derived_from' Data.\n"
    "Output valid JSON conforming to the AIRelationshipOutput schema."
)


class RelationshipExtractor:
    """Extracts semantic edges between units to form a traceability graph."""

    def __init__(
        self,
        validator: OutputValidator | None = None,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self.validator = validator or OutputValidator()
        self.prompt_loader = prompt_loader or get_prompt_loader()

    @property
    def system_prompt(self) -> str:
        template = self.prompt_loader.get_prompt("relationship_extractor_v1", _DEFAULT_SYSTEM_PROMPT)
        return template.system_prompt

    async def extract_relationships(
        self,
        units: list[ContentUnit],
        job_id: str | None = None,
    ) -> AIRelationshipOutput:
        """Extract relationships across a list of units.

        Parameters
        ----------
        units:
            List of units to analyze. Should be bounded (e.g. one section or 
            a targeted subset) to avoid context limit overflow.
        job_id:
            Active pipeline job ID.

        Returns
        -------
        AIRelationshipOutput
            Extracted relationships.

        Raises
        ------
        RelationshipError
            If relationship extraction fails.
        """
        if len(units) < 2:
            return AIRelationshipOutput(relationships=[])

        # Serialize units for the LLM
        units_json = []
        for u in units:
            u_dict = {
                "unit_id": u.unit_id,
                "content_type": u.content_type.value,
                "text": u.normalized_text[:500]  # truncate very long units
            }
            if u.research_role:
                u_dict["research_role"] = u.research_role.value
            units_json.append(u_dict)

        user_prompt = (
            "Identify relationships between the following units:\n\n"
            f"{units_json}\n"
        )

        request = GenerationRequest(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            required_capability=AICapability.SEMANTIC_REASONING,
            json_mode=True,
            job_id=job_id,
            step="relationship_extraction",
        )

        try:
            return await self.validator.generate_and_validate(
                request=request,
                schema=AIRelationshipOutput,
            )
        except Exception as exc:
            log.warning(
                "relationship_extractor.failure",
                unit_count=len(units),
                error=str(exc),
                job_id=job_id,
            )
            raise RelationshipError(
                f"Failed to extract relationships for {len(units)} units",
                job_id=job_id,
                step="relationship_extraction",
            ) from exc
