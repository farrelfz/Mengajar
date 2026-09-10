"""
Universal Document Intelligence System V5 — Signal Lifecycle State Machine.

Phase 3A.2 Hardening & Phase 3B: Strictly validated, immutable lifecycle transitions
for quality signals across detection, normalization, correlation, clustering,
causal attribution, repair, and resolution.
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any, Dict, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field


class QualitySignalLifecycleState(str, Enum):
    """The 10 canonical lifecycle states for quality signals."""
    RAW_DETECTION = "RAW_DETECTION"
    NORMALIZED = "NORMALIZED"
    CORRELATED = "CORRELATED"
    CLUSTERED = "CLUSTERED"
    CAUSAL_HYPOTHESIS = "CAUSAL_HYPOTHESIS"
    REPAIR_PROPOSED = "REPAIR_PROPOSED"
    REPAIR_APPLIED = "REPAIR_APPLIED"
    REVALIDATED = "REVALIDATED"
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


class InvalidLifecycleTransitionError(Exception):
    """Raised when an illegal lifecycle transition is attempted."""
    def __init__(self, from_state: QualitySignalLifecycleState, to_state: QualitySignalLifecycleState, rationale: str = ""):
        message = f"Illegal lifecycle transition from '{from_state.value}' to '{to_state.value}'."
        if rationale:
            message += f" Rationale: {rationale}"
        super().__init__(message)
        self.from_state = from_state
        self.to_state = to_state
        self.rationale = rationale


class QualitySignalLifecycleRecord(BaseModel):
    """Immutable audit record tracking the lifecycle history of a quality signal."""
    model_config = ConfigDict(frozen=True)

    record_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:8]}")
    signal_id: str
    current_state: QualitySignalLifecycleState = QualitySignalLifecycleState.RAW_DETECTION
    state_history: Tuple[Tuple[QualitySignalLifecycleState, float, str], ...] = Field(default_factory=tuple)
    active_repair_proposal_id: Optional[str] = None
    revalidation_signal_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SignalLifecycleStateMachine:
    """State machine governing validated transitions of quality signal lifecycles."""

    COMPLEX_LAYOUT_FAILURE_CODES: Set[str] = {
        "TEXT_TOO_SMALL",
        "HIGH_DENSITY",
        "DENSITY_OVERLOAD",
        "OVERFLOW_HIDDEN_CUTOFF",
        "TEXT_CLIPPING",
        "ELEMENT_COLLISION",
        "LAYOUT_MONOTONY",
        "LAYOUT_SEMANTIC_MISMATCH",
        "CARD_OVERLOAD",
    }

    VALID_TRANSITIONS: Dict[QualitySignalLifecycleState, Set[QualitySignalLifecycleState]] = {
        QualitySignalLifecycleState.RAW_DETECTION: {
            QualitySignalLifecycleState.NORMALIZED,
        },
        QualitySignalLifecycleState.NORMALIZED: {
            QualitySignalLifecycleState.CORRELATED,
            QualitySignalLifecycleState.CLUSTERED,
            QualitySignalLifecycleState.CAUSAL_HYPOTHESIS,  # Shortcut permitted only for single-source causes
        },
        QualitySignalLifecycleState.CORRELATED: {
            QualitySignalLifecycleState.CLUSTERED,
            QualitySignalLifecycleState.CAUSAL_HYPOTHESIS,
            QualitySignalLifecycleState.REPAIR_PROPOSED,
        },
        QualitySignalLifecycleState.CLUSTERED: {
            QualitySignalLifecycleState.CAUSAL_HYPOTHESIS,
            QualitySignalLifecycleState.REPAIR_PROPOSED,
        },
        QualitySignalLifecycleState.CAUSAL_HYPOTHESIS: {
            QualitySignalLifecycleState.CLUSTERED,
            QualitySignalLifecycleState.REPAIR_PROPOSED,
        },
        QualitySignalLifecycleState.REPAIR_PROPOSED: {
            QualitySignalLifecycleState.REPAIR_APPLIED,
            QualitySignalLifecycleState.UNRESOLVED,
        },
        QualitySignalLifecycleState.REPAIR_APPLIED: {
            QualitySignalLifecycleState.REVALIDATED,
            QualitySignalLifecycleState.UNRESOLVED,
        },
        QualitySignalLifecycleState.REVALIDATED: {
            QualitySignalLifecycleState.RESOLVED,
            QualitySignalLifecycleState.UNRESOLVED,
            QualitySignalLifecycleState.REPAIR_PROPOSED,
        },
        QualitySignalLifecycleState.UNRESOLVED: {
            QualitySignalLifecycleState.CAUSAL_HYPOTHESIS,
            QualitySignalLifecycleState.REPAIR_PROPOSED,
            QualitySignalLifecycleState.RESOLVED,
        },
        QualitySignalLifecycleState.RESOLVED: {
            QualitySignalLifecycleState.RAW_DETECTION,  # Re-opened upon regression
        },
    }

    @classmethod
    def is_valid_transition(
        cls,
        from_state: QualitySignalLifecycleState,
        to_state: QualitySignalLifecycleState,
    ) -> bool:
        """Returns True if the transition is permitted by lifecycle policy."""
        allowed = cls.VALID_TRANSITIONS.get(from_state, set())
        return to_state in allowed

    @classmethod
    def create_initial(
        cls,
        signal_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QualitySignalLifecycleRecord:
        """Initializes a new lifecycle record in RAW_DETECTION state."""
        now = time.time()
        initial_history = ((QualitySignalLifecycleState.RAW_DETECTION, now, "Initial detection ingested"),)
        return QualitySignalLifecycleRecord(
            signal_id=signal_id,
            current_state=QualitySignalLifecycleState.RAW_DETECTION,
            state_history=initial_history,
            metadata=metadata or {},
        )

    @classmethod
    def transition(
        cls,
        record: QualitySignalLifecycleRecord,
        next_state: QualitySignalLifecycleState,
        rationale: str = "",
        failure_code: Optional[str] = None,
        is_local_single_source: bool = False,
        active_repair_proposal_id: Optional[str] = None,
        revalidation_signal_id: Optional[str] = None,
    ) -> QualitySignalLifecycleRecord:
        """Advances lifecycle record to next state, raising InvalidLifecycleTransitionError if invalid."""
        if not cls.is_valid_transition(record.current_state, next_state):
            raise InvalidLifecycleTransitionError(
                from_state=record.current_state,
                to_state=next_state,
                rationale=rationale,
            )

        # Shortcut guard: NORMALIZED -> CAUSAL_HYPOTHESIS is forbidden for complex layout defects
        if record.current_state == QualitySignalLifecycleState.NORMALIZED and next_state == QualitySignalLifecycleState.CAUSAL_HYPOTHESIS:
            code_check = failure_code or record.metadata.get("failure_code", "")
            if code_check in cls.COMPLEX_LAYOUT_FAILURE_CODES and not is_local_single_source:
                raise InvalidLifecycleTransitionError(
                    from_state=record.current_state,
                    to_state=next_state,
                    rationale=f"Complex layout failure '{code_check}' cannot bypass correlation and clustering.",
                )

        now = time.time()
        updated_history = record.state_history + ((next_state, now, rationale),)

        return QualitySignalLifecycleRecord(
            record_id=record.record_id,
            signal_id=record.signal_id,
            current_state=next_state,
            state_history=updated_history,
            active_repair_proposal_id=active_repair_proposal_id or record.active_repair_proposal_id,
            revalidation_signal_id=revalidation_signal_id or record.revalidation_signal_id,
            metadata=record.metadata,
        )
