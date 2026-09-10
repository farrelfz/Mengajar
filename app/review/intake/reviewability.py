"""
Universal Document Intelligence System V5 — Reviewability Classifier.

Phase 6: Filters incoming cases to determine whether human expert attention
is genuinely required, avoiding fatigue from trivial auto-resolvable defects.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple
from app.review.contracts.enums import ReviewabilityStatus


class ReviewabilityClassifier:
    """Deterministic classifier evaluating whether a case requires human review."""

    AUTO_RESOLVABLE_FAILURE_CODES = {
        "FONT_TOO_SMALL",
        "PADDING_OVERFLOW",
        "LINE_HEIGHT_TIGHT",
        "TOKEN_OUT_OF_BOUNDS",
        "CONTAINER_PADDING_COLLISION",
    }

    SYSTEM_ERROR_CODES = {
        "CORRUPTED_MANIFEST",
        "AST_SYNTAX_ERROR",
        "RENDERER_CRASH",
        "UNHANDLED_EXCEPTION",
    }

    @classmethod
    def classify(
        cls,
        findings: Sequence[Dict[str, Any]],
        has_render_artifacts: bool = True,
        is_closed_or_archived: bool = False,
        has_system_exception: bool = False,
        is_regression: bool = False,
    ) -> Tuple[ReviewabilityStatus, str]:
        """
        Deterministically classifies case reviewability.
        Returns (ReviewabilityStatus, explanation).
        """
        if is_closed_or_archived:
            return (
                ReviewabilityStatus.NON_REVIEWABLE,
                "Artifact is permanently archived or closed; read-only review only.",
            )

        if has_system_exception:
            return (
                ReviewabilityStatus.SYSTEM_ERROR,
                "Case resulted from unhandled system crash or engine exception, not document quality.",
            )

        if not has_render_artifacts:
            return (
                ReviewabilityStatus.INSUFFICIENT_EVIDENCE,
                "Missing rendered page/slide outputs required for visual human inspection.",
            )

        # Check for system error codes in findings
        failure_codes = {f.get("failure_code", "") for f in findings}
        if any(fc in cls.SYSTEM_ERROR_CODES for fc in failure_codes):
            return (
                ReviewabilityStatus.SYSTEM_ERROR,
                "Critical syntax or manifest corruption detected; requires developer fix, not editorial review.",
            )

        # Regression is always expert review
        if is_regression:
            return (
                ReviewabilityStatus.EXPERT_REVIEW_REQUIRED,
                "Benchmark regression detected on golden reference artifact.",
            )

        # If empty findings, nothing to review
        if not findings:
            return (
                ReviewabilityStatus.NON_REVIEWABLE,
                "No findings or defects recorded on artifact.",
            )

        # Check if ALL findings are trivially auto-resolvable
        if failure_codes.issubset(cls.AUTO_RESOLVABLE_FAILURE_CODES):
            return (
                ReviewabilityStatus.AUTO_RESOLVABLE,
                "All recorded defects are known token/geometry issues resolvable by autonomous repair.",
            )

        # Default: complex semantic, pedagogical, or layout failure
        return (
            ReviewabilityStatus.EXPERT_REVIEW_REQUIRED,
            "Document contains complex structural, pedagogical, or unresolvable defects requiring expert judgment.",
        )
