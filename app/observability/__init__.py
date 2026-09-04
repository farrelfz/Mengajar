"""
Observability and Runtime Intelligence package facade.
"""

from __future__ import annotations

from typing import Optional

from app.observability.context import ObservabilityContextManager
from app.observability.contracts import (
    ArtifactLineageRecord,
    ErrorRecord,
    EventType,
    FailureDiagnostic,
    MetricRecord,
    ObservabilityEvent,
    ObservabilityReport,
    ObservationContext,
    ObservationLevel,
    RunSummary,
    SpanRecord,
)
from app.observability.tracing import (
    get_current_context,
    observe_run,
    observe_span,
    record_event,
    record_exception,
)
from app.observability.tracing import get_current_report as get_current_trace
from app.observability.metrics import MetricsRegistry
from app.observability.diagnostics import FailureDiagnosticEngine
from app.observability.lineage import ArtifactLineageGraph, record_artifact
from app.observability.export import export_json, export_report
from app.observability.reporting import generate_runtime_summary


def record_metric(
    name: str,
    value: float,
    unit: str = "count",
    tags: Optional[dict[str, str]] = None,
) -> None:
    """Convenience shortcut to record metric entries."""
    MetricsRegistry.record(name, value, unit, tags)
