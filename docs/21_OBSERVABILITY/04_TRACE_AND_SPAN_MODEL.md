# Trace and Span Model

This document explains the runtime traces, span hierarchies, status states, and attributes.

## Core Telemetry Models
- **RunSummary**: Captures high-level status, start/end timestamps, overall duration, and aggregations (counts for stages, spans, errors, and lineage items).
- **SpanRecord**: Records span IDs, names, component identifiers, stages, start/end times, durations in milliseconds, execution status (`running`, `succeeded`, `failed`), attributes dictionaries, and error messages.

## Span Lifecycle
1. **observe_run**: Initiates a trace context. Yields the execution control block. Captures exceptions if unhandled, logging a run failure.
2. **observe_span**: Creates nested operations. Captures times and error statuses on exit.
3. **Timer Registry**: Records millisecond-accurate latency benchmarks.
