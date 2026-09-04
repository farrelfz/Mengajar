"""
Refinement Stage: Calls IterativeRefinementController.
"""

from __future__ import annotations

from app.orchestration.contracts import (
    ProductionJobContext,
    StageExecutionResult,
    StageState,
    WorkflowStageType,
)
from app.orchestration.stages.base import ProductionStage
from app.refinement.controller import IterativeRefinementController


class RefinementStage(ProductionStage):
    def __init__(self, controller: IterativeRefinementController | None = None) -> None:
        self.controller = controller or IterativeRefinementController()

    @property
    def stage_id(self) -> str:
        return "refinement"

    @property
    def stage_type(self) -> WorkflowStageType:
        return WorkflowStageType.REFINEMENT

    def run(self, context: ProductionJobContext) -> StageExecutionResult:
        bp = context.shared_data.get("material_blueprint")
        comp = context.shared_data.get("composition")
        direction = context.shared_data.get("material_direction")

        bundle, history = self.controller.refine(
            blueprint=bp,
            composition=comp,
            journey=direction.journey if direction else None,
            target_format=context.request.metadata.target_format,
            max_iterations=1,
            artifact_id=context.job_id,
        )
        context.shared_data["material_blueprint"] = bundle.blueprint
        context.shared_data["composition"] = bundle.composition
        context.shared_data["refinement_history"] = history
        context.refinement_iterations += 1

        return StageExecutionResult(
            stage_id=self.stage_id,
            state=StageState.SUCCEEDED,
            output={"iterations": len(history.records), "final_status": history.final_status.value},
        )
