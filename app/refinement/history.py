"""
Refinement History & Memory: Maintains an immutable, multi-iteration audit trail of the refinement lifecycle.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from app.refinement.contracts import (
    ImprovementComparison,
    ImprovementDecision,
    RefinementCandidate,
    RefinementPlan,
    RefinementTrace,
)


class RefinementHistory(BaseModel):
    """Complete audit record across all refinement iterations."""

    artifact_id: str
    baseline_score: float = 0.0
    final_score: float = 0.0
    total_iterations: int = 0
    final_decision: ImprovementDecision = ImprovementDecision.ACCEPT
    stop_reason: str = ""
    plans: list[RefinementPlan] = Field(default_factory=list)
    candidates: list[RefinementCandidate] = Field(default_factory=list)
    comparisons: list[ImprovementComparison] = Field(default_factory=list)
    fingerprints: list[str] = Field(default_factory=list)
    traces: list[RefinementTrace] = Field(default_factory=list)

    def record_iteration(
        self,
        plan: RefinementPlan,
        candidate: RefinementCandidate,
        comparison: ImprovementComparison,
        fingerprint: str,
        trace: RefinementTrace,
    ) -> None:
        self.plans.append(plan)
        self.candidates.append(candidate)
        self.comparisons.append(comparison)
        self.fingerprints.append(fingerprint)
        self.traces.append(trace)
        self.total_iterations += 1
        self.final_score = candidate.quality_report.overall_score if candidate.quality_report else 0.0
