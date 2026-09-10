"""
Universal Document Intelligence System V5 — Benchmark Overfitting & Generalization Analyzer.

Phase 5: Monitors for memorization and overfitting on known training/validation fixtures.
Detects when high performance on known benchmarks fails to transfer to unseen domain inputs.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class GeneralizationHealthStatus(str, Enum):
    """Generalization health status comparing known versus unseen corpus splits."""
    GENERALIZATION_STRONG = "GENERALIZATION_STRONG"          # Gap < 0.04, high unseen scores
    GENERALIZATION_ACCEPTABLE = "GENERALIZATION_ACCEPTABLE"  # Gap <= 0.08
    GENERALIZATION_WEAK = "GENERALIZATION_WEAK"              # Gap > 0.08, unseen degradation
    OVERFITTING_SUSPECTED = "OVERFITTING_SUSPECTED"          # Gap > 0.15, severe memorization signal


class OverfittingSignalReport(BaseModel):
    """Diagnostic report on generalization gap and model memorization risks."""
    model_config = ConfigDict(frozen=True)

    known_split_mean: float = Field(ge=0.0, le=1.0)
    unseen_split_mean: float = Field(ge=0.0, le=1.0)
    generalization_gap: float  # known - unseen
    status: GeneralizationHealthStatus
    overfitting_warning: bool
    diagnosis: str


class OverfittingSignalAnalyzer:
    """Analyzes score distributions between known training fixtures and unseen generalization fixtures."""

    @classmethod
    def analyze(
        cls,
        known_scores: List[float],
        unseen_scores: List[float],
    ) -> OverfittingSignalReport:
        """
        Computes generalization gap and determines if generator is overfitting to known benchmarks.
        """
        if not known_scores or not unseen_scores:
            return OverfittingSignalReport(
                known_split_mean=sum(known_scores) / len(known_scores) if known_scores else 0.0,
                unseen_split_mean=sum(unseen_scores) / len(unseen_scores) if unseen_scores else 0.0,
                generalization_gap=0.0,
                status=GeneralizationHealthStatus.GENERALIZATION_ACCEPTABLE,
                overfitting_warning=False,
                diagnosis="Insufficient data in one or both splits to evaluate generalization gap.",
            )

        known_mean = round(sum(known_scores) / len(known_scores), 4)
        unseen_mean = round(sum(unseen_scores) / len(unseen_scores), 4)
        gap = round(known_mean - unseen_mean, 4)

        if gap > 0.15:
            status = GeneralizationHealthStatus.OVERFITTING_SUSPECTED
            warning = True
            diag = (
                f"Severe generalization gap ({gap:.3f} > 0.150). Known mean ({known_mean:.3f}) vastly exceeds "
                f"unseen mean ({unseen_mean:.3f}). High risk of heuristic/prompt overfitting to known fixtures."
            )
        elif gap > 0.08:
            status = GeneralizationHealthStatus.GENERALIZATION_WEAK
            warning = True
            diag = (
                f"Noticeable generalization gap ({gap:.3f} > 0.080). Performance on novel domain fixtures "
                f"is lagging behind known reference fixtures."
            )
        elif gap < 0.04 and unseen_mean >= 0.85:
            status = GeneralizationHealthStatus.GENERALIZATION_STRONG
            warning = False
            diag = (
                f"Excellent generalization parity (gap={gap:.3f} < 0.040, unseen mean={unseen_mean:.3f}). "
                "The generator demonstrates consistent high fidelity across unseen domains."
            )
        else:
            status = GeneralizationHealthStatus.GENERALIZATION_ACCEPTABLE
            warning = False
            diag = f"Acceptable generalization gap ({gap:.3f} <= 0.080). Performance remains consistent."

        return OverfittingSignalReport(
            known_split_mean=known_mean,
            unseen_split_mean=unseen_mean,
            generalization_gap=gap,
            status=status,
            overfitting_warning=warning,
            diagnosis=diag,
        )
