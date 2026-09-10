"""
Universal Document Intelligence System V5 — Reviewer Expertise Router.

Phase 6: Routes review cases to suitably qualified experts while enforcing
capability prerequisites, workload limits, and conflict-of-interest exclusions.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple
from app.review.contracts.review_case import ReviewCase
from app.review.contracts.reviewer import ReviewerCapabilityProfile, ReviewerProfile


class ExpertiseRouter:
    """Matches pending review cases to qualified, available reviewers."""

    @classmethod
    def can_review_case(
        cls,
        reviewer: ReviewerProfile,
        case: ReviewCase,
        active_lease_count: int = 0,
        capability_profile: Optional[ReviewerCapabilityProfile] = None,
    ) -> Tuple[bool, str]:
        """
        Determines if a reviewer is eligible to review a given case.
        Returns (is_eligible, explanation).
        """
        if not reviewer.is_active:
            return False, f"Reviewer {reviewer.reviewer_id} is inactive."

        if active_lease_count >= reviewer.max_concurrent_leases:
            return False, f"Reviewer has reached maximum concurrent leases ({reviewer.max_concurrent_leases})."

        # Check required capabilities
        missing_caps = [c for c in case.required_capabilities if not reviewer.has_capability(c)]
        if missing_caps:
            missing_names = ", ".join(c.value for c in missing_caps)
            return False, f"Reviewer lacks required capabilities: {missing_names}."

        # Check capability profile specific constraints
        if capability_profile:
            if case.artifact_type.upper() not in [fmt.upper() for fmt in capability_profile.specialized_artifacts]:
                return False, f"Reviewer profile does not support artifact format {case.artifact_type}."

            # Conflict of interest check
            case_tags = case.metadata.get("tags", [])
            for tag in case_tags:
                if tag in capability_profile.conflict_of_interest_tags:
                    return False, f"Conflict of interest detected with case tag '{tag}'."

        return True, "Reviewer is eligible for this case."

    @classmethod
    def find_eligible_cases(
        cls,
        reviewer: ReviewerProfile,
        cases: Sequence[ReviewCase],
        active_lease_count: int = 0,
        capability_profile: Optional[ReviewerCapabilityProfile] = None,
    ) -> List[ReviewCase]:
        """Filters and returns cases sorted by priority that the reviewer is qualified to inspect."""
        eligible: List[ReviewCase] = []
        for case in cases:
            ok, _ = cls.can_review_case(
                reviewer=reviewer,
                case=case,
                active_lease_count=active_lease_count,
                capability_profile=capability_profile,
            )
            if ok:
                eligible.append(case)

        # Return sorted descending by priority score
        return sorted(eligible, key=lambda c: c.priority_score, reverse=True)
