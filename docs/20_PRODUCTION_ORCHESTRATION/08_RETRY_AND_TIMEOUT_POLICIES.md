# Retry and Timeout Policies

This document details retry evaluation, backoffs, and timeout policies.

## Retry Policies
- **max_attempts**: Maximum retries configured per stage.
- **backoff_strategy**: Supporting `NO_RETRY`, `IMMEDIATE`, `LINEAR`, and `EXPONENTIAL` backoff strategies.
- Transient errors in rendering evaluate the current attempt against `max_attempts` and decide whether to transition the stage back to `RETRYING` and re-execute.

## Timeout Policies
To prevent execution freezes, stages declare timeout constraints:
- **Grounding Stage**: 30 seconds
- **Rendering Stage**: 60 seconds
- **Quality Evaluation**: 10 seconds

Current implementation runs synchronously but defines clean interface abstractions compatible with future async/distributed timeouts.
