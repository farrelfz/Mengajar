# Metrics and Performance Profiling

This document explains performance registry metrics, profiling capabilities, slow operation alerts, and bottleneck detection.

## Metrics Classes
- **increment(name, value, unit, tags)**: High-frequency throughput metrics (e.g. `artifacts.generated`).
- **set(name, value, unit, tags)**: Gauges tracking absolute stats (e.g. `quality.score`, `grounding.contradictions`).
- **timer(name, tags)**: Latency metric tracking context manager.

## Profiling and Bottleneck Identification
- **identify_bottlenecks()**: Summarizes elapsed execution time percentage relative to total run duration across pipeline stages.
- **check_slow_operation(name, duration_ms)**: Tests durations against configured thresholds (Rendering: 5000ms, Grounding/Retrieval: 4000ms, Default: 3000ms), logging warning events if exceeded.
