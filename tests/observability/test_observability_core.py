"""
Unit tests for core observability components (contracts, context, events, metrics, profiling, lineage).
"""

from __future__ import annotations

import time
import pytest
from app.observability import (
    ObservabilityContextManager,
    observe_run,
    observe_span,
    record_event,
    record_metric,
    get_current_trace,
    get_current_context,
    MetricsRegistry,
    EventType,
    ObservationLevel,
    ArtifactLineageGraph,
    record_artifact,
    export_report,
)
from app.observability.profiling import identify_bottlenecks, SlowOperationThresholds, check_slow_operation


def test_observability_disabled():
    """Ensure that if observability is disabled, no events/spans are recorded."""
    ObservabilityContextManager.set_enabled(False)
    try:
        with observe_run("disabled_test") as run_id:
            with observe_span("span1"):
                record_event(EventType.DIAGNOSTIC_EMITTED, "Should not log")
                record_metric("metric.test", 1.0)
                record_artifact("art_id", "path", "PDF")

        report = get_current_trace()
        assert report is None
    finally:
        ObservabilityContextManager.set_enabled(True)


def test_run_context_and_span_hierarchy():
    """Verify context variable nesting, span hierarchy, and timestamps."""
    with observe_run("run_test") as run_id:
        ctx_run = get_current_context()
        assert ctx_run.run_id == run_id
        assert ctx_run.trace_id is not None
        assert ctx_run.parent_span_id is None
        assert ctx_run.span_id is None

        with observe_span("span_parent", component="CompA", stage="stage1") as parent_id:
            ctx_parent = get_current_context()
            assert ctx_parent.span_id == parent_id
            assert ctx_parent.parent_span_id is None
            assert ctx_parent.stage == "stage1"
            assert ctx_parent.component == "CompA"

            with observe_span("span_child", component="CompB", stage="stage1") as child_id:
                ctx_child = get_current_context()
                assert ctx_child.span_id == child_id
                assert ctx_child.parent_span_id == parent_id
                assert ctx_child.stage == "stage1"
                assert ctx_child.component == "CompB"

        report = get_current_trace()
        assert report is not None
        assert report.run_summary.run_id == run_id
        assert len(report.spans) == 2
        
        # Verify parent child links
        spans_map = {s.name: s for s in report.spans}
        assert spans_map["span_child"].parent_span_id == spans_map["span_parent"].span_id
        assert spans_map["span_parent"].duration_ms is not None
        assert spans_map["span_child"].duration_ms is not None


def test_event_collection_and_filtering():
    """Verify structured event recording and filtering utilities."""
    from app.observability.events import get_events

    with observe_run("event_test") as run_id:
        record_event(EventType.CAPABILITY_RESOLVED, "Capability matched", level=ObservationLevel.INFO, attributes={"cap": "REASONING"})
        record_event(EventType.DIAGNOSTIC_EMITTED, "Low score warnings", level=ObservationLevel.WARNING)

        # Retrieve report
        events_all = get_events(run_id=run_id)
        assert len(events_all) > 2  # run_started, capability_resolved, diagnostic_emitted, run_completed...
        
        events_warning = get_events(run_id=run_id, level=ObservationLevel.WARNING)
        assert len(events_warning) == 1
        assert "warnings" in events_warning[0].message


def test_metrics_registry_timers_counters():
    """Verify counter, gauge, timers, and timer context manager aggregations."""
    with observe_run("metrics_test") as run_id:
        MetricsRegistry.increment("test.counter", 2.0, tags={"env": "test"})
        MetricsRegistry.set("test.gauge", 85.0)

        with MetricsRegistry.timer("test.timer"):
            time.sleep(0.005)

        report = get_current_trace()
        assert report is not None
        
        metrics_map = {m.name: m for m in report.metrics}
        assert "test.counter" in metrics_map
        assert metrics_map["test.counter"].value == 2.0
        assert metrics_map["test.counter"].tags == {"env": "test"}
        assert "test.gauge" in metrics_map
        assert metrics_map["test.gauge"].value == 85.0
        assert "test.timer" in metrics_map
        assert metrics_map["test.timer"].value >= 5.0


def test_bottleneck_detection_and_thresholds():
    """Verify profiling bottlenecks and slow operation warning diagnostics."""
    with observe_run("profiling_test") as run_id:
        with observe_span("intel", stage="intelligence"):
            time.sleep(0.01)
        with observe_span("render", stage="rendering"):
            time.sleep(0.02)

        # check slow rendering warning
        check_slow_operation("rendering", 6000.0)  # threshold is 5000ms

        bottlenecks = identify_bottlenecks()
        assert len(bottlenecks) >= 2
        assert bottlenecks[0]["component"] == "rendering"
        assert bottlenecks[1]["component"] == "intelligence"
        
        report = get_current_trace()
        diagnostic_events = [e for e in report.events if e.event_type == EventType.DIAGNOSTIC_EMITTED]
        assert len(diagnostic_events) == 1
        assert "Slow operation" in diagnostic_events[0].message


def test_artifact_lineage_graph():
    """Test register_artifact lineage node building and graph ancestor/descendant lookups."""
    with observe_run("lineage_test") as run_id:
        record_artifact("req", "outputs/request.json", "request")
        record_artifact("blue", "outputs/blueprint.json", "blueprint", parent_artifacts=["req"])
        record_artifact("comp", "outputs/composition.json", "composition", parent_artifacts=["blue"])
        record_artifact("pdf_output", "outputs/final.pdf", "PDF", parent_artifacts=["comp"])

        report = get_current_trace()
        assert len(report.artifact_lineage) == 4

        graph = ArtifactLineageGraph(report.artifact_lineage)
        assert graph.get_ancestors("pdf_output") == ["blue", "comp", "req"]
        assert graph.get_descendants("req") == ["blue", "comp", "pdf_output"]
        assert graph.get_descendants("comp") == ["pdf_output"]
