"""
Universal Document Intelligence System V5 — Review Priority Model.

Phase 6: Deterministic multi-factor scoring prioritizing cases requiring
urgent human intervention without opaque or arbitrary weights.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Any, Dict, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.review.contracts.enums import ReviewTrigger


class PriorityBand(str, Enum):
    P0_CRITICAL = "P0_CRITICAL"
    P1_HIGH = "P1_HIGH"
    P2_NORMAL = "P2_NORMAL"
    P3_BACKGROUND = "P3_BACKGROUND"


class PriorityScoreBreakdown(BaseModel):
    """Inspectable mathematical breakdown of a review case priority score."""
    model_config = ConfigDict(frozen=True)

    overall_score: float
    band: PriorityBand
    severity_component: float
    impact_component: float
    staleness_component: float
    governance_component: float
    convergence_component: float
    explanation: str


class ReviewPriorityModel:
    """Calculates deterministic priority scores for ReviewCases."""

    # Weights summing to 1.0
    W_SEVERITY = 0.35
    W_IMPACT = 0.20
    W_STALENESS = 0.15
    W_GOVERNANCE = 0.15
    W_CONVERGENCE = 0.15

    @classmethod
    def calculate(
        cls,
        trigger: ReviewTrigger,
        hard_blocker_count: int = 0,
        critical_finding_count: int = 0,
        is_certification_benchmark: bool = False,
        age_seconds: float = 0.0,
        convergence_failure: bool = False,
    ) -> PriorityScoreBreakdown:
        """Computes inspectable priority score between 0.0 and 1.0."""
        # 1. Severity
        if hard_blocker_count > 0:
            s_sev = 1.0
        elif critical_finding_count > 0:
            s_sev = 0.75
        else:
            s_sev = 0.30

        # 2. Impact
        s_imp = 1.0 if is_certification_benchmark else 0.50

        # 3. Staleness (saturates at 24 hours / 86400s)
        s_stale = min(1.0, max(0.0, age_seconds / 86400.0))

        # 4. Governance
        if trigger in (ReviewTrigger.BENCHMARK_REGRESSION, ReviewTrigger.REPAIR_INVARIANT_FAILURE):
            s_gov = 1.0
        elif trigger in (ReviewTrigger.QUALITY_MANUAL_REVIEW, ReviewTrigger.CONVERGENCE_FAILURE):
            s_gov = 0.90 if hard_blocker_count > 0 else 0.70
        elif trigger == ReviewTrigger.BENCHMARK_INSUFFICIENT:
            s_gov = 0.60
        else:
            s_gov = 0.20

        # 5. Convergence
        s_conv = 1.0 if (convergence_failure or trigger == ReviewTrigger.CONVERGENCE_FAILURE) else 0.10

        overall = (
            cls.W_SEVERITY * s_sev
            + cls.W_IMPACT * s_imp
            + cls.W_STALENESS * s_stale
            + cls.W_GOVERNANCE * s_gov
            + cls.W_CONVERGENCE * s_conv
        )
        overall = round(min(1.0, max(0.0, overall)), 3)

        if overall >= 0.75:
            band = PriorityBand.P0_CRITICAL
        elif overall >= 0.60:
            band = PriorityBand.P1_HIGH
        elif overall >= 0.35:
            band = PriorityBand.P2_NORMAL
        else:
            band = PriorityBand.P3_BACKGROUND

        explanation = (
            f"Score {overall:.3f} [{band.value}]: sev={s_sev:.2f}, imp={s_imp:.2f}, "
            f"stale={s_stale:.2f}, gov={s_gov:.2f}, conv={s_conv:.2f}"
        )

        return PriorityScoreBreakdown(
            overall_score=overall,
            band=band,
            severity_component=s_sev,
            impact_component=s_imp,
            staleness_component=s_stale,
            governance_component=s_gov,
            convergence_component=s_conv,
            explanation=explanation,
        )
