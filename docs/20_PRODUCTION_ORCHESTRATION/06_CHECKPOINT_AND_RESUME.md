# Checkpoint and Resume

This document details state serialization, InMemoryCheckpointStore, and recovery execution.

## Checkpoint Protocol
Checkpoints are captured at boundaries (e.g. Request Validated, Grounded, Planning Directed, Composed, Rendered).
- `completed_stages`: Records succeeded nodes.
- `shared_data` & `stage_results`: Deep copied to isolate active memory state.

## Resumption Mechanics
Calling `resume(checkpoint_id, request)` resolves the workflow DAG, ignores completed nodes present in the checkpoint, and starts execution at the first uncompleted stage. Resuming from composition complete skips heavy upstream intelligence stages entirely.
