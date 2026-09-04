"""
Director Stage: Calls IntelligentMaterialDirector to plan educational choreography.
"""

from __future__ import annotations

from app.director import (
    AudienceProfile,
    InstructionalIntent,
    IntelligentMaterialDirector,
    KnowledgeState,
    LearningGoal,
)
from app.orchestration.contracts import (
    ProductionJobContext,
    StageExecutionResult,
    StageState,
    WorkflowStageType,
)
from app.orchestration.stages.base import ProductionStage


class DirectorStage(ProductionStage):
    def __init__(self, director: IntelligentMaterialDirector | None = None) -> None:
        self.director = director or IntelligentMaterialDirector()

    @property
    def stage_id(self) -> str:
        return "directing"

    @property
    def stage_type(self) -> WorkflowStageType:
        return WorkflowStageType.DIRECTING

    def run(self, context: ProductionJobContext) -> StageExecutionResult:
        meta = context.request.metadata
        concept_title = context.request.source_hint.replace("_", " ").title()
        goal = LearningGoal(
            concept=concept_title,
            expected_understanding=f"Core understanding of {concept_title}",
            domain=meta.domain,
        )
        aud = AudienceProfile(
            education_level=meta.audience_level,
            prior_knowledge=KnowledgeState.NOVICE,
        )
        direction = self.director.direct(
            goal=goal,
            audience=aud,
            intent=InstructionalIntent.TEACH,
            format_id=meta.target_format,
        )
        context.shared_data["material_direction"] = direction
        return StageExecutionResult(
            stage_id=self.stage_id,
            state=StageState.SUCCEEDED,
            output={"strategy": direction.strategy.value, "stages": len(direction.journey.stages)},
        )
