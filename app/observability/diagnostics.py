"""
Failure diagnostic engine capturing execution errors and context variables.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Optional

from app.observability.contracts import FailureDiagnostic
from app.observability.tracing import get_current_report


class FailureDiagnosticEngine:
    """System to extract diagnostics, stack context, and causal failures."""

    @staticmethod
    def capture_failure(
        exc: Exception,
        stage: Optional[str] = None,
        component: Optional[str] = None,
        completed_stages: Optional[list[str]] = None,
        partial_outputs: Optional[dict[str, Any]] = None,
    ) -> FailureDiagnostic:
        report = get_current_report()

        # Trace causality
        causal_context: list[str] = []
        cause = exc.__cause__ or exc.__context__
        while cause:
            causal_context.append(f"{type(cause).__name__}: {str(cause)}")
            cause = cause.__cause__ or cause.__context__

        diagnostic = FailureDiagnostic(
            failure_id=str(uuid.uuid4()),
            run_id=report.run_summary.run_id if report else "unknown_run",
            trace_id=report.run_summary.trace_id if report else "unknown_trace",
            stage=stage,
            component=component,
            exception_type=type(exc).__name__,
            message=str(exc),
            causal_context=causal_context,
            completed_stages=completed_stages or [],
            partial_outputs=partial_outputs or {},
            timestamp=time.time(),
        )

        if report:
            report.diagnostics = diagnostic

        return diagnostic
