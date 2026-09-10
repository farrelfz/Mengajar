"""
Universal Document Intelligence System V5 — Root-Cause-Aware Targeted Repair & Convergence Engine.

Phase 3B: Complete self-correcting quality convergence architecture across all four artifact types:
1. PRESENTATION
2. HANDOUT
3. WORKSHEET
4. SCIENTIFIC_DOCUMENT
"""

from app.quality.repair.contracts import (
    ConvergenceState,
    RepairAction,
    RepairHistoryEntry,
    RepairMutationClass,
    RepairPlan,
    RepairRequest,
    RepairResult,
    RepairRiskLevel,
    RepairTarget,
)
from app.quality.repair.convergence import (
    ConvergenceController,
    OscillationDetectionResult,
    RepairOscillationDetector,
)
from app.quality.repair.provenance import (
    ProvenanceEdge,
    ProvenanceNode,
    RepairProvenanceGraph,
)
from app.quality.repair.regression_guard import (
    RegressionCheckResult,
    RegressionGuard,
)
from app.quality.repair.registry import (
    DEFAULT_STRATEGY_REGISTRY,
    RepairStrategyRegistry,
)
from app.quality.repair.repair_engine import TargetedRepairEngine
from app.quality.repair.rollback import ArtifactSnapshot, SnapshotManager
from app.quality.repair.root_cause import (
    DeterministicRootCauseAnalyzer,
    RootCauseHypothesis,
    RootCauseType,
)
from app.quality.repair.strategies.base import RepairStrategy
from app.quality.repair.design_resolver import DesignAwareRepairResolver

__all__ = [
    "RepairMutationClass",
    "RepairRiskLevel",
    "ConvergenceState",
    "RepairTarget",
    "RepairAction",
    "RepairPlan",
    "RepairResult",
    "RepairHistoryEntry",
    "RepairRequest",
    "RootCauseType",
    "RootCauseHypothesis",
    "DeterministicRootCauseAnalyzer",
    "RepairStrategyRegistry",
    "DEFAULT_STRATEGY_REGISTRY",
    "RepairStrategy",
    "SnapshotManager",
    "ArtifactSnapshot",
    "RegressionGuard",
    "RegressionCheckResult",
    "ConvergenceController",
    "RepairOscillationDetector",
    "OscillationDetectionResult",
    "TargetedRepairEngine",
    "RepairProvenanceGraph",
    "ProvenanceNode",
    "ProvenanceEdge",
    "DesignAwareRepairResolver",
]

