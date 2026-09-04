# Failure and Recovery

This document details error classifications and recovery behaviors.

## Failure Classifications
Errors are mapped into structured `ProductionFailure` models categorized under:
- **INPUT**: Bad parameters/ideas. (Fatal, no retry)
- **DEPENDENCY**: Missing context dependencies. (Fatal)
- **GROUNDING**: Contradictions detected by grounding gates. (Fatal)
- **RENDERING**: Browser-based render timeouts or process glitches. (Recoverable)
- **INTERNAL**: Unexpected python exceptions. (Fatal)

## Exception Isolation
All stage executions are wrapped in a generic `try-except` envelope. This guarantees that internal stage exceptions are trapped, isolated, logged, and mapped to a clean failure record rather than crashing the orchestrator loop. Downstream stages are transitively marked as `BLOCKED`.
