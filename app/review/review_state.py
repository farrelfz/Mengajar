"""
Universal Document Intelligence System V5 — Human Review State Machine.

Phase 6: Deterministic, auditable state machine for the human review lifecycle.
Explicitly decoupled from ProductionStateMachine.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from app.review.contracts.enums import ReviewState


class IllegalReviewStateTransitionError(ValueError):
    """Raised when an illegal transition is attempted on a review case."""

    def __init__(self, from_state: ReviewState, to_state: ReviewState, reason: str = "") -> None:
        msg = f"Illegal review state transition from {from_state.value} to {to_state.value}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason


@dataclass(frozen=True)
class ReviewStateTransitionRecord:
    """Immutable audit record of a review case state transition."""
    from_state: ReviewState
    to_state: ReviewState
    timestamp: float
    actor_id: str = "system"
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReviewStateMachine:
    """Deterministic, auditable state machine governing ReviewCase lifecycles."""

    LEGAL_TRANSITIONS: Dict[ReviewState, Set[ReviewState]] = {
        ReviewState.OPEN: {
            ReviewState.LEASED,
            ReviewState.DEFERRED,
            ReviewState.CLOSED_NO_ACTION,
            ReviewState.ESCALATED,
        },
        ReviewState.LEASED: {
            ReviewState.UNDER_REVIEW,
            ReviewState.DIRECTIVE_PROPOSED,
            ReviewState.AWAITING_SECOND_REVIEW,
            ReviewState.RESOLVED,
            ReviewState.ESCALATED,
            ReviewState.OPEN,  # lease timeout or cancellation returns to OPEN
            ReviewState.DEFERRED,
        },
        ReviewState.UNDER_REVIEW: {
            ReviewState.AWAITING_SECOND_REVIEW,
            ReviewState.ADJUDICATION,
            ReviewState.DIRECTIVE_PROPOSED,
            ReviewState.RESOLVED,
            ReviewState.ESCALATED,
            ReviewState.DEFERRED,
            ReviewState.OPEN,  # lease expired mid-review
        },
        ReviewState.AWAITING_SECOND_REVIEW: {
            ReviewState.UNDER_REVIEW,
            ReviewState.ADJUDICATION,
            ReviewState.DIRECTIVE_PROPOSED,
            ReviewState.RESOLVED,
            ReviewState.ESCALATED,
        },
        ReviewState.ADJUDICATION: {
            ReviewState.DIRECTIVE_PROPOSED,
            ReviewState.RESOLVED,
            ReviewState.ESCALATED,
            ReviewState.CLOSED_NO_ACTION,
        },
        ReviewState.DIRECTIVE_PROPOSED: {
            ReviewState.DIRECTIVE_VALIDATED,
            ReviewState.UNDER_REVIEW,  # validation rejected directive
            ReviewState.ESCALATED,
        },
        ReviewState.DIRECTIVE_VALIDATED: {
            ReviewState.REPAIR_REPLAY_REQUESTED,
            ReviewState.RESOLVED,
            ReviewState.ESCALATED,
        },
        ReviewState.REPAIR_REPLAY_REQUESTED: {
            ReviewState.RESOLVED,
            ReviewState.OPEN,  # replay failed; reopened for review
            ReviewState.ESCALATED,
        },
        # Terminal / Closed states
        ReviewState.RESOLVED: set(),
        ReviewState.CLOSED_NO_ACTION: set(),
        ReviewState.ESCALATED: {ReviewState.OPEN, ReviewState.ADJUDICATION},  # Can be reopened by senior specialist
        ReviewState.DEFERRED: {ReviewState.OPEN},
    }

    def __init__(self, initial_state: ReviewState = ReviewState.OPEN) -> None:
        self._current_state = initial_state
        self._history: List[ReviewStateTransitionRecord] = [
            ReviewStateTransitionRecord(
                from_state=initial_state,
                to_state=initial_state,
                timestamp=time.time(),
                actor_id="system",
                reason="Review case initialized",
            )
        ]

    @property
    def current_state(self) -> ReviewState:
        return self._current_state

    @property
    def history(self) -> Tuple[ReviewStateTransitionRecord, ...]:
        return tuple(self._history)

    def can_transition_to(self, target_state: ReviewState) -> bool:
        allowed = self.LEGAL_TRANSITIONS.get(self._current_state, set())
        return target_state in allowed

    def transition(
        self,
        target_state: ReviewState,
        actor_id: str = "system",
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ReviewStateTransitionRecord:
        """Executes a transition or raises IllegalReviewStateTransitionError."""
        if not self.can_transition_to(target_state):
            raise IllegalReviewStateTransitionError(
                from_state=self._current_state,
                to_state=target_state,
                reason=f"Transition from {self._current_state.value} to {target_state.value} is forbidden.",
            )

        record = ReviewStateTransitionRecord(
            from_state=self._current_state,
            to_state=target_state,
            timestamp=time.time(),
            actor_id=actor_id,
            reason=reason,
            metadata=metadata or {},
        )
        self._history.append(record)
        self._current_state = target_state
        return record
