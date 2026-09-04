"""
KIR AI Document Intelligence — Quality Critic Agent.

Evaluates intermediate or final outputs for source fidelity, 
traceability rules, and structural consistency.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.ai.client import AICapability, GenerationRequest
from app.intelligence.output_validator import OutputValidator
from app.intelligence.prompt_loader import PromptLoader, get_prompt_loader
from app.intelligence.schemas import (
    AIQualityCritiqueOutput,
    BlueprintProposal,
)

_DEFAULT_SYSTEM_PROMPT = (
    "You are a strict Quality Critic AI for document generation.\n"
    "Evaluate the provided Blueprint Proposal for structural consistency and source fidelity.\n"
    "Output valid JSON conforming to the AIQualityCritiqueOutput schema."
)


class QualityCritic(BaseAgent):
    """Agent responsible for enforcing quality and source fidelity."""

    def __init__(
        self,
        validator: OutputValidator | None = None,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self.validator = validator or OutputValidator()
        self.prompt_loader = prompt_loader or get_prompt_loader()

    @property
    def name(self) -> str:
        return "quality_critic"

    @property
    def responsibility(self) -> str:
        return "Critique outputs for fidelity, traceability, and structure."

    @property
    def system_prompt(self) -> str:
        template = self.prompt_loader.get_prompt("quality_critic_v1", _DEFAULT_SYSTEM_PROMPT)
        return template.system_prompt

    async def critique_blueprint(
        self, proposal: BlueprintProposal, job_id: str | None = None
    ) -> AIQualityCritiqueOutput:
        """Evaluate a BlueprintProposal."""
        self.log_start(job_id=job_id)
        
        try:
            # We serialize the proposal summary here
            groups_summary = [
                {"id": g.group_id, "type": g.blueprint_candidate.value, "title": g.title}
                for g in proposal.content_groups
            ]
            
            user_prompt = (
                f"Evaluate this document blueprint proposal:\n"
                f"Title: {proposal.document_title}\n"
                f"Genre: {proposal.document_genre.value}\n"
                f"Groups: {groups_summary}\n"
            )
            
            request = GenerationRequest(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                required_capability=AICapability.CRITIQUE,
                json_mode=True,
                job_id=job_id,
                step="quality_critique",
            )
            
            result = await self.validator.generate_and_validate(
                request=request, schema=AIQualityCritiqueOutput
            )
            
            self.log_complete(job_id=job_id, is_acceptable=result.is_acceptable)
            return result
            
        except Exception as exc:
            self.log_failure(exc, job_id=job_id)
            raise
