"""
Universal Document Intelligence System V5 — Quality Calibration Package.

Phase 2C: Comprehensive calibration engine, scoring evaluators, explainability models,
degeneracy detection, and pairwise comparison framework.
"""

from __future__ import annotations

from app.quality.calibration.failure_taxonomy import (
    FailureCategory,
    FailureSeverity,
    QualityFailure,
)
from app.quality.calibration.quality_dimensions import (
    BaseQualityDimension,
    HandoutDimension,
    PresentationDimension,
    ScientificDocumentDimension,
    WorksheetDimension,
)
from app.quality.calibration.score_explanation import DimensionalScoreExplanation
from app.quality.calibration.calibration_engine import (
    CALIBRATION_PROFILES,
    QualityCalibrationProfile,
    QualityDetectionMetrics,
)
from app.quality.calibration.degeneracy_detector import (
    DegeneracyFinding,
    QualityScoreDegeneracyDetector,
)
from app.quality.calibration.quality_scoring import (
    HandoutQualityEvaluator,
    MasterQualityScoringEngine,
    PresentationQualityEvaluator,
    ScientificDocumentQualityEvaluator,
    WorksheetQualityEvaluator,
)
from app.quality.calibration.decision_engine import (
    CalibratedDecisionEngine,
    PairwiseComparisonResult,
    PairwiseQualityComparator,
)
from app.quality.calibration.benchmark_matrix import (
    BenchmarkArtifactEntry,
    BenchmarkQualityMatrix,
)

__all__ = [
    "FailureCategory",
    "FailureSeverity",
    "QualityFailure",
    "BaseQualityDimension",
    "PresentationDimension",
    "HandoutDimension",
    "WorksheetDimension",
    "ScientificDocumentDimension",
    "DimensionalScoreExplanation",
    "CALIBRATION_PROFILES",
    "QualityCalibrationProfile",
    "QualityDetectionMetrics",
    "DegeneracyFinding",
    "QualityScoreDegeneracyDetector",
    "PresentationQualityEvaluator",
    "HandoutQualityEvaluator",
    "WorksheetQualityEvaluator",
    "ScientificDocumentQualityEvaluator",
    "MasterQualityScoringEngine",
    "CalibratedDecisionEngine",
    "PairwiseComparisonResult",
    "PairwiseQualityComparator",
    "BenchmarkArtifactEntry",
    "BenchmarkQualityMatrix",
]
