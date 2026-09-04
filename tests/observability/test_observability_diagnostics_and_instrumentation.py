"""
Integration and regression tests for trace diagnostics, determinism, and engine pipeline instrumentation.
"""

from __future__ import annotations

import time
import pytest
from app.observability import (
    FailureDiagnosticEngine,
    get_current_trace,
    export_report,
    observe_run,
    observe_span,
    record_event,
    EventType,
)
from app.orchestration.contracts import JobMetadata, ProductionJobRequest, ProductionJobStatus
from app.orchestration.engine import ProductionOrchestrator
from app.orchestration.idempotency import IdempotencyRegistry


def test_failure_diagnostics_causal_chains():
    """Verify diagnostic exceptions and causal contexts."""
    with observe_run("diag_test") as run_id:
        try:
            try:
                raise KeyError("Configuration key missing")
            except KeyError as inner:
                raise ValueError("Initialization failure") from inner
        except Exception as exc:
            diag = FailureDiagnosticEngine.capture_failure(
                exc,
                stage="composition",
                component="LayoutEngine",
                completed_stages=["validation"],
                partial_outputs={"layout": "partial_v1"},
            )

            assert diag.stage == "composition"
            assert diag.component == "LayoutEngine"
            assert diag.exception_type == "ValueError"
            assert diag.message == "Initialization failure"
            assert len(diag.causal_context) == 1
            assert "KeyError" in diag.causal_context[0]
            assert "Configuration key missing" in diag.causal_context[0]
            assert diag.completed_stages == ["validation"]
            assert diag.partial_outputs == {"layout": "partial_v1"}

            report = get_current_trace()
            assert report is not None
            assert report.diagnostics is not None
            assert report.diagnostics.failure_id == diag.failure_id


def test_pipeline_instrumentation_with_orchestrator():
    """Verify that running the production engine registers proper spans and events."""
    IdempotencyRegistry.clear()
    orch = ProductionOrchestrator()

    req = ProductionJobRequest(
        job_id="job_trace_test",
        raw_input="Sample prompt for testing engine traces.",
        metadata=JobMetadata(domain="general", profile="fast_preview"),
    )

    res = orch.run(req)
    assert res.success is True

    # Retrieve matching trace reports
    from app.observability.tracing import active_reports
    # Minimal runs should create a report
    assert len(active_reports) >= 1
    
    report = list(active_reports.values())[-1]
    assert report.run_summary.status == "completed"
    
    # Fast Preview profile spans
    span_names = [s.name for s in report.spans]
    assert "request_validation" in span_names
    assert "blueprint_generation" in span_names
    assert "composition" in span_names
    assert "rendering" in span_names
    assert "finalization" in span_names

    # Check registered artifacts
    lineage_ids = [l.artifact_id for l in report.artifact_lineage]
    assert "request" in lineage_ids
    assert "blueprint" in lineage_ids
    assert "composition" in lineage_ids
    assert "pdf" in lineage_ids


def normalize_trace(data: dict) -> dict:
    """Strip dynamic variables (IDs, timestamps, durations) from trace dictionary."""
    def clean(val, parent_key=None):
        if isinstance(val, dict):
            new_val = {}
            for k, v in val.items():
                if k in [
                    "run_id",
                    "trace_id",
                    "span_id",
                    "parent_span_id",
                    "source_run_id",
                    "event_id",
                    "artifact_id",
                    "timestamp",
                    "started_at",
                    "completed_at",
                    "start_time",
                    "end_time",
                    "duration_ms",
                    "execution_duration_ms",
                    "created_at",
                ]:
                    continue
                if k == "value" or k == "duration_ms":
                    new_val[k] = 0.0
                elif k == "message" and isinstance(v, str) and v.startswith("Metric recorded: "):
                    if "=" in v:
                        new_val[k] = v.split("=")[0]
                    else:
                        new_val[k] = v
                else:
                    new_val[k] = clean(v, k)
            return new_val
        elif isinstance(val, list):
            return [clean(x, parent_key) for x in val]
        elif isinstance(val, str):
            return val.replace("job_det_1", "job_generic").replace("job_det_2", "job_generic")
        return val
    return clean(data)


def test_trace_determinism():
    """Verify structural determinism across identical engine executions."""
    IdempotencyRegistry.clear()
    orch = ProductionOrchestrator()

    req1 = ProductionJobRequest(
        job_id="job_det_1",
        raw_input="Deterministic replay query.",
        metadata=JobMetadata(domain="general", profile="fast_preview"),
    )
    req2 = ProductionJobRequest(
        job_id="job_det_2",
        raw_input="Deterministic replay query.",
        metadata=JobMetadata(domain="general", profile="fast_preview"),
    )

    res1 = orch.run(req1)
    IdempotencyRegistry.clear()
    res2 = orch.run(req2)
    assert res1.success is True
    assert res2.success is True

    from app.observability.tracing import active_reports
    report1 = active_reports.get(list(active_reports.keys())[-2])
    report2 = active_reports.get(list(active_reports.keys())[-1])

    # Convert to dict and normalize
    dict1 = export_report(report1.run_summary.run_id)
    dict2 = export_report(report2.run_summary.run_id)

    norm1 = normalize_trace(dict1)
    norm2 = normalize_trace(dict2)

    assert norm1 == norm2


def test_multi_run_isolation():
    """Verify concurrent/sequential trace isolation (no context contamination)."""
    with observe_run("run_A") as run_a_id:
        with observe_span("span_A"):
            record_event(EventType.DIAGNOSTIC_EMITTED, "Event from A")

    with observe_run("run_B") as run_b_id:
        with observe_span("span_B"):
            record_event(EventType.DIAGNOSTIC_EMITTED, "Event from B")

    from app.observability.tracing import active_reports
    report_a = active_reports.get(run_a_id)
    report_b = active_reports.get(run_b_id)

    assert report_a is not None
    assert report_b is not None

    spans_a = [s.name for s in report_a.spans]
    spans_b = [s.name for s in report_b.spans]

    assert "span_A" in spans_a
    assert "span_B" not in spans_a

    assert "span_B" in spans_b
    assert "span_A" not in spans_b

    events_a = [e.message for e in report_a.events]
    events_b = [e.message for e in report_b.events]

    assert "Event from A" in events_a
    assert "Event from B" not in events_a

    assert "Event from B" in events_b
    assert "Event from A" not in events_b
