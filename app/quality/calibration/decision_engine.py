"""
Universal Document Intelligence System V5 — Calibrated Decision Engine & Pairwise Comparator.

Phase 2C: Authoritative decision engine and pairwise good vs bad comparator.
Enforces:
- Semantic integrity override: High visual quality CANNOT override integrity violations.
- Scientific integrity override: Unsupported claims or broken citations block export.
- Pedagogical integrity override: Worksheet answer leaks block export.
- Strict ordering: GOOD > MODERATE > BAD with explainable margins.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict

from app.quality.calibration.failure_taxonomy import FailureCategory, FailureSeverity
from app.quality.calibration.quality_scoring import MasterQualityScoringEngine
from app.quality.contracts import (
    ArtifactFidelityReport,
    ArtifactQualityReport,
    CalibratedQualityDecision,
    QualityDecisionStatus,
    QualityFinding,
    QualitySeverity,
)


class PairwiseComparisonResult(BaseModel):
    """Result of comparing a good artifact vs an intentionally mutated bad artifact."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    good_score: float
    bad_score: float
    score_margin: float
    good_status: str
    bad_status: str
    is_valid_ordering: bool
    summary: str


class PairwiseQualityComparator:
    """Demonstrates that quality(good) > quality(bad) across all artifact types."""

    @classmethod
    def compare(
        cls,
        artifact_type: str,
        good_artifact: Any,
        bad_artifact: Any,
        min_margin: float = 0.15,
    ) -> PairwiseComparisonResult:
        good_report = MasterQualityScoringEngine.evaluate(artifact_type, good_artifact)
        bad_report = MasterQualityScoringEngine.evaluate(artifact_type, bad_artifact)

        margin = round(good_report.overall_quality_score - bad_report.overall_quality_score, 3)
        is_valid = margin >= min_margin and good_report.overall_quality_score > bad_report.overall_quality_score

        summary = (
            f"Comparison for {artifact_type}: Good score = {good_report.overall_quality_score:.3f} "
            f"({good_report.quality_level.value}), Bad score = {bad_report.overall_quality_score:.3f} "
            f"({bad_report.quality_level.value}). Margin: +{margin:.3f} (Required: >= {min_margin:.2f})."
        )

        return PairwiseComparisonResult(
            artifact_type=artifact_type,
            good_score=good_report.overall_quality_score,
            bad_score=bad_report.overall_quality_score,
            score_margin=margin,
            good_status=good_report.quality_level.value,
            bad_status=bad_report.quality_level.value,
            is_valid_ordering=is_valid,
            summary=summary,
        )


class CalibratedDecisionEngine:
    """Master arbiter evaluating both Fidelity and Quality into definitive export decisions."""

    @classmethod
    def arbitrate(
        cls,
        fidelity_report: ArtifactFidelityReport,
        quality_report: ArtifactQualityReport,
    ) -> CalibratedQualityDecision:
        return CalibratedQualityDecision.arbitrate(fidelity_report, quality_report)
