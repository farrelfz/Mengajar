"""
Composition Stage: Calls CompositionBridge to resolve capabilities and generate page compositions.
"""

from __future__ import annotations

from pathlib import Path
from app.capabilities.registry import CapabilityRegistry
from app.composition.bridge import CompositionBridge
from app.libraries import register_all_default_capabilities
from app.orchestration.contracts import (
    ProductionJobContext,
    StageExecutionResult,
    StageState,
    WorkflowStageType,
)
from app.orchestration.stages.base import ProductionStage


class CompositionStage(ProductionStage):
    def __init__(self, bridge: CompositionBridge | None = None) -> None:
        reg = CapabilityRegistry.get_instance()
        register_all_default_capabilities(reg)
        self.bridge = bridge or CompositionBridge(registry=reg)

    @property
    def stage_id(self) -> str:
        return "composition"

    @property
    def stage_type(self) -> WorkflowStageType:
        return WorkflowStageType.COMPOSITION

    def run(self, context: ProductionJobContext) -> StageExecutionResult:
        bp = context.shared_data.get("material_blueprint")
        if not bp:
            raise ValueError("No material blueprint found in context for composition.")

        out_dir = Path("outputs/production_orchestration") / context.job_id
        out_dir.mkdir(parents=True, exist_ok=True)

        comp, assets = self.bridge.compose_material(
            material=bp,
            output_dir=out_dir,
            target_format=context.request.metadata.target_format,
        )
        context.shared_data["composition"] = comp
        context.shared_data["assets"] = assets

        return StageExecutionResult(
            stage_id=self.stage_id,
            state=StageState.SUCCEEDED,
            output={"pages_count": len(comp.pages), "regions_count": sum(len(p.regions) for p in comp.pages)},
            artifacts=["document_composition"],
        )
