"""
Request Validation Stage.
"""

from __future__ import annotations

from app.orchestration.contracts import (
    FailureCategory,
    FailureSeverity,
    ProductionFailure,
    ProductionJobContext,
    StageExecutionResult,
    StageState,
    WorkflowStageType,
)
from app.orchestration.stages.base import ProductionStage


class RequestValidationStage(ProductionStage):
    @property
    def stage_id(self) -> str:
        return "request_validation"

    @property
    def stage_type(self) -> WorkflowStageType:
        return WorkflowStageType.VALIDATION

    def validate_input(self, context: ProductionJobContext) -> list[str]:
        errors = []
        if not context.request.raw_input.strip():
            errors.append("Empty raw_input provided in request.")
        return errors

    def run(self, context: ProductionJobContext) -> StageExecutionResult:
        context.shared_data["validated_input"] = context.request.raw_input
        return StageExecutionResult(
            stage_id=self.stage_id,
            state=StageState.SUCCEEDED,
            output={"validated": True},
        )
