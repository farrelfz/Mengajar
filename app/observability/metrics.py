"""
Registry for capturing performance and throughput metrics.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Generator, Optional

from app.observability.contracts import EventType, MetricRecord
from app.observability.context import ObservabilityContextManager
from app.observability.tracing import get_current_context, get_current_report, record_event


class MetricsRegistry:
    """Central registry to record timers, counters, gauges and histograms."""

    @staticmethod
    def record(
        name: str,
        value: float,
        unit: str = "count",
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        if not ObservabilityContextManager.is_enabled():
            return

        report = get_current_report()
        if not report:
            return

        ctx = get_current_context()
        record = MetricRecord(
            name=name,
            value=value,
            unit=unit,
            timestamp=time.time(),
            context=ctx,
            tags=tags or {},
        )
        report.metrics.append(record)

        # Emit an event corresponding to this metric
        record_event(
            EventType.METRIC_RECORDED,
            message=f"Metric recorded: {name}={value} {unit}",
            attributes={"metric_name": name, "value": value, "tags": tags or {}},
        )

    @classmethod
    def increment(
        cls,
        name: str,
        value: float = 1.0,
        unit: str = "count",
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        cls.record(name, value, unit, tags)

    @classmethod
    def set(
        cls,
        name: str,
        value: float,
        unit: str = "gauge",
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        cls.record(name, value, unit, tags)

    @classmethod
    def observe(
        cls,
        name: str,
        value: float,
        unit: str = "histogram",
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        cls.record(name, value, unit, tags)

    @classmethod
    @contextmanager
    def timer(
        cls, name: str, tags: Optional[dict[str, str]] = None
    ) -> Generator[None, None, None]:
        start = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start) * 1000.0
            cls.record(name, duration_ms, "ms", tags)
