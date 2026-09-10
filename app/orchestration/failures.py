"""
Failure Isolation: Classification, containment, and recovery categorization.
"""

from __future__ import annotations

from typing import Any
from app.orchestration.contracts import FailureCategory, FailureSeverity, ProductionFailure


class PipelineStateSynchronizationError(Exception):
    """Raised when pipeline state invariants or synchronization constraints are violated."""

    def __init__(self, message: str, diagnostics: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics or {}


class PipelineProgressSynchronizationError(Exception):
    """Raised when pipeline progress counters, task denominators, or stage transitions violate invariants."""

    def __init__(self, message: str, diagnostics: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics or {}


class FailureIsolationManager:
    """Classifies exceptions into structured ProductionFailure records."""

    @classmethod
    def classify_exception(cls, stage_id: str, exception: Exception) -> ProductionFailure:
        msg = str(exception)
        msg_lower = msg.lower()

        if "input" in msg_lower or "empty" in msg_lower or "missing" in msg_lower:
            return ProductionFailure(
                stage_id=stage_id,
                category=FailureCategory.INPUT,
                severity=FailureSeverity.FATAL,
                message=msg,
                retryable=False,
            )
        elif "render" in msg_lower or "playwright" in msg_lower or "timeout" in msg_lower:
            return ProductionFailure(
                stage_id=stage_id,
                category=FailureCategory.RENDERING,
                severity=FailureSeverity.RECOVERABLE,
                message=msg,
                retryable=True,
            )
        elif "grounding" in msg_lower or "contradiction" in msg_lower:
            return ProductionFailure(
                stage_id=stage_id,
                category=FailureCategory.GROUNDING,
                severity=FailureSeverity.WARNING,
                message=msg,
                retryable=False,
            )
        else:
            return ProductionFailure(
                stage_id=stage_id,
                category=FailureCategory.INTERNAL,
                severity=FailureSeverity.FATAL,
                message=msg,
                retryable=False,
            )


from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class ProductionFailureType(str, Enum):
    """Canonical failure taxonomy distinguishing system crashes from quality or convergence issues."""
    SYSTEM_ERROR = "SYSTEM_ERROR"
    RENDER_FAILURE = "RENDER_FAILURE"
    QUALITY_FAILURE = "QUALITY_FAILURE"
    REPAIR_FAILURE = "REPAIR_FAILURE"
    SAFETY_VIOLATION = "SAFETY_VIOLATION"
    CONVERGENCE_FAILURE = "CONVERGENCE_FAILURE"


class ProductionFailureRecord(BaseModel):
    """Authoritative failure record for forensic analysis and user communication."""
    model_config = ConfigDict(frozen=True)

    failure_type: ProductionFailureType
    owning_layer: str
    message: str
    recoverability: str  # RECOVERABLE, FATAL, MANUAL_INTERVENTION
    repair_eligible: bool
    human_action_required: bool
    root_cause_reference: str | None = None
    diagnostics: dict[str, Any] = Field(default_factory=dict)
