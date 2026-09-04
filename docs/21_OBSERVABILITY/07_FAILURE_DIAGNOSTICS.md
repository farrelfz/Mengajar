# Failure Diagnostics

This document details runtime error tracking, causal chains, and exception contexts.

## FailureDiagnostic Schema
When a pipeline stage encounters an exception:
- **exception_type**: Class name.
- **message**: Explanatory string.
- **causal_context**: Chronologically traversed cause tree (via `exc.__cause__` or `exc.__context__`).
- **completed_stages**: Sequence of successfully executed stages prior to failure.
- **partial_outputs**: Snapshot of the context's shared data when the failure occurred.

This diagnostic record is appended to the trace report, allowing debuggers to pinpoint exactly what was accomplished before a run crashed.
