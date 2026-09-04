"""
Artifact Validation & QA Stage.
"""

from __future__ import annotations

from pathlib import Path
from app.orchestration.contracts import (
    GateDecisionEnum,
    ProductionGateResult,
    ProductionGateType,
    ProductionJobContext,
    StageExecutionResult,
    StageState,
    WorkflowStageType,
)
from app.orchestration.stages.base import ProductionStage


class ArtifactValidationStage(ProductionStage):
    @property
    def stage_id(self) -> str:
        return "artifact_validation"

    @property
    def stage_type(self) -> WorkflowStageType:
        return WorkflowStageType.ARTIFACT_VALIDATION

    def run(self, context: ProductionJobContext) -> StageExecutionResult:
        pdf_path = context.shared_data.get("pdf_path")
        valid = False
        if pdf_path and Path(pdf_path).exists() and Path(pdf_path).stat().st_size > 0:
            valid = True

        gate_res = ProductionGateResult(
            gate_type=ProductionGateType.ARTIFACT_GEOMETRY_GATE,
            decision=GateDecisionEnum.PASS if valid else GateDecisionEnum.FAIL,
            score=1.0 if valid else 0.0,
            threshold=1.0,
            reasoning="Valid non-empty PDF artifact generated" if valid else "PDF artifact missing or empty",
            recommended_next_stage="finalization" if valid else None,
        )
        context.gate_results.append(gate_res)

        return StageExecutionResult(
            stage_id=self.stage_id,
            state=StageState.SUCCEEDED if valid else StageState.FAILED,
            output={"valid": valid, "pdf_path": pdf_path},
        )
