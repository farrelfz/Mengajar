# Execution Events

This document details structured trace events logged during pipeline runs.

## Event Schema
Each logged `ExecutionEvent` contains:
- `event_id`: Unique identifier.
- `job_id`: Associated job id.
- `timestamp`: Float epoch.
- `event_type`: Categorical label (e.g. `JOB_CREATED`, `STAGE_STARTED`).
- `stage`: Stage ID string.
- `metadata`: Dictionary of event-specific outputs/metrics.

## Ordered Event Stream
Events are collected in chronological order and indexed by sequence number. Observability tools in future batches will consume this stream to render dashboards, trace latencies, and flag failed execution nodes.
