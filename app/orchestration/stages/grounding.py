"""
Knowledge Grounding Stage: Calls KnowledgeGroundingEngine to verify claim evidence and provenance.
"""

from __future__ import annotations

from pathlib import Path
from app.grounding import KnowledgeGroundingEngine, LocalDocumentKnowledgeProvider
from app.orchestration.contracts import (
    ProductionJobContext,
    StageExecutionResult,
    StageState,
    WorkflowStageType,
)
from app.orchestration.stages.base import ProductionStage


class GroundingStage(ProductionStage):
    def __init__(self, engine: KnowledgeGroundingEngine | None = None) -> None:
        if engine:
            self.engine = engine
        else:
            providers = []
            phys_fixture = Path("tests/fixtures/grounding/physics_sources.md")
            if phys_fixture.exists():
                p = LocalDocumentKnowledgeProvider("local_phys")
                p.load_markdown_file(phys_fixture, domain="physics")
                providers.append(p)

            res_fixture = Path("tests/fixtures/grounding/research_sources.md")
            if res_fixture.exists():
                r = LocalDocumentKnowledgeProvider("local_research")
                r.load_markdown_file(res_fixture, domain="research_methodology")
                providers.append(r)

            self.engine = KnowledgeGroundingEngine(providers=providers)

    @property
    def stage_id(self) -> str:
        return "grounding"

    @property
    def stage_type(self) -> WorkflowStageType:
        return WorkflowStageType.GROUNDING

    def run(self, context: ProductionJobContext) -> StageExecutionResult:
        mat = context.shared_data.get("material_blueprint", context.request.raw_input)
        domain = context.request.metadata.domain

        grounded_context = self.engine.ground_material(mat, domain=domain)
        rep = grounded_context.report
        context.shared_data["grounding_report"] = rep
        context.shared_data["grounded_context"] = grounded_context

        return StageExecutionResult(
            stage_id=self.stage_id,
            state=StageState.SUCCEEDED,
            output={
                "overall_score": rep.score.overall_score,
                "claims_total": rep.claims_total,
                "claims_grounded": rep.claims_grounded,
                "claims_unsupported": rep.claims_unsupported,
                "claims_contradicted": rep.claims_contradicted,
            },
        )
