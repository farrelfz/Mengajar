"""
Universal Document Intelligence System V5 — Canonical Production State Machine.

Phase 3D: Closed-loop multi-artifact generation, quality governance & safe convergence.
Enforces strictly valid state transitions, rejects illegal bypasses (e.g. RENDERED -> EXPORTED
without Quality Authority approval), and records immutable audit transitions.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field


class ProductionState(str, Enum):
    """Authoritative lifecycle states of a document production execution."""
    CREATED = "CREATED"

    SOURCE_VALIDATING = "SOURCE_VALIDATING"
    SOURCE_PARSED = "SOURCE_PARSED"

    KNOWLEDGE_PROCESSING = "KNOWLEDGE_PROCESSING"
    KNOWLEDGE_READY = "KNOWLEDGE_READY"

    INTENT_RESOLUTION = "INTENT_RESOLUTION"
    INTENT_READY = "INTENT_READY"

    TRANSFORMATION = "TRANSFORMATION"
    BLUEPRINT_READY = "BLUEPRINT_READY"

    GROUPING = "GROUPING"
    COMPOSITION_READY = "COMPOSITION_READY"

    RENDERING = "RENDERING"
    RENDERED = "RENDERED"

    QUALITY_EVALUATING = "QUALITY_EVALUATING"
    QUALITY_EVALUATED = "QUALITY_EVALUATED"

    REPAIR_ANALYZING = "REPAIR_ANALYZING"
    REPAIR_PLANNING = "REPAIR_PLANNING"
    REPAIRING = "REPAIRING"

    RE_RENDERING = "RE_RENDERING"
    RE_VALIDATING = "RE_VALIDATING"

    APPROVED = "APPROVED"
    APPROVED_WITH_WARNINGS = "APPROVED_WITH_WARNINGS"

    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"

    EXPORTING = "EXPORTING"
    EXPORTED = "EXPORTED"

    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class IllegalStateTransitionError(RuntimeError):
    """Raised when an illegal state transition is attempted."""
    def __init__(self, from_state: ProductionState, to_state: ProductionState, reason: str = ""):
        msg = f"Illegal production state transition from '{from_state.value}' to '{to_state.value}'."
        if reason:
            msg += f" Reason: {reason}"
        super().__init__(msg)
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason


@dataclass(frozen=True)
class StateTransitionRecord:
    """Immutable audit record of a production state change."""
    from_state: ProductionState
    to_state: ProductionState
    timestamp: float
    iteration: int
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProductionStateMachine:
    """Deterministic, auditable state machine enforcing strict lifecycle transitions."""

    # Explicit whitelist of legal transitions
    LEGAL_TRANSITIONS: Dict[ProductionState, Set[ProductionState]] = {
        ProductionState.CREATED: {
            ProductionState.SOURCE_VALIDATING,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.SOURCE_VALIDATING: {
            ProductionState.SOURCE_PARSED,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.SOURCE_PARSED: {
            ProductionState.KNOWLEDGE_PROCESSING,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.KNOWLEDGE_PROCESSING: {
            ProductionState.KNOWLEDGE_READY,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.KNOWLEDGE_READY: {
            ProductionState.INTENT_RESOLUTION,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.INTENT_RESOLUTION: {
            ProductionState.INTENT_READY,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.INTENT_READY: {
            ProductionState.TRANSFORMATION,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.TRANSFORMATION: {
            ProductionState.BLUEPRINT_READY,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.BLUEPRINT_READY: {
            ProductionState.GROUPING,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.GROUPING: {
            ProductionState.COMPOSITION_READY,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.COMPOSITION_READY: {
            ProductionState.RENDERING,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.RENDERING: {
            ProductionState.RENDERED,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.RENDERED: {
            # Must be evaluated by Quality Authority before any approval/export!
            ProductionState.QUALITY_EVALUATING,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.QUALITY_EVALUATING: {
            ProductionState.QUALITY_EVALUATED,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.QUALITY_EVALUATED: {
            ProductionState.APPROVED,
            ProductionState.APPROVED_WITH_WARNINGS,
            ProductionState.REPAIR_ANALYZING,
            ProductionState.MANUAL_REVIEW_REQUIRED,
            ProductionState.BLOCKED,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.REPAIR_ANALYZING: {
            ProductionState.REPAIR_PLANNING,
            ProductionState.MANUAL_REVIEW_REQUIRED,
            ProductionState.BLOCKED,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.REPAIR_PLANNING: {
            ProductionState.REPAIRING,
            ProductionState.MANUAL_REVIEW_REQUIRED,
            ProductionState.BLOCKED,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.REPAIRING: {
            ProductionState.RE_RENDERING,
            ProductionState.REPAIR_ANALYZING,
            ProductionState.BLUEPRINT_READY,
            ProductionState.GROUPING,
            ProductionState.MANUAL_REVIEW_REQUIRED,
            ProductionState.BLOCKED,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.RE_RENDERING: {
            ProductionState.RE_VALIDATING,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.RE_VALIDATING: {
            ProductionState.QUALITY_EVALUATED,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.APPROVED: {
            ProductionState.EXPORTING,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.APPROVED_WITH_WARNINGS: {
            ProductionState.EXPORTING,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        ProductionState.EXPORTING: {
            ProductionState.EXPORTED,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
        },
        # Terminal states have no further transitions (immutable end)
        ProductionState.EXPORTED: set(),
        ProductionState.MANUAL_REVIEW_REQUIRED: set(),
        ProductionState.BLOCKED: set(),
        ProductionState.FAILED: set(),
        ProductionState.CANCELLED: set(),
    }

    def __init__(self, initial_state: ProductionState = ProductionState.CREATED) -> None:
        self._current_state = initial_state
        self._history: List[StateTransitionRecord] = [
            StateTransitionRecord(
                from_state=initial_state,
                to_state=initial_state,
                timestamp=time.time(),
                iteration=0,
                reason="Initial state creation",
            )
        ]

    @property
    def current_state(self) -> ProductionState:
        return self._current_state

    @property
    def history(self) -> Tuple[StateTransitionRecord, ...]:
        return tuple(self._history)

    def can_transition_to(self, target_state: ProductionState) -> bool:
        allowed = self.LEGAL_TRANSITIONS.get(self._current_state, set())
        return target_state in allowed

    def transition(
        self,
        target_state: ProductionState,
        iteration: int = 0,
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StateTransitionRecord:
        """Executes a state transition or raises IllegalStateTransitionError."""
        if not self.can_transition_to(target_state):
            # Formulate detailed refusal reason
            if self._current_state == ProductionState.RENDERED and target_state == ProductionState.EXPORTED:
                detail = "Rendered artifacts cannot bypass Quality Authority evaluation to export directly."
            elif self._current_state == ProductionState.BLOCKED and target_state in (ProductionState.EXPORTING, ProductionState.EXPORTED):
                detail = "Blocked artifacts cannot be exported under any circumstance."
            elif self._current_state == ProductionState.MANUAL_REVIEW_REQUIRED and target_state == ProductionState.REPAIRING:
                detail = "Artifacts flagged for manual review cannot be repaired autonomously."
            else:
                detail = f"Transition not allowed by canonical lifecycle rules from {self._current_state.value}."

            raise IllegalStateTransitionError(
                from_state=self._current_state,
                to_state=target_state,
                reason=f"{reason} - {detail}" if reason else detail,
            )

        rec = StateTransitionRecord(
            from_state=self._current_state,
            to_state=target_state,
            timestamp=time.time(),
            iteration=iteration,
            reason=reason,
            metadata=metadata or {},
        )
        self._history.append(rec)
        self._current_state = target_state
        return rec
