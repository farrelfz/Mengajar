"""
Personalization Stage: Calls PersonalizationEngine to adapt blueprint to learner profile.
"""

from __future__ import annotations

from app.orchestration.contracts import (
    ProductionJobContext,
    StageExecutionResult,
    StageState,
    WorkflowStageType,
)
from app.orchestration.stages.base import ProductionStage
from app.personalization import (
    AdaptationPolicyType,
    LearnerProfile,
    PersonalizationEngine,
)


class PersonalizationStage(ProductionStage):
    def __init__(self, engine: PersonalizationEngine | None = None) -> None:
        self.engine = engine or PersonalizationEngine()

    @property
    def stage_id(self) -> str:
        return "personalization"

    @property
    def stage_type(self) -> WorkflowStageType:
        return WorkflowStageType.PERSONALIZATION

    def should_execute(self, context: ProductionJobContext) -> bool:
        return "learner_profile" in context.shared_data

    def run(self, context: ProductionJobContext) -> StageExecutionResult:
        profile: LearnerProfile = context.shared_data["learner_profile"]
        bp = context.shared_data.get("material_blueprint")
        policy = context.shared_data.get("adaptation_policy", AdaptationPolicyType.BALANCED)

        if not bp:
            return StageExecutionResult(stage_id=self.stage_id, state=StageState.SKIPPED)

        rep = self.engine.personalize(
            blueprint=bp,
            learner_profile=profile,
            policy=policy,
            target_format=context.request.metadata.target_format,
        )
        context.shared_data["personalization_report"] = rep
        return StageExecutionResult(
            stage_id=self.stage_id,
            state=StageState.SUCCEEDED,
            output={"decisions_count": len(rep.adaptation_plan.decisions)},
        )
