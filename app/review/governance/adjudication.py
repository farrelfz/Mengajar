"""
Universal Document Intelligence System V5 — Review Adjudication Manager.

Phase 6: Governs senior expert resolution of contentious or divergent reviews.
"""

from __future__ import annotations

import time
from typing import Optional, Tuple

from app.review.contracts.enums import ReviewState
from app.review.contracts.review_case import ReviewCase
from app.review.contracts.review_decision import ReviewDecision
from app.review.contracts.reviewer import ReviewerProfile
from app.review.decisions.review_engine import ReviewDecisionEngine
from app.review.review_state import ReviewStateMachine


class AdjudicationManager:
    """Coordinates binding senior adjudication on conflicted review cases."""

    @classmethod
    def adjudicate(
        cls,
        case: ReviewCase,
        senior_reviewer: ReviewerProfile,
        binding_decision: ReviewDecision,
    ) -> Tuple[bool, ReviewCase, str]:
        """Resolves case via certified senior expert adjudication."""
        if not senior_reviewer.can_adjudicate():
            return (
                False,
                case,
                f"Reviewer '{senior_reviewer.reviewer_id}' is not authorized as a senior adjudicator "
                f"(requires active status, senior flag, and calibration >= 0.85).",
            )

        sm = ReviewStateMachine(initial_state=case.current_state)
        # Transition to ADJUDICATION if not already there
        if case.current_state != ReviewState.ADJUDICATION:
            if sm.can_transition_to(ReviewState.ADJUDICATION):
                sm.transition(ReviewState.ADJUDICATION, actor_id=senior_reviewer.reviewer_id, reason="Adjudication started")
            else:
                return False, case, f"Cannot enter ADJUDICATION from state '{case.current_state.value}'."

        # Apply the binding decision
        is_ok, updated_case, errors = ReviewDecisionEngine.apply_decision(
            case=case.model_copy(update={"current_state": ReviewState.ADJUDICATION}),
            decision=binding_decision,
        )
        if not is_ok:
            return False, case, "; ".join(errors)

        return True, updated_case, "Senior adjudication committed successfully."
