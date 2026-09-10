"""
Universal Document Intelligence System V5 — Quality & Fidelity Contracts Package.

Exports both legacy quality contracts and Phase 2C calibrated contracts:
- Legacy: QualityDimension, QualitySeverity, QualityLevel, QualityFinding, QualityMetric, etc.
- Phase 2C Fidelity: ArtifactFidelityReport
- Phase 2C Quality: ArtifactQualityReport, QualitySignalExplanation
- Phase 2C Decision: QualityDecisionStatus, CalibratedQualityDecision
"""

from __future__ import annotations

from app.quality.contracts.legacy_contracts import (
    EvaluationStage,
    EvaluationTrace,
    QualityDimension,
    QualityFinding,
    QualityGateDecision,
    QualityGateResult,
    QualityLevel,
    QualityMetric,
    QualityReport,
    QualityScore,
    QualitySeverity,
)
from app.quality.contracts.fidelity_contract import (
    ArtifactFidelityReport,
)
from app.quality.contracts.quality_contract import (
    ArtifactQualityReport,
    QualitySignalExplanation,
)
from app.quality.contracts.decision_contract import (
    CalibratedQualityDecision,
    QualityDecisionStatus,
)
from app.quality.contracts.signals import (
    QualityDomain,
    QualityLocation,
    QualitySignal,
    SignalConfidence,
    SignalSeverity,
)
from app.quality.contracts.findings import (
    FindingCluster,
    QualityFinding as CanonicalQualityFinding,
)
from app.quality.contracts.dimensions import (
    CanonicalQualityDimension,
    QualityDimensionScore,
)
from app.quality.contracts.decisions import (
    ExportDecision,
    UnifiedQualityDecision,
)
from app.quality.contracts.provenance import (
    EvidenceReference,
    EvidenceSourceType,
    QualityProvenanceGraph,
)
from app.quality.contracts.authority import (
    UnifiedQualityReport,
)

__all__ = [
    # Legacy
    "QualityDimension",
    "QualitySeverity",
    "QualityLevel",
    "EvaluationStage",
    "QualityGateDecision",
    "QualityFinding",
    "QualityMetric",
    "QualityScore",
    "EvaluationTrace",
    "QualityGateResult",
    "QualityReport",
    # Phase 2C Fidelity
    "ArtifactFidelityReport",
    # Phase 2C Quality
    "ArtifactQualityReport",
    "QualitySignalExplanation",
    # Phase 2C Decision
    "QualityDecisionStatus",
    "CalibratedQualityDecision",
    # Phase 3A.1 Canonical Contracts
    "QualityDomain",
    "SignalSeverity",
    "SignalConfidence",
    "QualityLocation",
    "QualitySignal",
    "CanonicalQualityFinding",
    "FindingCluster",
    "CanonicalQualityDimension",
    "QualityDimensionScore",
    "ExportDecision",
    "UnifiedQualityDecision",
    "EvidenceSourceType",
    "EvidenceReference",
    "QualityProvenanceGraph",
    "UnifiedQualityReport",
]
