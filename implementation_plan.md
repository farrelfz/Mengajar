# Universal Document Intelligence System V5
# Phase 6 Implementation Plan: Human-in-the-Loop Review Studio & Expert Decision Governance

## Overview
Phase 6 establishes an authoritative, strictly bounded, and calibrated Human-in-the-Loop Review Studio. It bridges Level-0 automated quality enforcement with human expert judgment without sacrificing mathematical invariants, benchmark integrity, or automated export safeguards.

---

### PHASE 6 [COMPLETED].1: Canonical Review Contracts
- **Objective**: Define immutable, frozen Pydantic contracts governing review cases, expert decisions, finding adjudications, repair directives, and reviewer metadata.
- **Files Expected to be Created**:
  - `app/review/contracts/cases.py`
  - `app/review/contracts/decisions.py`
  - `app/review/contracts/directives.py`
  - `app/review/contracts/reviewer.py`
  - `app/review/contracts/__init__.py`
- **Existing Files to Integrate With**:
  - `app/quality/contracts/findings.py` (`QualityFinding`)
  - `app/quality/contracts/decisions.py` (`ExportDecision`)
  - `app/quality/contracts/signals.py` (`SignalSeverity`, `QualityDomain`)
- **Authority Boundary**: Read-only consumption of quality finding and signal contracts. Zero mutation of Level-0 quality types.
- **Invariants**: Contracts must be frozen, serializable to deterministic JSON, and reject unspecified/unknown fields.
- **Tests**: `tests/unit/review/test_review_contracts.py` (schema validation, immutability, roundtrip JSON serialization).
- **Backward Compatibility Risks**: Zero. New package `app/review/`.
- **Stop Condition**: All unit tests pass; 100% type annotations complete.

---

### PHASE 6 [COMPLETED].2: Review Intake & Queue Intelligence
- **Objective**: Implement automatic discovery and ingestion of review cases from production failures, convergence reports, benchmark regressions, and invariant rejections, with a multi-factor priority queue.
- **Files Expected to be Created**:
  - `app/review/queue/intake_adapter.py`
  - `app/review/queue/priority_model.py`
  - `app/review/queue/queue_registry.py`
  - `app/review/queue/state_machine.py` (`ReviewStateMachine`)
  - `app/review/queue/__init__.py`
- **Existing Files to Integrate With**:
  - `app/orchestration/production_context.py` (`ArtifactProductionContext`)
  - `app/orchestration/failure_reporter.py` (`ConvergenceFailureReporter`)
  - `app/benchmarking/golden_contracts.py` (`BenchmarkEvaluation`, `CertificationDecision`)
- **Authority Boundary**: Listens to terminal states (`MANUAL_REVIEW_REQUIRED`, `BLOCKED`) without mutating `ProductionStateMachine`.
- **Invariants**: Queue state transitions must be logged; priority scoring must be deterministic; expired case leases must release cleanly.
- **Tests**: `tests/unit/review/test_review_intake_and_queue.py` (priority calculation, case ingestion, timeout recovery, lease management).
- **Backward Compatibility Risks**: Zero pipeline interruption.
- **Stop Condition**: Queue ingestion passes unit tests across all 4 trigger types.

---

### PHASE 6 [COMPLETED].3: Evidence & Artifact Lineage Adapter
- **Objective**: Create unified evidence and lineage extraction that synthesizes render snapshots, geometry bounding boxes, claim-to-source traceability links, and repair transaction histories into a review packet.
- **Files Expected to be Created**:
  - `app/review/evidence/evidence_adapter.py`
  - `app/review/evidence/lineage_adapter.py`
  - `app/review/evidence/bundle_exporter.py`
  - `app/review/evidence/__init__.py`
- **Existing Files to Integrate With**:
  - `app/quality/contracts/provenance.py` (`QualityProvenanceGraph`)
  - `app/intelligence/transformation/traceability.py` (`TransformationTraceabilityEngine`)
  - `app/quality/repair/transaction.py` (`RepairTransactionRecord`)
- **Authority Boundary**: Pure read-only aggregation. Never modifies underlying evidence or hashes.
- **Invariants**: All evidence references must resolve to valid source files or verifiable cryptographic hashes.
- **Tests**: `tests/unit/review/test_review_evidence_adapter.py` (evidence packaging, missing file handling, bounding box resolution).
- **Backward Compatibility Risks**: None.
- **Stop Condition**: Complete evidence bundle generated from mock and real production contexts.

---

### PHASE 6 [COMPLETED].4: Structured Review Decision Engine
- **Objective**: Implement the domain engine that accepts, validates, and records structured expert determinations (confirming defects, disputing false positives, updating causal attributions, or requesting repairs).
- **Files Expected to be Created**:
  - `app/review/decisions/decision_engine.py`
  - `app/review/decisions/decision_validator.py`
  - `app/review/decisions/__init__.py`
- **Existing Files to Integrate With**:
  - `app/review/contracts/decisions.py`
  - `app/quality/causal/cause_catalog.py`
- **Authority Boundary**: Validates semantic completeness of human rationale and constraints; does not execute repairs directly.
- **Invariants**: Decisions require non-empty rationale (min 20 characters); decision timestamps and reviewer signatures must be present.
- **Tests**: `tests/unit/review/test_review_decision_engine.py` (decision validation, invalid rationale rejection, duplicate prevention).
- **Backward Compatibility Risks**: None.
- **Stop Condition**: Decision engine rejects invalid/malformed decisions deterministically.

---

### PHASE 6 [COMPLETED].5: Directive Safety Gateway
- **Objective**: Build the cryptographic and invariant safety firewall that inspects human repair directives and halts unsafe operations (force export, citation synthesis, anti-spoiling violations).
- **Files Expected to be Created**:
  - `app/review/safety/directive_validator.py`
  - `app/review/safety/safety_rules.py`
  - `app/review/safety/exceptions.py`
  - `app/review/safety/__init__.py`
- **Existing Files to Integrate With**:
  - `app/quality/repair/safety_invariants.py` (`RepairSafetyInvariants`)
  - `app/orchestration/escalation_router.py` (`RepairEscalationRouter`, `RepairEscalationLayer`)
- **Authority Boundary**: Hard gate. Operates as an impassable barrier between human desires and repair actuators.
- **Invariants**: Hard blockers: `force_export=True` rejected; ungrounded citations rejected; answer disclosure rejected; baseline lowering rejected.
- **Tests**: `tests/unit/review/test_directive_safety_gateway.py` (adversarial rejection tests across all forbidden directive categories).
- **Backward Compatibility Risks**: None.
- **Stop Condition**: 100% of adversarial unsafe directives are rejected with explicit `IllegalDirectiveException`.

---

### PHASE 6 [COMPLETED].6: Disagreement & Adjudication Engine
- **Objective**: Implement multi-reviewer consensus evaluation, inter-annotator agreement metrics (Cohen/Fleiss Kappa), and senior adjudication workflows for high-stakes conflicts.
- **Files Expected to be Created**:
  - `app/review/governance/disagreement_analyzer.py`
  - `app/review/governance/adjudication_manager.py`
  - `app/review/governance/__init__.py`
- **Existing Files to Integrate With**:
  - `app/review/contracts/decisions.py`
  - `app/review/queue/state_machine.py`
- **Authority Boundary**: Resolves human-to-human divergence; never overrides Level-0 automated rules.
- **Invariants**: If consensus score $< 0.80$ or if any reviewer flags a safety blocker, state must transition to `ADJUDICATION_REQUIRED`.
- **Tests**: `tests/unit/review/test_disagreement_and_adjudication.py` (consensus scoring, variance detection, adjudication resolution).
- **Backward Compatibility Risks**: None.
- **Stop Condition**: Consensus and disagreement calculations match mathematical ground truth across synthetic test cases.

---

### PHASE 6 [COMPLETED].7: Reviewer Calibration
- **Objective**: Provide empirical calibration and bias tracking by seeding blind golden cases and measuring reviewer precision, recall, and leniency/harshness indices.
- **Files Expected to be Created**:
  - `app/review/governance/reviewer_calibration.py`
  - `app/review/governance/calibration_registry.py`
- **Existing Files to Integrate With**:
  - `app/benchmarking/golden_registry.py` (`GoldenCorpusRegistry`)
  - `app/benchmarking/golden_contracts.py` (`GoldenArtifactReference`)
- **Authority Boundary**: Evaluates reviewer performance against static golden ground truth.
- **Invariants**: Reviewers with calibration $< 0.85$ are barred from single-approver and senior adjudication privileges.
- **Tests**: `tests/unit/review/test_reviewer_calibration.py` (blind test evaluation, leniency bias detection, gating enforcement).
- **Backward Compatibility Risks**: None.
- **Stop Condition**: Calibration engine correctly detects biased and fatigue-simulated reviewer submissions.

---

### PHASE 6 [COMPLETED].8: Review Provenance & Immutable Ledger
- **Objective**: Implement the tamper-evident, append-only review ledger that cryptographically binds review cases, decisions, evidence IDs, and reviewer signatures to the artifact SHA-256 hash.
- **Files Expected to be Created**:
  - `app/review/provenance/review_ledger.py`
  - `app/review/provenance/signature_guard.py`
  - `app/review/provenance/__init__.py`
- **Existing Files to Integrate With**:
  - `app/quality/contracts/provenance.py` (`QualityProvenanceGraph`)
- **Authority Boundary**: Write-once, read-many cryptographic ledger.
- **Invariants**: Past records are immutable; hash chain verifies ledger continuity; corrupted records trigger integrity alerts.
- **Tests**: `tests/unit/review/test_review_provenance.py` (record commitment, hash verification, tamper detection).
- **Backward Compatibility Risks**: None.
- **Stop Condition**: Ledger passes cryptographic audit and tamper-injection tests.

---

### PHASE 6 [COMPLETED].9: RepairEngine Integration Boundary
- **Objective**: Safely bridge approved review directives to `MinimalInterventionRepairPlanner` and `RepairTransactionManager`, spawning governed replay iterations without modifying production state machines illegally.
- **Files Expected to be Created**:
  - `app/review/bridge/repair_bridge.py`
  - `app/review/bridge/replay_coordinator.py`
  - `app/review/bridge/__init__.py`
- **Existing Files to Integrate With**:
  - `app/quality/repair/transaction.py` (`RepairTransactionManager`)
  - `app/quality/repair/planner.py` (`MinimalInterventionRepairPlanner`)
  - `app/orchestration/production_orchestrator.py` (`ProductionOrchestrator`)
- **Authority Boundary**: Human directives become constrained input parameters to repair planners; all repair results are subject to normal `RepairSafetyInvariants`.
- **Invariants**: Directives can only target approved layers (R0-R5); mutations must undergo standard UQA re-evaluation before export.
- **Tests**: `tests/unit/review/test_review_repair_bridge.py` (directive-to-plan translation, safe replay execution, rollback upon failure).
- **Backward Compatibility Risks**: Production orchestrator behavior must remain 100% backward compatible when called autonomously.
- **Stop Condition**: Directive successfully guides repair actuator in test scenario with full drift and invariant checks passing.

---

### PHASE 6 [COMPLETED].10: Benchmark Governance Proposal Flow
- **Objective**: Allow reviewers to nominate inspected edge cases and failure modes as Golden Corpus candidates through the `AntiLaunderingGuard`.
- **Files Expected to be Created**:
  - `app/review/governance/benchmark_proposer.py`
  - `app/review/governance/proposal_contracts.py`
- **Existing Files to Integrate With**:
  - `app/benchmarking/governance.py` (`AntiLaunderingGuard`, `BaselineMutationRecord`)
  - `app/benchmarking/golden_registry.py` (`GoldenCorpusRegistry`, `GoldenCorpusVersionManager`)
- **Authority Boundary**: Submits proposals to Golden Corpus governance; cannot directly mutate `golden_corpus/manifest.json`.
- **Invariants**: Baseline scores cannot be lowered; change classifications must be `CORPUS_EXPANSION` or `LEGITIMATE_CORRECTION`.
- **Tests**: `tests/unit/review/test_review_benchmark_proposer.py` (candidate submission, anti-laundering gate verification, version increment).
- **Backward Compatibility Risks**: None.
- **Stop Condition**: Golden candidate successfully proposed and validated by AntiLaunderingGuard.

---

### PHASE 6 [COMPLETED].11: Adversarial Safety Validation
- **Objective**: Comprehensive adversarial test suite targeting human review vulnerabilities (force export exploits, forged reviewer signatures, answer disclosures, malicious directives, corrupted ledgers).
- **Files Expected to be Created**:
  - `tests/unit/review/test_adversarial_review_safety.py`
  - `tests/fixtures/review/adversarial_directives.json`
- **Existing Files to Integrate With**:
  - All `app/review/` safety and governance modules.
- **Authority Boundary**: Adversarial validation.
- **Invariants**: Zero security bypasses; zero invariant compromises under adversarial input.
- **Tests**: At least 25 adversarial test cases.
- **Backward Compatibility Risks**: None.
- **Stop Condition**: 100% of adversarial attacks neutralized with strict exceptions.

---

### PHASE 6 [COMPLETED].12: End-to-End Review Lifecycle Benchmark
- **Objective**: End-to-end integration benchmark validating the full lifecycle: Production Failure $ightarrow$ Intake $ightarrow$ Queue Prioritization $ightarrow$ Evidence Presentation $ightarrow$ Review Decision $ightarrow$ Directive Safety Gate $ightarrow$ Governed Replay $ightarrow$ Ledger Provenance.
- **Files Expected to be Created**:
  - `tests/integration/review/test_end_to_end_review_lifecycle.py`
  - `app/review/cli.py` (developer & reviewer CLI harness)
- **Existing Files to Integrate With**:
  - Entire `app/review/`, `app/orchestration/`, `app/quality/`, `app/benchmarking/` pipeline.
- **Authority Boundary**: End-to-end orchestration validation.
- **Invariants**: The entire test suite (all existing 246 tests + new review tests) must pass with zero failures.
- **Tests**: Full lifecycle execution across all 4 canonical artifact types.
- **Backward Compatibility Risks**: Complete regression testing against baseline.
- **Stop Condition**: All integration tests pass; documentation updated; zero existing test regressions.

---

# Phase 7 Implementation Plan: Production UX & Dashboard Integration

## Overview
Phase 7 upgrades the existing localhost web dashboard from a simple job-status monitor into a comprehensive production observability and governance interface. It exposes the rich quality, repair, convergence, benchmark, and human review data generated by Phases 1–6 — all as read-only observations, never as authority-bypassing controls.

**Non-negotiable invariant**: The dashboard MUST NEVER become an authority. The UX layer is a VIEW + INTERACTION ADAPTER.

---

### PHASE 7 [PENDING].1: Job Read Model Writer
- **Objective**: Implement `JobReadModelWriter` — a non-authority adapter that serializes pipeline terminal state data to job-scoped JSON files.
- **Files Expected**:
  - `app/web/read_model.py` — `JobReadModelWriter` class
- **Files to Integrate With** (READ-ONLY):
  - `app/orchestration/production_context.py` — `ArtifactProductionContext`
  - `app/orchestration/production_state.py` — `StateTransitionRecord`
  - `app/quality/contracts/authority.py` — `UnifiedQualityReport`
  - `app/quality/repair/transaction.py` — `RepairTransactionRecord`
  - `app/orchestration/convergence_controller.py` — `ConvergenceCheckResult`
  - `app/orchestration/failure_reporter.py` — `ConvergenceFailureReporter`
- **Output Structure**: `outputs/web_runs/{job_id}/` with `job_manifest.json`, `quality_report.json`, `state_timeline.json`, `repair_history.json`, `convergence.json`, `convergence_failure.md`
- **Authority Boundary**: Pure serialization adapter. Zero authority logic. Zero state mutations.
- **Invariants**: Must serialize to deterministic JSON; must be called only at terminal states; must not block pipeline execution.
- **Tests**: `tests/unit/web/test_job_read_model_writer.py`
- **Stop Condition**: All 6 files written correctly at each of the 4 terminal states (EXPORTED, MANUAL_REVIEW_REQUIRED, BLOCKED, FAILED).

---

### PHASE 7 [PENDING].2: Job Read Model API Endpoints
- **Objective**: Add 4 new endpoints to `app/web/server.py` serving read model JSON for job lifecycle inspection.
- **Files to Modify**:
  - `app/web/server.py` — add endpoints
- **New Endpoints**:
  - `GET /api/jobs/{id}/quality-report` → `quality_report.json`
  - `GET /api/jobs/{id}/repair-history` → `repair_history.json`
  - `GET /api/jobs/{id}/state-timeline` → `state_timeline.json`
  - `GET /api/jobs/{id}/convergence` → `convergence.json` + `convergence_failure.md`
- **Authority Boundary**: All endpoints are read-only from the filesystem. No authority object construction.
- **Invariants**: 404 if read model not yet written; 200 with JSON if job terminal; 202 if job still running.
- **Tests**: `tests/unit/web/test_job_read_model_api.py`
- **Stop Condition**: All 4 endpoints pass unit tests with mock read model files.

---

### PHASE 7 [PENDING].3: Pipeline Stage Stepper UI
- **Objective**: Replace the simple percent bar with a 10-stage pipeline stepper using `PIPELINE_STAGES` definitions.
- **Files to Modify**:
  - `app/web/static/app.js` — stepper component
  - `app/web/static/app.css` — stepper styles
  - `app/web/static/index.html` — stepper mount point
- **Authority Boundary**: Pure visual rendering from SSE events. No authority calls.
- **Invariants**: Stage numbers must match `PIPELINE_STAGES` definitions exactly; must not invent stages.
- **Tests**: Browser visual test (manual) + unit test for stage mapping correctness.
- **Stop Condition**: All 10 stages display correctly with SSE progress events during a live generation run.

---

### PHASE 7 [PENDING].4: State Machine Badge UI
- **Objective**: Display the exact `ProductionState` value as a color-coded badge + state transition timeline.
- **Files to Modify**:
  - `app/web/static/app.js` — state badge + timeline component
  - `app/web/static/app.css` — state color classes
- **Data Source**: `GET /api/jobs/{id}/state-timeline`
- **Authority Boundary**: Read-only display. State categories defined by audit Section D.2.
- **Tests**: Unit test for state → color mapping completeness.
- **Stop Condition**: All 21 `ProductionState` values correctly mapped to their UI category and color.

---

### PHASE 7 [PENDING].5: Quality Report Panel
- **Objective**: Display `UnifiedQualityReport` data as visual panels: decision badge, overall score gauge, domain score chart, findings table, blockers list.
- **Files to Modify**:
  - `app/web/static/app.js` — quality panel component
  - `app/web/static/app.css` — quality panel styles
- **Data Source**: `GET /api/jobs/{id}/quality-report`
- **Authority Boundary**: Read-only display. No quality re-computation. No score editing.
- **Invariants**: Decision badge must not be interactive (no click-to-override). Hard blockers must be visually prominent. Findings table must be read-only.
- **Tests**: Unit test for decision → badge color mapping; findings table pagination above 200 entries.
- **Stop Condition**: All 4 `ExportDecision` values display correctly; domain scores render as chart; findings table paginates.

---

### PHASE 7 [PENDING].6: Repair History Panel
- **Objective**: Display per-iteration repair history as a table + score trajectory line chart + convergence outcome.
- **Files to Modify**:
  - `app/web/static/app.js` — repair panel component
- **Data Source**: `GET /api/jobs/{id}/repair-history` + `GET /api/jobs/{id}/convergence`
- **Authority Boundary**: Read-only display of repair records. No re-invocation of repair planner.
- **Invariants**: Repair history must show mutation scope per iteration; score trajectory must use Chart.js (CDN); convergence outcome must match `ProductionConvergenceOutcome` enum values exactly.
- **Tests**: Visual test + unit test for convergence outcome → human-readable label mapping.
- **Stop Condition**: Repair history table renders for multi-iteration jobs; score trajectory chart displays correctly.

---

### PHASE 7 [PENDING].7: Convergence Failure Viewer
- **Objective**: Render `convergence_failure.md` (13-section Markdown) inline in the dashboard for BLOCKED and MANUAL_REVIEW_REQUIRED jobs.
- **Files to Modify**:
  - `app/web/static/app.js` — Markdown renderer (using CDN marked.js or showdown.js)
- **Data Source**: `GET /api/jobs/{id}/convergence` → `convergence_failure.md` content
- **Authority Boundary**: Read-only render. No editing. No re-generation from dashboard.
- **Invariants**: All 13 sections must render; must display prominently for blocked states; must not hide any section.
- **Tests**: Visual test with synthetic 13-section Markdown fixture.
- **Stop Condition**: All 13 sections render correctly for a blocked job.

---

### PHASE 7 [PENDING].8: Review Queue Panel
- **Objective**: Display the live review queue from `ReviewQueueRegistry` with case list, priority scores, and evidence download links.
- **Files to Modify**:
  - `app/web/server.py` — add `/api/review/cases` and `/api/review/cases/{id}` endpoints
  - `app/web/static/app.js` — review queue panel
- **Files to Integrate With** (READ-ONLY):
  - `app/review/queue/registry.py` — `ReviewQueueRegistry`
  - `app/review/static_bundle.py` — `StaticReviewBundleGenerator`
- **Authority Boundary**: Read from `ReviewQueueRegistry`; generate bundles server-side; no decision submission in Phase 7.8 (deferred to 7.9).
- **Invariants**: Must not allow dashboard to create, modify, or close review cases; queue display must reflect registry state at poll time.
- **Tests**: `tests/unit/web/test_review_queue_api.py`
- **Stop Condition**: Review queue panel lists MANUAL_REVIEW_REQUIRED cases with priority scores and evidence download links.

---

### PHASE 7 [PENDING].9: Benchmark Command Center
- **Objective**: Display Golden Corpus summary, certification status per artifact type, and regression alerts from benchmark infrastructure.
- **Files to Modify**:
  - `app/web/server.py` — add `/api/benchmarks/corpus` and `/api/benchmarks/certification` endpoints
  - `app/web/static/app.js` — benchmarks panel
- **Files to Integrate With** (READ-ONLY):
  - `app/benchmarking/golden_registry.py` — `GoldenCorpusRegistry`
  - `app/benchmarking/reports.py` — `BenchmarkReport`
- **Authority Boundary**: Read-only corpus summary and certification reports. Run trigger delegates to CLI subprocess. CANNOT modify corpus.
- **Invariants**: Corpus count must match `GoldenCorpusRegistry` manifest; certification status must come from latest `BenchmarkReport`; regression alerts must not have "dismiss" action.
- **Tests**: `tests/unit/web/test_benchmark_api.py`
- **Stop Condition**: Benchmark panel displays corpus size, certification status, and regression status for all 4 artifact types.

---

### PHASE 7 [PENDING].10: Artifact Library Enhancement
- **Objective**: Enhance the document library with filter by artifact type, quality decision, terminal state, and date range; add quick quality score display.
- **Files to Modify**:
  - `app/web/server.py` — extend `GET /api/documents` with filter params
  - `app/web/static/app.js` — enhanced library component
- **Files to Integrate With** (READ-ONLY):
  - `outputs/web_runs/*/job_manifest.json` — read model
- **Authority Boundary**: Read-only. No file modification. No quality re-computation.
- **Tests**: Unit test for filter logic with mock manifests.
- **Stop Condition**: Library filters by artifact type and quality decision correctly.


---

# Phase 7.1 Implementation Plan: Persistent Job Read Model Foundation

## Overview
Phase 7.1 creates the persistent, deterministic, immutable, rebuildable Read Model foundation for production jobs following strict CQRS separation ("Observation Without Authority"). It provides query-only projections of authoritative production state to the filesystem without introducing databases or mutating domain authorities.

---

### PHASE 7.1 [PENDING].1: Canonical Read Model Contracts
- **Objective**: Define typed frozen Pydantic contracts for read models, snapshots, identities, projections, and source references.
- **Files to Create**:
  - `app/dashboard/contracts/projections.py`
  - `app/dashboard/contracts/snapshots.py`
  - `app/dashboard/contracts/references.py`
  - `app/dashboard/contracts/enums.py`
  - `app/dashboard/contracts/__init__.py`
- **Authority Boundary**: Read-only projection models. Zero calculation formulas.
- **Invariants**: Must distinguish summary data from reference pointers; schema_version must be explicit; frozen Pydantic models.
- **Tests**: `tests/unit/dashboard/test_job_read_model_contracts.py`
- **Stop Condition**: Contracts validate and roundtrip serialize deterministically.

---

### PHASE 7.1 [PENDING].2: Atomic Job Snapshot Writer
- **Objective**: Implement `AtomicJobSnapshotWriter` ensuring crash-resilient, atomic write operations using POSIX `os.replace`.
- **Files to Create**:
  - `app/dashboard/persistence/writer.py`
  - `app/dashboard/persistence/__init__.py`
- **Authority Boundary**: Pure I/O persistence. Never modifies domain state.
- **Invariants**: Temp file on same filesystem (`.tmp_<uuid>`); SHA-256 integrity hash; atomic rename; latest.json pointer update.
- **Tests**: `tests/unit/dashboard/test_atomic_snapshot_writer.py`
- **Stop Condition**: Writers pass atomic replacement tests and concurrent read isolation tests.

---

### PHASE 7.1 [PENDING].3: Read Model Projector & Source References
- **Objective**: Implement `JobReadModelProjector` extracting observational signals from `ArtifactProductionContext` and authoritative reports.
- **Files to Create**:
  - `app/dashboard/projector/projector.py`
  - `app/dashboard/projector/references.py`
  - `app/dashboard/projector/__init__.py`
- **Authority Boundary**: Extracts and projects authoritative results verbatim. READ MODEL NEVER CALCULATES QUALITY.
- **Invariants**: Scores copied without recalculation; large artifacts referenced via path and SHA-256; no domain mutation.
- **Tests**: `tests/unit/dashboard/test_job_read_model_projector.py`
- **Stop Condition**: Complete projection assembled from mock and real production contexts.

---

### PHASE 7.1 [PENDING].4: Job Read Model Registry
- **Objective**: Implement `JobReadModelRegistry` providing indexing, retrieval, and listing over `artifacts/read_models/jobs/`.
- **Files to Create**:
  - `app/dashboard/registry/registry.py`
  - `app/dashboard/registry/__init__.py`
- **Authority Boundary**: Filesystem-backed index. Must be 100% rebuildable from disk snapshots.
- **Invariants**: No database; in-memory cache synchronized with filesystem; thread-safe.
- **Tests**: `tests/unit/dashboard/test_read_model_registry.py`
- **Stop Condition**: Listing, filtering by state/type, and retrieval pass unit tests.

---

### PHASE 7.1 [PENDING].5: Staleness & Consistency Detectors
- **Objective**: Implement `ReadModelStalenessDetector` and `SnapshotConsistencyContract`.
- **Files to Create**:
  - `app/dashboard/governance/staleness.py`
  - `app/dashboard/governance/consistency.py`
  - `app/dashboard/governance/integrity.py`
  - `app/dashboard/governance/__init__.py`
- **Authority Boundary**: Verifies observational alignment. Exposes FRESH/STALE and CONSISTENT/CROSS_ITERATION statuses.
- **Invariants**: Detects mtime/hash drifts in referenced files; detects cross-iteration desynchronization.
- **Tests**: `tests/unit/dashboard/test_staleness_detector.py`, `tests/unit/dashboard/test_snapshot_consistency.py`, `tests/unit/dashboard/test_read_model_integrity.py`
- **Stop Condition**: Stale files and cross-iteration snapshots deterministically detected.

---

### PHASE 7.1 [PENDING].6: Job Read Model Rebuilder
- **Objective**: Implement `JobReadModelRebuilder` to reconstruct read models and registry indexes from authoritative artifacts.
- **Files to Create**:
  - `app/dashboard/rebuilder/rebuilder.py`
  - `app/dashboard/rebuilder/__init__.py`
- **Authority Boundary**: Reconstructs projections without rerunning generation, quality evaluation, or repair.
- **Invariants**: Pure read-only extraction from outputs and snapshots; zero LLM calls.
- **Tests**: `tests/unit/dashboard/test_read_model_rebuilder.py`
- **Stop Condition**: Deleting latest.json and registry index recovers identical state via rebuild.

---

### PHASE 7.1 [PENDING].7: Production Observation Adapter & Failure Isolation
- **Objective**: Build `ProductionObservationAdapter` hooking lifecycle progression without coupling production to observability persistence.
- **Files to Create**:
  - `app/dashboard/adapter/observation_adapter.py`
  - `app/dashboard/adapter/__init__.py`
- **Authority Boundary**: Failure to write read model produces `OBSERVABILITY_PROJECTION_WRITE_FAILED` but does NOT fail production.
- **Invariants**: Production success + write error = production still succeeds.
- **Tests**: `tests/unit/dashboard/test_read_model_adversarial.py`
- **Stop Condition**: Adversarial simulation confirms complete failure isolation.

---

### PHASE 7.1 [PENDING].8: CLI Inspection Harness & Phase 7.2 Boundary
- **Objective**: Implement developer/operator CLI inspection commands (`inspect-job`, `list-jobs`, `verify-job-snapshot`, `rebuild-job-read-model`).
- **Files to Create**:
  - `app/dashboard/cli.py`
  - `app/dashboard/__init__.py`
- **Authority Boundary**: Read-only query tool. No mutation capabilities.
- **Tests**: Unit tests for CLI parser and output formatting.
- **Stop Condition**: CLI inspects and verifies snapshots offline.

---

### PHASE 7.1 [PENDING].9: End-to-End Integration & Regression Verification
- **Objective**: Verify end-to-end production read model emission across all 4 artifact types and verify zero regressions on existing 649 tests.
- **Files to Create**:
  - `tests/integration/dashboard/test_production_read_model_projection.py`
  - `docs/phase_7_1_persistent_job_read_model.md`
- **Invariants**: All 649 baseline tests pass + all new dashboard unit/integration tests pass.
- **Stop Condition**: 100% green test suite.
