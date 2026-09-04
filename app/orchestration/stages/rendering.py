"""
Rendering Stage: Calls MasterRenderEngine.
"""

from __future__ import annotations

from pathlib import Path
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
from app.rendering.engine import MasterRenderEngine


class RenderingStage(ProductionStage):
    def __init__(
        self,
        engine: MasterRenderEngine | None = None,
        templates_dir: Path | str = "app/rendering/html/templates",
    ) -> None:
        self.templates_dir = Path(templates_dir)
        self.engine = engine

    @property
    def stage_id(self) -> str:
        return "rendering"

    @property
    def stage_type(self) -> WorkflowStageType:
        return WorkflowStageType.RENDERING

    def run(self, context: ProductionJobContext) -> StageExecutionResult:
        comp = context.shared_data.get("composition")
        if not comp:
            raise ValueError("No document composition found for rendering.")

        out_dir = Path("outputs/production_orchestration") / context.job_id
        out_dir.mkdir(parents=True, exist_ok=True)

        engine = self.engine or MasterRenderEngine(
            templates_dir=self.templates_dir,
            output_dir=out_dir,
        )

        res = engine.render(comp, output_filename=context.job_id)
        if not res.success:
            return StageExecutionResult(
                stage_id=self.stage_id,
                state=StageState.FAILED,
                failure=ProductionFailure(
                    stage_id=self.stage_id,
                    category=FailureCategory.RENDERING,
                    severity=FailureSeverity.RECOVERABLE,
                    message="; ".join(res.errors),
                    retryable=True,
                ),
            )

        context.shared_data["render_result"] = res
        context.shared_data["pdf_path"] = res.pdf_path
        if res.pdf_path:
            context.artifacts.append(res.pdf_path)

        return StageExecutionResult(
            stage_id=self.stage_id,
            state=StageState.SUCCEEDED,
            output={"pdf_path": res.pdf_path, "pages": res.pages},
            artifacts=[res.pdf_path] if res.pdf_path else [],
        )
