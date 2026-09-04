"""
Critic Stage: Calls GenerativeCriticEngine to diagnose defects and explain improvements.
"""

from __future__ import annotations

from app.critic.engine import GenerativeCriticEngine
from app.orchestration.contracts import (
    ProductionJobContext,
    StageExecutionResult,
    StageState,
    WorkflowStageType,
)
from app.orchestration.stages.base import ProductionStage


class CriticStage(ProductionStage):
    def __init__(self, engine: GenerativeCriticEngine | None = None) -> None:
        self.engine = engine or GenerativeCriticEngine()

    @property
    def stage_id(self) -> str:
        return "critic_review"

    @property
    def stage_type(self) -> WorkflowStageType:
        return WorkflowStageType.CRITIC_REVIEW

    def run(self, context: ProductionJobContext) -> StageExecutionResult:
        bp = context.shared_data.get("material_blueprint")
        comp = context.shared_data.get("composition")
        direction = context.shared_data.get("material_direction")
        q_rep = context.shared_data.get("quality_report")

        rep = self.engine.critique(
            blueprint=bp,
            composition=comp,
            journey=direction.journey if direction else None,
            quality_report=q_rep,
            target_format=context.request.metadata.target_format,
        )
        context.shared_data["critic_report"] = rep

        return StageExecutionResult(
            stage_id=self.stage_id,
            state=StageState.SUCCEEDED,
            output={"critiques_count": len(rep.critiques), "overall_score": rep.critic_score.overall_score},
        )
