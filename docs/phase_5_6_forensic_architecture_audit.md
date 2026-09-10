# Phase 5 & 6 Forensic Architecture Audit

## A. Source Knowledge Entry
- Enters through `app.intelligence.pipeline` or `app.orchestration.engine.ProductionOrchestrator`, originating from parsed Markdown tree via `MarkdownTreeParser`.

## B. Knowledge Units Representation
- Managed in `app.intelligence.schemas` and `app.document.manifest`, represented as Knowledge Units tied to the `ContentManifestBuilder`.

## C. Artifact Intent Resolution
- Handled by `app.agents.document_planner.DocumentPlanner` and `app.director.policies`.

## D. Blueprint Creation
- Created in the `BLUEPRINT_GENERATION` stage (`WorkflowStageType.BLUEPRINT_GENERATION`) executed by `SlideArchitect` or specific `app.blueprints` generators.

## E. Renderer Execution
- Controlled inside `app.integration.render_execution` and `app.rendering` (using `html`, `playwright`, `reportlab` adapters).

## F. Unified Quality Authority Decisions
- Made in `app.quality.authority.UnifiedQualityAuthority` which manages 4 orthogonal truth layers. Evaluated in `PRE_RENDER_QUALITY` and `ARTIFACT_VALIDATION` workflow stages.

## G. Repair Iterations Storage
- Managed by `app.quality.repair.RepairEngine` and `app.quality.repair.actuation`. Iterations are tied to the active pipeline job state or `RepairResult`.

## H. Manual Review Case Routing
- Currently, if the `RepairEngine` exhausts its budget or if `UnifiedQualityAuthority` yields `MANUAL_REVIEW_REQUIRED`, the job stops and creates `repair_forensics.md` for manual inspection. No structured GUI backend currently exists.

## I. Benchmark Fixtures Location
- Exist mostly as test markdown files (e.g., `oobleck_experiment.md`, `hand_fire_full.md`) referenced in `tests/integration/` or `tests/unit/benchmarking/`.

## J. Quality Reports Serialization
- Quality reports are serialized as `.json` and `.md` (e.g., `presentation_quality_report.md`, `repair_safety_report.json`, `repair_safety_report.md`, `pipeline_synchronization_audit.md`) in the workspace root or output directory.

## K. Provenance Graphs Storage
- Managed in `app.intelligence.traceability` or embedded directly in the `PipelineJob` and `BlueprintProposal` structures.

## L. Iteration Structuring in ProductionVersionManager
- The state machine invalidates downstream dependencies on blueprint mutation (e.g., `BLUEPRINT (v1) -> COMPOSITION (v1) -> HTML (v1) -> PDF (v1)` bumps to `v2`).

## M. AuthorizedExportGate Approval Verification
- The pipeline requires `state.active_qa_result != None`, all blocking gates to pass (`No CRITICAL_FAILURE gates`), and the export decision must derive exclusively from the active QA result (`Export decision matches active_qa_result.round_id`).

## N. Comparison or Regression Detection Components
- `RepairConvergenceAnalyzer` detects whether scores improved or degraded between repair iterations, which can be adapted into the benchmark regression system.

## O. Components to Reuse
- `RenderedArtifactInspector` (built in Phase 4) handles PyMuPDF bounds, can be reused for visual comparison.
- `ContentManifestBuilder` handles semantic extraction, can be reused for semantic equivalence.
- `UnifiedQualityAuthority` handles quality rules, ensuring benchmark logic only evaluates regression against standard, rather than reinventing standard.
- `RepairConvergenceAnalyzer` can be extended into `RegressionDetector`.
