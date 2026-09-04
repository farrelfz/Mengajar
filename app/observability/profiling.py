"""
Performance profiling and slow operation diagnostic threshold checks.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from app.observability.contracts import EventType
from app.observability.context import ObservabilityContextManager
from app.observability.tracing import get_current_report, record_event


class SlowOperationThresholds:
    default_stage_ms: float = 3000.0
    rendering_ms: float = 5000.0
    knowledge_retrieval_ms: float = 4000.0

    @classmethod
    def get_threshold(cls, name: str) -> float:
        name_lower = name.lower()
        if "rendering" in name_lower or "render" in name_lower:
            return cls.rendering_ms
        if "grounding" in name_lower or "retrieval" in name_lower:
            return cls.knowledge_retrieval_ms
        return cls.default_stage_ms


def check_slow_operation(name: str, duration_ms: float) -> None:
    """Evaluate duration and issue warning if slow operation threshold exceeded."""
    threshold = SlowOperationThresholds.get_threshold(name)
    if duration_ms > threshold:
        record_event(
            EventType.DIAGNOSTIC_EMITTED,
            message=f"Slow operation detected: {name} took {duration_ms:.1f}ms (threshold={threshold:.1f}ms)",
            attributes={
                "operation": name,
                "duration_ms": duration_ms,
                "threshold": threshold,
            },
        )


def identify_bottlenecks() -> list[dict[str, Any]]:
    """Determine performance bottlenecks across run components."""
    report = get_current_report()
    if not report:
        return []

    total_ms = report.run_summary.duration_ms
    if not total_ms or total_ms <= 0:
        total_ms = (time.time() - report.run_summary.started_at) * 1000.0

    if total_ms <= 0:
        return []

    durations: dict[str, float] = {}
    for span in report.spans:
        if span.duration_ms:
            key = span.stage or span.name
            durations[key] = durations.get(key, 0.0) + span.duration_ms

    sorted_components = sorted(durations.items(), key=lambda x: x[1], reverse=True)
    return [
        {
            "component": k,
            "duration_ms": round(v, 2),
            "percentage_of_run": round((v / total_ms) * 100.0, 1),
        }
        for k, v in sorted_components
    ]
