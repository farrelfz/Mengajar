"""
Universal Document Intelligence System V5 — Review Confidence Evaluator.

Phase 6: Verifies epistemic calibration of reviewer self-reported confidence.
HIGH reviewer confidence ≠ automatic system truth.
"""

from __future__ import annotations

from typing import Tuple
from app.review.contracts.enums import EvidenceSufficiencyLevel, ReviewConfidence


class ConfidenceEvaluator:
    """Audits reported confidence against empirical evidence sufficiency."""

    @classmethod
    def audit_confidence(
        cls,
        confidence: ReviewConfidence,
        sufficiency: EvidenceSufficiencyLevel,
    ) -> Tuple[bool, str]:
        """
        Validates that reported confidence is justified by evidence sufficiency.
        Returns (is_justified, audit_note).
        """
        if sufficiency == EvidenceSufficiencyLevel.INSUFFICIENT and confidence == ReviewConfidence.HIGH:
            return (
                False,
                "Overconfidence anomaly: Reviewer asserted HIGH confidence despite INSUFFICIENT evidence.",
            )

        if sufficiency == EvidenceSufficiencyLevel.PARTIALLY_SUFFICIENT and confidence == ReviewConfidence.HIGH:
            return (
                True,
                "Caution: Reviewer asserted HIGH confidence with PARTIALLY_SUFFICIENT evidence.",
            )

        return True, "Confidence level is epistemically aligned with evidence sufficiency."
