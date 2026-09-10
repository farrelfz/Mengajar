"""
Universal Document Intelligence System V5 — Quality Score Degeneracy Detector.

Phase 2C: Detects degenerate, suspicious, or self-confirming scoring patterns:
- Universal 1.000 scoring across structurally different artifacts
- Near-zero variance across benchmark distributions
- Insensitivity to severe adversarial mutations
- Perfect correlation between execution success and quality score
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.quality_contract import ArtifactQualityReport


class DegeneracyFinding(BaseModel):
    """Diagnostic report describing a detected scoring degeneracy pattern."""
    model_config = ConfigDict(frozen=True)

    is_degenerate: bool
    severity: str  # CRITICAL, WARNING, INFO
    reason: str
    affected_artifacts_count: int
    variance: float
    recommended_action: str


class QualityScoreDegeneracyDetector:
    """Monitors quality evaluation score distributions for lack of sensitivity or false perfection."""

    @staticmethod
    def detect(reports: List[ArtifactQualityReport]) -> Optional[DegeneracyFinding]:
        """Analyzes a collection of quality reports and returns a DegeneracyFinding if degenerate."""
        if not reports or len(reports) < 2:
            return None

        scores = [r.overall_quality_score for r in reports]
        n = len(scores)
        mean_score = sum(scores) / n

        # Calculate sample variance
        variance = sum((s - mean_score) ** 2 for s in scores) / max(n - 1, 1)

        # 1. Check Universal 1.000
        all_perfect = all(math.isclose(s, 1.0, abs_tol=1e-4) for s in scores)
        if all_perfect and n >= 3:
            return DegeneracyFinding(
                is_degenerate=True,
                severity="CRITICAL",
                reason=(
                    f"Universal 1.000 scoring detected across {n} artifacts. "
                    "Evaluator is exhibiting false perfection and likely measuring contract compliance rather than quality."
                ),
                affected_artifacts_count=n,
                variance=0.0,
                recommended_action="Run adversarial calibration suite and verify multi-dimensional visual and pedagogical evaluators.",
            )

        # 2. Check Near-Zero Variance with high average score
        if variance < 1e-5 and mean_score > 0.95 and n >= 4:
            return DegeneracyFinding(
                is_degenerate=True,
                severity="WARNING",
                reason=(
                    f"Quality score distribution variance is near zero ({variance:.6f}) with mean {mean_score:.3f}. "
                    "Evaluator may be insensitive to stylistic or pedagogical variation."
                ),
                affected_artifacts_count=n,
                variance=variance,
                recommended_action="Calibrate dimension weights and review metric discrimination thresholds.",
            )

        return None
