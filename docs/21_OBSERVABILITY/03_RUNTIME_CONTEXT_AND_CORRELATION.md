# Runtime Context and Correlation

This document describes how execution contexts propagate across nested boundaries using correlation identifiers.

## Context Correlation Keys
- **Run ID**: Unique UUID generated per pipeline run execution.
- **Trace ID**: Unique UUID correlating child operations under a single generation trigger.
- **Span ID**: Unique UUID corresponding to individual logical stages.
- **Parent Span ID**: Correlates nested sub-steps.

## Automatic Context Propagation
The system leverages Python's built-in `contextvars` module (`run_id_var`, `trace_id_var`, `span_id_var`, `parent_span_id_var`). When entering a context manager (`observe_run` or `observe_span`), context variables are updated thread-safely and task-safely, and restored upon exit. This avoids passing trace metrics through function signatures manually.
