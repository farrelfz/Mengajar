"""
Universal Document Intelligence System V5 — Blind Review Policy.

Phase 6: Masks specific metadata to eliminate anchoring, authority,
and confirmation bias without ever hiding safety-critical physical evidence.
"""

from __future__ import annotations

from typing import Any, Dict
from app.review.contracts.enums import BlindReviewMode
from app.review.contracts.evidence import ReviewEvidencePackage


class BlindReviewPolicy:
    """Enforces contextual masking on ReviewEvidencePackages."""

    @classmethod
    def apply_mask(
        cls,
        evidence_package: ReviewEvidencePackage,
        mode: BlindReviewMode = BlindReviewMode.FULL_CONTEXT_REVIEW,
    ) -> ReviewEvidencePackage:
        """Returns a copy of the evidence package with forbidden context stripped."""
        if mode == BlindReviewMode.FULL_CONTEXT_REVIEW:
            return evidence_package

        updates: Dict[str, Any] = {}

        if mode == BlindReviewMode.PARTIALLY_BLIND_REVIEW:
            # Mask previous repair history strategies and failed attempts
            updates["failed_strategies"] = ()
            # Mask historical score baseline
            updates["historical_baseline"] = None

        elif mode == BlindReviewMode.BLIND_REVIEW:
            # Mask previous repair strategies
            updates["failed_strategies"] = ()
            updates["historical_baseline"] = None
            # Mask quality decision and scores to prevent anchoring on system judgment
            updates["quality_decision"] = "MASKED_FOR_BLIND_REVIEW"
            updates["benchmark_comparison"] = None

        return evidence_package.model_copy(update=updates)
