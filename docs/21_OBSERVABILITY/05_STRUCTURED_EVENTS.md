# Structured Events

This document details event recording, types, attribute schemas, and filtering functions.

## Structured ObservabilityEvent Schema
- **event_id**: Unique identifier.
- **event_type**: Enum representing lifecycle transitions and operational signals.
- **timestamp**: Float epoch.
- **level**: Log level enum.
- **context**: Metadata copy (Run ID, Trace ID, Span ID, Component, Stage).
- **message**: Narrative description.
- **attributes**: Extensible dictionary for operational key-values.

## Events Query Interface
The `get_events` function exposes filtering options by:
- run_id
- event_type
- level
- stage
- component
- trace_id
It returns list results sorted chronologically.
