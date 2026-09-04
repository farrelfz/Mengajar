"""
Failure Isolation: Classification, containment, and recovery categorization.
"""

from __future__ import annotations

from typing import Any
from app.orchestration.contracts import FailureCategory, FailureSeverity, ProductionFailure


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
