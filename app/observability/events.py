"""
Querying and filtering functions for trace events.
"""

from __future__ import annotations

from typing import Optional

from app.observability.contracts import EventType, ObservabilityEvent, ObservationLevel
from app.observability.context import ObservabilityContextManager
from app.observability.tracing import active_reports


def get_events(
    run_id: Optional[str] = None,
    event_type: Optional[EventType] = None,
    level: Optional[ObservationLevel] = None,
    stage: Optional[str] = None,
    component: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> list[ObservabilityEvent]:
    """Retrieve and filter events recorded during execution."""
    rid = run_id or ObservabilityContextManager.get_run_id()
    if not rid:
        return []

    report = active_reports.get(rid)
    if not report:
        return []

    res = report.events
    if event_type:
        res = [e for e in res if e.event_type == event_type]
    if level:
        res = [e for e in res if e.level == level]
    if stage:
        res = [e for e in res if e.context.stage == stage]
    if component:
        res = [e for e in res if e.context.component == component]
    if trace_id:
        res = [e for e in res if e.context.trace_id == trace_id]

    return res
