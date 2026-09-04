"""
Quality Evaluation Stage: Calls QualityEvaluationEngine.
"""

from __future__ import annotations

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
from app.quality import QualityEvaluationEngine


class QualityStage(ProductionStage):
    def __init__(self, engine: QualityEvaluationEngine | None = None) -> None:
        self.engine = engine or QualityEvaluationEngine()

    @property
    def stage_id(self) -> str:
        return "pre_render_quality"

    @property
    def stage_type(self) -> WorkflowStageType:
        return WorkflowStageType.PRE_RENDER_QUALITY

    def run(self, context: ProductionJobContext) -> StageExecutionResult:
        bp = context.shared_data.get("material_blueprint")
        comp = context.shared_data.get("composition")
        direction = context.shared_data.get("material_direction")

        if not bp or not comp:
            raise ValueError("Blueprint or composition missing for quality evaluation.")

        rep = self.engine.evaluate_artifact(
            job_id=context.job_id,
            material_bp=bp,
            composition=comp,
            journey=direction.journey if direction else None,
            pdf_path=None,
            target_format=context.request.metadata.target_format,
        )
        context.shared_data["quality_report"] = rep

        gate_res = ProductionGateResult(
            gate_type=ProductionGateType.STRUCTURAL_QUALITY_GATE,
            decision=GateDecisionEnum.PASS if rep.gate_result.can_proceed else GateDecisionEnum.REFINE,
            score=rep.overall_score,
            threshold=0.75,
            reasoning=rep.gate_result.gate_reasoning,
            findings=[f.finding for f in rep.findings],
            recommended_next_stage="rendering" if rep.gate_result.can_proceed else "critic_review",
        )
        context.gate_results.append(gate_res)

        return StageExecutionResult(
            stage_id=self.stage_id,
            state=StageState.SUCCEEDED,
            output={
                "overall_score": rep.overall_score,
                "can_proceed": rep.gate_result.can_proceed,
                "grade": rep.quality_level.value,
            },
        )
