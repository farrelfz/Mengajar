"""
KIR AI Document Intelligence — Document Planner Agent.

Consumes an AnalysisResult and runs the BlueprintProposer algorithm
to generate a BlueprintProposal.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.intelligence.blueprint_proposer import BlueprintProposer
from app.intelligence.output_validator import OutputValidator
from app.intelligence.schemas import (
    AnalysisResult,
    BlueprintProposal,
)


class DocumentPlanner(BaseAgent):
    """Agent responsible for planning the document structure (BlueprintProposal)."""

    def __init__(
        self,
        proposer: BlueprintProposer | None = None,
        validator: OutputValidator | None = None,
    ) -> None:
        self.proposer = proposer or BlueprintProposer()
        self.validator = validator or OutputValidator()

    @property
    def name(self) -> str:
        return "document_planner"

    @property
    def responsibility(self) -> str:
        return "Transform semantic analysis into a blueprint-ready structural model."

    async def plan(self, analysis: AnalysisResult) -> BlueprintProposal:
        """Create a blueprint proposal from analysis."""
        self.log_start(job_id=analysis.job_id)
        
        try:
            # Deterministic content-to-blueprint algorithm
            proposal = self.proposer.propose(analysis)
            
            self.log_complete(job_id=analysis.job_id, groups=len(proposal.content_groups))
            return proposal
            
        except Exception as exc:
            self.log_failure(exc, job_id=analysis.job_id)
            raise
