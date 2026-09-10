"""
Universal Document Intelligence System V5 — Authority Boundary Guard.

Phase 6: Structural barrier guaranteeing that human review cannot bypass
UnifiedQualityAuthority or AuthorizedExportGate.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from app.quality.contracts.decisions import ExportDecision
from app.review.safety.exceptions import SovereignAuthorityBypassAttemptError


class AuthorityBoundaryGuard:
    """Verifies that review workflows never violate Level-0 authority sovereignty."""

    @classmethod
    def verify_export_eligibility(
        cls,
        quality_decision: str,
        human_approved: bool,
    ) -> bool:
        """
        Guarantees that Human Approval ≠ Export Authorization.
        Only EXPORT_APPROVED or EXPORT_APPROVED_WITH_WARNINGS from UQA permits export.
        """
        valid_decisions = (
            ExportDecision.EXPORT_APPROVED.value,
            ExportDecision.EXPORT_APPROVED_WITH_WARNINGS.value,
        )

        if human_approved and quality_decision not in valid_decisions:
            raise SovereignAuthorityBypassAttemptError(
                f"Cannot authorize export: Human approved, but Level-0 Quality Authority decision is '{quality_decision}'. "
                f"Human approval can NEVER override Level-0 authority."
            )

        return quality_decision in valid_decisions

    @classmethod
    def guard_quality_scores(
        cls,
        original_scores: Dict[str, float],
        proposed_scores: Dict[str, float],
    ) -> None:
        """Forbids reviewers from mutating automated numerical quality scores."""
        if original_scores != proposed_scores:
            raise SovereignAuthorityBypassAttemptError(
                "Human reviewers cannot directly edit or recalculate Level-0 quality scores."
            )
