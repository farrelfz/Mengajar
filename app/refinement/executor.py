"""
Refinement Executor: Applies planned patches to generate candidate artifact bundles.
"""

from __future__ import annotations

from typing import Any
from app.refinement.contracts import (
    RefinedArtifactBundle,
    RefinementAction,
    RefinementCandidate,
    RefinementPatch,
    RefinementPlan,
)
from app.refinement.strategies import (
    BaseRefinementStrategy,
    CapabilityRefinementStrategy,
    DensityRefinementStrategy,
    PedagogicalRefinementStrategy,
    RedundancyRefinementStrategy,
)


class RefinementExecutor:
    """Executes refinement plans immutably via strategy dispatch."""

    def __init__(self, strategies: list[BaseRefinementStrategy] | None = None) -> None:
        self.strategies = strategies or [
            PedagogicalRefinementStrategy(),
            DensityRefinementStrategy(),
            CapabilityRefinementStrategy(),
            RedundancyRefinementStrategy(),
        ]

    def execute_plan(
        self,
        baseline: RefinedArtifactBundle,
        plan: RefinementPlan,
    ) -> RefinementCandidate:
        current_bundle = baseline
        applied_patches: list[RefinementPatch] = []

        for action in plan.actions:
            # Find matching strategy
            matched_strategy = next((s for s in self.strategies if s.can_handle(action)), None)
            if matched_strategy is not None:
                patch_op = matched_strategy.create_patch(action)
                current_bundle, patch_meta = patch_op.apply(current_bundle)
                applied_patches.append(patch_meta)

        candidate_id = f"{baseline.artifact_id}_cand_iter{plan.iteration}"
        current_bundle.artifact_id = candidate_id

        return RefinementCandidate(
            candidate_id=candidate_id,
            parent_artifact_id=baseline.artifact_id,
            iteration=plan.iteration,
            patches=applied_patches,
            artifact_bundle=current_bundle,
            metadata={"patches_count": len(applied_patches)},
        )
