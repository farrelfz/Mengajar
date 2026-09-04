"""
Tracing module managing run and span context lifecycles.
"""

from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from typing import Any, Generator, Optional

from app.observability.contracts import (
    EventType,
    ObservationContext,
    ObservabilityEvent,
    ObservabilityReport,
    ObservationLevel,
    RunSummary,
    SpanRecord,
)
from app.observability.context import (
    ObservabilityContextManager,
    component_var,
    parent_span_id_var,
    run_id_var,
    span_id_var,
    stage_var,
    trace_id_var,
)


# Global active reports repository
active_reports: dict[str, ObservabilityReport] = {}


def get_current_report() -> Optional[ObservabilityReport]:
    run_id = ObservabilityContextManager.get_run_id()
    if run_id:
        return active_reports.get(run_id)
    return None


def get_current_context() -> ObservationContext:
    return ObservationContext(
        run_id=ObservabilityContextManager.get_run_id() or "unknown_run",
        trace_id=ObservabilityContextManager.get_trace_id() or "unknown_trace",
        parent_span_id=ObservabilityContextManager.get_parent_span_id(),
        span_id=ObservabilityContextManager.get_span_id(),
        stage=ObservabilityContextManager.get_stage(),
        component=ObservabilityContextManager.get_component(),
        timestamp=time.time(),
    )


def record_event(
    event_type: EventType,
    message: str,
    level: ObservationLevel = ObservationLevel.INFO,
    attributes: Optional[dict[str, Any]] = None,
) -> None:
    if not ObservabilityContextManager.is_enabled():
        return

    run_id = ObservabilityContextManager.get_run_id()
    if not run_id:
        return

    report = active_reports.get(run_id)
    if not report:
        return

    event = ObservabilityEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        timestamp=time.time(),
        level=level,
        context=get_current_context(),
        message=message,
        attributes=attributes or {},
    )
    report.events.append(event)


def finish_run(run_id: str, status: str = "completed") -> None:
    report = active_reports.get(run_id)
    if not report:
        return

    summary = report.run_summary
    summary.status = status
    summary.completed_at = time.time()
    summary.duration_ms = (summary.completed_at - summary.started_at) * 1000.0

    # Aggregate metric counters
    summary.span_count = len(report.spans)
    summary.error_count = len(report.errors)
    summary.artifact_count = len(report.artifact_lineage)
    summary.stage_count = len(set(s.stage for s in report.spans if s.stage))

    record_event(
        EventType.RUN_COMPLETED if status == "completed" else EventType.RUN_FAILED,
        message=f"Run finished with status: {status}",
    )


@contextmanager
def observe_run(name: str) -> Generator[str, None, None]:
    if not ObservabilityContextManager.is_enabled():
        yield "disabled_run"
        return

    run_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())

    token_run = run_id_var.set(run_id)
    token_trace = trace_id_var.set(trace_id)

    report = ObservabilityReport(
        run_summary=RunSummary(
            run_id=run_id,
            trace_id=trace_id,
            status="running",
            started_at=time.time(),
        )
    )
    active_reports[run_id] = report

    record_event(
        EventType.RUN_STARTED,
        message=f"Run started: {name}",
    )

    try:
        yield run_id
        finish_run(run_id, "completed")
    except Exception as e:
        record_exception(e, recoverable=False)
        finish_run(run_id, "failed")
        raise
    finally:
        run_id_var.reset(token_run)
        trace_id_var.reset(token_trace)


@contextmanager
def observe_span(
    name: str, component: Optional[str] = None, stage: Optional[str] = None
) -> Generator[str, None, None]:
    if not ObservabilityContextManager.is_enabled():
        yield "disabled_span"
        return

    run_id = ObservabilityContextManager.get_run_id()
    if not run_id:
        yield "no_active_run"
        return

    span_id = str(uuid.uuid4())
    parent_id = ObservabilityContextManager.get_span_id()

    token_span = span_id_var.set(span_id)
    token_parent = parent_span_id_var.set(parent_id)

    prev_stage = stage_var.get()
    prev_comp = component_var.get()

    if stage:
        token_stage = stage_var.set(stage)
    if component:
        token_comp = component_var.set(component)

    start_time = time.time()
    record = SpanRecord(
        span_id=span_id,
        parent_span_id=parent_id,
        name=name,
        component=component or prev_comp,
        stage=stage or prev_stage,
        start_time=start_time,
        status="running",
    )

    report = active_reports.get(run_id)
    if report:
        report.spans.append(record)

    record_event(
        EventType.SPAN_STARTED,
        message=f"Span started: {name}",
        attributes={"component": component or prev_comp, "stage": stage or prev_stage},
    )

    try:
        yield span_id
        record.status = "succeeded"
        record.end_time = time.time()
        record.duration_ms = (record.end_time - record.start_time) * 1000.0
        record_event(
            EventType.SPAN_COMPLETED,
            message=f"Span completed: {name}",
            attributes={"duration_ms": record.duration_ms},
        )
    except Exception as e:
        record.status = "failed"
        record.error = str(e)
        record.end_time = time.time()
        record.duration_ms = (record.end_time - record.start_time) * 1000.0
        record_event(
            EventType.SPAN_FAILED,
            message=f"Span failed: {name}",
            attributes={"error": str(e), "duration_ms": record.duration_ms},
        )
        raise
    finally:
        span_id_var.reset(token_span)
        parent_span_id_var.reset(token_parent)
        if stage:
            stage_var.reset(token_stage)
        if component:
            component_var.reset(token_comp)


def record_exception(exc: Exception, recoverable: bool = False) -> None:
    if not ObservabilityContextManager.is_enabled():
        return

    run_id = ObservabilityContextManager.get_run_id()
    if not run_id:
        return

    report = active_reports.get(run_id)
    if not report:
        return

    import traceback
    from app.observability.contracts import ErrorRecord

    summary = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    err_record = ErrorRecord(
        exception_type=type(exc).__name__,
        message=str(exc),
        component=ObservabilityContextManager.get_component(),
        stage=ObservabilityContextManager.get_stage(),
        traceback_summary=summary,
        recoverable=recoverable,
        context=get_current_context(),
    )
    report.errors.append(err_record)
