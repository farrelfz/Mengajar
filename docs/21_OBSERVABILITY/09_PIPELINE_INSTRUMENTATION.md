# Pipeline Instrumentation

This document details the non-invasive instrumentation strategy applied to orchestration boundaries.

## Instrumented Execution Stages
- **ProductionOrchestrator.run / resume**: Exposes the root tracing boundaries via the `observe_run` context manager.
- **Stage Execution**: Iterative execution loops in `engine.py` are wrapped in nested `observe_span` calls, logging the concrete stage adapter classes (e.g. `BlueprintGenerationStage`, `CompositionStage`) and tagging active stages.
- **Lineage Registration**: Call hooks record the creation of intermediate structures and PDFs (e.g., requests, blueprints, compositions, generated PDFs) to construct the lineage DAG.
- **Diagnostics Trapping**: Wraps all step executions, catching python exceptions and writing diagnostic failure files automatically.
- **Metrics Captures**: Custom timer context blocks record millisecond metrics for each stage automatically.
