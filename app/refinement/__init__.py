"""
Iterative Refinement Package Exports.
"""

from app.refinement.contracts import (
    ImprovementComparison,
    ImprovementDecision,
    InvariantCategory,
    InvariantViolation,
    RefinedArtifactBundle,
    RefinementAction,
    RefinementCandidate,
    RefinementIntent,
    RefinementPatch,
    RefinementPlan,
    RefinementRisk,
    RefinementScope,
    RefinementStage,
    RefinementTargetLayer,
    RefinementTrace,
)
from app.refinement.controller import IterativeRefinementController
from app.refinement.convergence import ConvergenceDetector
from app.refinement.decision import ImprovementJudge
from app.refinement.evaluator import ImprovementComparator, RefinementEvaluator
from app.refinement.executor import RefinementExecutor
from app.refinement.history import RefinementHistory
from app.refinement.invariants import InvariantChecker
from app.refinement.ownership import RefinementOwnershipResolver
from app.refinement.patches import (
    BaseRefinementPatch,
    CapabilityReplacementPatch,
    DensitySplitPatch,
    PedagogicalSequencePatch,
    RedundancyDeduplicationPatch,
)
from app.refinement.planner import RefinementPlanner
from app.refinement.strategies import (
    BaseRefinementStrategy,
    CapabilityRefinementStrategy,
    DensityRefinementStrategy,
    PedagogicalRefinementStrategy,
    RedundancyRefinementStrategy,
)

__all__ = [
    "RefinementStage",
    "RefinementTargetLayer",
    "RefinementScope",
    "RefinementIntent",
    "RefinementRisk",
    "ImprovementDecision",
    "InvariantCategory",
    "InvariantViolation",
    "RefinementAction",
    "RefinementPlan",
    "RefinementPatch",
    "RefinedArtifactBundle",
    "RefinementCandidate",
    "ImprovementComparison",
    "RefinementTrace",
    "RefinementOwnershipResolver",
    "InvariantChecker",
    "BaseRefinementPatch",
    "PedagogicalSequencePatch",
    "DensitySplitPatch",
    "CapabilityReplacementPatch",
    "RedundancyDeduplicationPatch",
    "BaseRefinementStrategy",
    "PedagogicalRefinementStrategy",
    "DensityRefinementStrategy",
    "CapabilityRefinementStrategy",
    "RedundancyRefinementStrategy",
    "RefinementPlanner",
    "RefinementExecutor",
    "RefinementEvaluator",
    "ImprovementComparator",
    "ImprovementJudge",
    "ConvergenceDetector",
    "RefinementHistory",
    "IterativeRefinementController",
]
