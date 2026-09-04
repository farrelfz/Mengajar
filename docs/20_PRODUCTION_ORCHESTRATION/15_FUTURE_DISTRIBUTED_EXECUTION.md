# Future Distributed Execution

This document details abstractions preparing the control plane for future asynchronous or distributed scaling.

## Decoupled Execution Backend
To ensure we do not lock the orchestrator into local synchronous runs, the design abstracts stage execution:
- **LocalExecutionBackend (Current)**: Executes stages sequentially on the local thread.
- **AsyncExecutionBackend (Future)**: Leverages `asyncio` to execute independent DAG branches in parallel.
- **DistributedExecutionBackend (Future)**: Resolves Celery/Redis/external queue task distribution.

All contexts and checkpoints are serializable and structured, ensuring future transitions to distributed workers require no core orchestrator modifications.
