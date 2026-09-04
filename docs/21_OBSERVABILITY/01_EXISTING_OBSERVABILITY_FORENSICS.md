# Existing Observability Forensics

## 1. Current Runtime Visibility & Logging
- **Structured Logging**: The system uses `structlog` via `app/core/logging.py`, leveraging contextvars (`structlog.contextvars.merge_contextvars`) to bind context. Loggers are bound to modules and record events (e.g. `agent.content_intelligence.start`).
- **Timing and Performance Telemetry**: Stage executions in `app/orchestration/stages/base.py` capture duration measurements in milliseconds using `time.perf_counter()`.
- **Manifests & Reports**: The benchmark runner generates `outputs/production_orchestration_benchmark/benchmark_report.json`, capturing scenarios, profiles, executed stages, durations, retry counts, checkpoint counts, final states, and artifact counts.

## 2. Identified Blind Spots and Telemetry Gaps
- **Lack of Standardized Span/Trace Hierarchy**: While the orchestrator logs high-level stages, there is no nested, parent-child span representation tracking sub-operations (e.g., capability select latency inside composition, knowledge retrieval latency inside grounding, SVG generation inside rendering).
- **Correlation ID Gaps**: There is no dedicated `trace_id` or `span_id` propagating context variables automatically without passing variables through nested components.
- **Lineage Tracking**: Generated artifacts (blueprint JSON, composition schema, HTML, output PDF) lack a centralized graph describing which request parameters, seeds, or external source retrieval sets produced them.
- **Performance Diagnostics**: There is no centralized bottleneck analyzer showing the percentage of runtime spent in specific components (e.g., rendering vs. LLM calls) or alerting on slow operation thresholds.
- **Failure Cause Lineage**: When exceptions occur, stack trace dumps go to the console/sys.stderr, but the orchestrator does not structure them into a causal failure tree containing partial outputs, context snapshots, and recoverability.
