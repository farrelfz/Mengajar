"""
Improvement Judge & Acceptance Policy: Arbitrates whether candidate artifacts are accepted, rejected, retried, or stopped.
"""

from __future__ import annotations

from app.refinement.contracts import ImprovementComparison, ImprovementDecision


class ImprovementJudge:
    """Judges candidate improvement strictly guarding against false improvements and invariant regressions."""

    @classmethod
    def judge(
        cls,
        comparison: ImprovementComparison,
    ) -> ImprovementDecision:
        # Rule 1: Any Invariant Violation MUST be REJECTED immediately
        if comparison.invariant_violations:
            return ImprovementDecision.REJECT

        # Rule 2: If new regressions appeared, REJECT or RETRY
        if comparison.new_regressions:
            return ImprovementDecision.REJECT

        # Rule 3: If meaningful improvement with no regressions
        if comparison.is_meaningful_improvement:
            return ImprovementDecision.ACCEPT

        # Rule 4: If quality score delta is negligible (< 0.005) and zero findings resolved
        if comparison.quality_delta <= 0.005 and len(comparison.resolved_finding_ids) == 0:
            return ImprovementDecision.STOP_NO_IMPROVEMENT

        return ImprovementDecision.ACCEPT
