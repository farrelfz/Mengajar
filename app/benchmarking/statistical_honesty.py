"""
Universal Document Intelligence System V5 — Benchmark Statistical Honesty Engine.

Phase 5: Prevents false scientific confidence when evaluating benchmarks with limited sample sizes.
Differentiates between preliminary signals, high-variance runs, and conclusive statistical improvements.
"""

from __future__ import annotations

import math
import statistics
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class StatisticalConfidenceLevel(str, Enum):
    """Honest calibration of benchmark evidentiary certainty."""
    CONSISTENT_IMPROVEMENT = "CONSISTENT_IMPROVEMENT"      # Robust sample size, low variance, positive delta
    OBSERVED_IMPROVEMENT = "OBSERVED_IMPROVEMENT"          # Moderate sample size, positive delta
    PRELIMINARY_SIGNAL = "PRELIMINARY_SIGNAL"              # Limited sample size (n < 5)
    INSUFFICIENT_SAMPLE_SIZE = "INSUFFICIENT_SAMPLE_SIZE"  # Very small sample (n < 3)
    HIGH_VARIANCE = "HIGH_VARIANCE"                        # Noisy score distribution (variance > threshold)


class SampleAdequacyReport(BaseModel):
    """Rigorous qualification of benchmark statistical validity and epistemic limits."""
    model_config = ConfigDict(frozen=True)

    total_observations: int
    mean_score: float = Field(ge=0.0, le=1.0)
    variance: float = Field(ge=0.0)
    confidence_level: StatisticalConfidenceLevel
    is_statistically_conclusive: bool
    confidence_limitation_statement: str
    recommended_sample_size: int = 15


class StatisticalHonestyEngine:
    """Evaluates empirical score distributions with strict epistemic modesty."""

    MIN_CONCLUSIVE_SAMPLES: int = 10
    HIGH_VARIANCE_THRESHOLD: float = 0.04

    @classmethod
    def evaluate(
        cls,
        scores: List[float],
        baseline_mean: Optional[float] = None,
    ) -> SampleAdequacyReport:
        """
        Evaluates a set of benchmark observation scores and assigns an honest confidence level.
        """
        n = len(scores)
        if n == 0:
            return SampleAdequacyReport(
                total_observations=0,
                mean_score=0.0,
                variance=0.0,
                confidence_level=StatisticalConfidenceLevel.INSUFFICIENT_SAMPLE_SIZE,
                is_statistically_conclusive=False,
                confidence_limitation_statement="Zero observations available; benchmark cannot be evaluated.",
            )

        mean_val = round(sum(scores) / n, 4)
        var_val = round(statistics.variance(scores) if n > 1 else 0.0, 5)

        if n < 3:
            conf = StatisticalConfidenceLevel.INSUFFICIENT_SAMPLE_SIZE
            conclusive = False
            msg = f"Sample size (n={n}) is too small for statistical validity. Results are purely anecdotal."
        elif n < 8:
            if var_val > cls.HIGH_VARIANCE_THRESHOLD:
                conf = StatisticalConfidenceLevel.HIGH_VARIANCE
                conclusive = False
                msg = f"Small sample (n={n}) exhibits high score variance ({var_val:.4f}). Signals are volatile."
            else:
                conf = StatisticalConfidenceLevel.PRELIMINARY_SIGNAL
                conclusive = False
                msg = f"Sample size (n={n}) provides preliminary directional signal only. Not statistically conclusive."
        else:
            if var_val > cls.HIGH_VARIANCE_THRESHOLD:
                conf = StatisticalConfidenceLevel.HIGH_VARIANCE
                conclusive = False
                msg = f"Observations (n={n}) show high variance ({var_val:.4f}). Consistent improvement cannot be claimed."
            elif baseline_mean is not None and mean_val > baseline_mean:
                conf = (
                    StatisticalConfidenceLevel.CONSISTENT_IMPROVEMENT
                    if n >= cls.MIN_CONCLUSIVE_SAMPLES
                    else StatisticalConfidenceLevel.OBSERVED_IMPROVEMENT
                )
                conclusive = (n >= cls.MIN_CONCLUSIVE_SAMPLES)
                msg = (
                    f"Statistically robust improvement observed (n={n}, mean={mean_val:.3f} > baseline={baseline_mean:.3f})."
                    if conclusive
                    else f"Observed improvement over baseline (n={n}), pending further expansion to n>={cls.MIN_CONCLUSIVE_SAMPLES}."
                )
            else:
                conf = StatisticalConfidenceLevel.OBSERVED_IMPROVEMENT
                conclusive = (n >= cls.MIN_CONCLUSIVE_SAMPLES)
                msg = f"Sample size (n={n}) is adequate. Scores stable around {mean_val:.3f}."

        return SampleAdequacyReport(
            total_observations=n,
            mean_score=mean_val,
            variance=var_val,
            confidence_level=conf,
            is_statistically_conclusive=conclusive,
            confidence_limitation_statement=msg,
        )
