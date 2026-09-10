# Universal Document Intelligence System V5
# Phase 6 Implementation Tasks: Human-in-the-Loop Review Studio

```text
STATUS: PHASE 6 IMPLEMENTATION COMPLETE — ALL 649 TESTS PASSING
```

---

### TASK-601: Canonical Review Contracts
- **STATUS**: [x] COMPLETED
- **OBJECTIVE**: Create frozen Pydantic contracts for review cases, expert decisions, finding adjudications, repair directives, and reviewer metadata.
- **DELIVERED**: `app/review/contracts/` (`enums.py`, `review_case.py`, `review_decision.py`, `directives.py`, `evidence.py`, `reviewer.py`).
- **TESTS**: 6/6 passed in `tests/unit/review/test_review_contracts.py`.

---

### TASK-602: Review Intake & Priority Queue Registry
- **STATUS**: [x] COMPLETED
- **OBJECTIVE**: Build intake adapter with reviewability classification, priority scoring model, and file-backed atomic queue registry.
- **DELIVERED**: `app/review/intake/` (`reviewability.py`, `intake_router.py`), `app/review/queue/` (`intelligence.py`, `leasing.py`, `expertise_router.py`, `registry.py`).
- **TESTS**: 5/5 passed in `tests/unit/review/test_review_intake_and_queue.py`.

---

### TASK-603: Unified Evidence & Lineage Adapter
- **STATUS**: [x] COMPLETED
- **OBJECTIVE**: Extract and aggregate render previews, DOM geometry, claim-to-source traceability links, and repair transaction histories into a review bundle.
- **DELIVERED**: `app/review/evidence/` (`sufficiency.py`, `lineage_adapter.py`, `artifact_snapshot.py`, `evidence_package.py`).
- **TESTS**: 3/3 passed in `tests/unit/review/test_review_evidence_adapter.py`.

---

### TASK-604: Structured Review Decision Engine
- **STATUS**: [x] COMPLETED
- **OBJECTIVE**: Implement domain engine that validates and records structured expert determinations (confirming defects, disputing false positives, updating root cause hypotheses).
- **DELIVERED**: `app/review/decisions/` (`confidence.py`, `counterfactuals.py`, `review_engine.py`).
- **TESTS**: Integrated in review contracts and e2e suites.

---

### TASK-605: Directive Safety Gateway
- **STATUS**: [x] COMPLETED
- **OBJECTIVE**: Implement safety firewall enforcing hard constraints on human repair directives (blocking force-export, citation fabrication, answer key disclosure).
- **DELIVERED**: `app/review/safety/` (`directive_safety_validator.py`, `authority_boundary_guard.py`, `exceptions.py`), `app/review/directives/` (`ontology.py`).
- **TESTS**: 8/8 passed in `tests/unit/review/test_directive_safety_gateway.py`.

---

### TASK-606: Multi-Reviewer Disagreement & Adjudication Engine
- **STATUS**: [x] COMPLETED
- **OBJECTIVE**: Calculate inter-annotator agreement across concurrent reviews and route contentious cases to senior adjudication.
- **DELIVERED**: `app/review/governance/` (`disagreement.py`, `adjudication.py`).
- **TESTS**: 4/4 passed in `tests/unit/review/test_disagreement_and_adjudication.py`.

---

### TASK-607: Reviewer Calibration & Bias Tracking
- **STATUS**: [x] COMPLETED
- **OBJECTIVE**: Evaluate reviewer reliability, precision, recall, and leniency/harshness biases by interleaving blind golden cases.
- **DELIVERED**: `app/review/governance/calibration.py`.
- **TESTS**: Verified in calibration unit tests.

---

### TASK-608: Cryptographic Review Provenance Ledger
- **STATUS**: [x] COMPLETED
- **OBJECTIVE**: Maintain an immutable, append-only ledger of all review actions, decisions, and signatures linked to artifact digests.
- **DELIVERED**: `app/review/provenance/` (`hash_chain.py`, `immutable_ledger.py`).
- **TESTS**: 2/2 passed in `tests/unit/review/test_review_provenance_and_bridges.py`.

---

### TASK-609: Safe RepairEngine Integration Bridge
- **STATUS**: [x] COMPLETED
- **OBJECTIVE**: Bridge validated repair directives to `MinimalInterventionRepairPlanner` with correct escalation layers and scopes.
- **DELIVERED**: `app/review/bridge/repair_bridge.py`.
- **TESTS**: Verified with layer and scope mappings.

---

### TASK-610: Benchmark Governance Proposal Flow
- **STATUS**: [x] COMPLETED
- **OBJECTIVE**: Permit human reviewers to nominate edge cases and unhandled failures to the Golden Corpus via `AntiLaunderingGuard`.
- **DELIVERED**: `app/review/bridge/benchmark_bridge.py`.
- **TESTS**: Verified anti-laundering baseline lowering block.

---

### TASK-611: Adversarial Review Safety Validation
- **STATUS**: [x] COMPLETED
- **OBJECTIVE**: Execute an adversarial test suite evaluating the system against all known human-in-the-loop attack vectors (Scenarios A through T).
- **DELIVERED**: `tests/unit/review/test_adversarial_review_safety.py`.
- **TESTS**: 20/20 passed.

---

### TASK-612: End-to-End Review Lifecycle Integration Benchmark
- **STATUS**: [x] COMPLETED
- **OBJECTIVE**: Comprehensive end-to-end integration benchmark validating the full review lifecycle across all 4 artifact types using real repository fixtures.
- **DELIVERED**: `tests/integration/review/test_end_to_end_review_lifecycle.py`, `app/review/cli.py`, `app/review/static_bundle.py`.
- **TESTS**: 4/4 passed across Presentation, Handout, Worksheet, and Scientific Document.

---

# Phase 7 Tasks: Production UX & Dashboard Integration

```text
STATUS: PHASE 7.0 FORENSIC AUDIT COMPLETE — AWAITING IMPLEMENTATION APPROVAL
```

---

### TASK-701: Job Read Model Writer
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Implement `JobReadModelWriter` — a non-authority serialization adapter that writes pipeline terminal state to job-scoped JSON files at terminal state transitions.
- **INPUT**: `ArtifactProductionContext` at terminal state (EXPORTED, MANUAL_REVIEW_REQUIRED, BLOCKED, FAILED)
- **OUTPUT**: `outputs/web_runs/{job_id}/` with `job_manifest.json`, `quality_report.json`, `state_timeline.json`, `repair_history.json`, `convergence.json`, `convergence_failure.md`
- **INVARIANTS**: Must be called only at terminal states; must not mutate any authority object; must not block pipeline execution; JSON output must be deterministically serializable
- **DEPENDENCIES**: `ArtifactProductionContext`, `UnifiedQualityReport`, `RepairTransactionRecord`, `StateTransitionRecord`, `ConvergenceFailureReporter`
- **TESTS**: `tests/unit/web/test_job_read_model_writer.py` — 6 tests covering each terminal state
- **STOP CONDITION**: All 6 read model files written correctly at each of the 4 terminal states

---

### TASK-702: Job Read Model API Endpoints
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Add 4 new HTTP endpoints to `app/web/server.py` serving read model data from the filesystem.
- **INPUT**: `{job_id}` path parameter; filesystem read model files
- **OUTPUT**: JSON responses from `quality_report.json`, `repair_history.json`, `state_timeline.json`, `convergence.json`
- **INVARIANTS**: 404 if read model not yet written; 200 with JSON if terminal; 202 if still running; no authority object construction in endpoints
- **DEPENDENCIES**: TASK-701 (read model files must exist)
- **TESTS**: `tests/unit/web/test_job_read_model_api.py` — 8 tests
- **STOP CONDITION**: All 4 endpoints pass unit tests with mock read model fixture files

---

### TASK-703: Pipeline Stage Stepper UI
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Replace simple percent bar with 10-stage pipeline stepper using `PIPELINE_STAGES` definitions from `stage_registry.py`.
- **INPUT**: SSE `task_start` and `task_done` events with `stage_number` and `total_stages`
- **OUTPUT**: Visual 10-stage stepper in `app/web/static/` (HTML, CSS, JS)
- **INVARIANTS**: Stage numbers must match `PIPELINE_STAGES` exactly; no invented stages; stepper must update in real-time from SSE stream
- **DEPENDENCIES**: Existing SSE stream from `GET /api/jobs/{id}/stream`
- **TESTS**: Unit test for stage number → stage name mapping completeness (all 10 stages)
- **STOP CONDITION**: All 10 stages display with correct names from `PIPELINE_STAGES` during live generation

---

### TASK-704: State Machine Badge & Timeline UI
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Display exact `ProductionState` value as color-coded badge + clickable state transition timeline.
- **INPUT**: `GET /api/jobs/{id}/state-timeline` (from TASK-702)
- **OUTPUT**: State badge + timeline in job detail panel
- **INVARIANTS**: All 21 `ProductionState` values must be mapped to UI category and color (audit Section D.2); dashboard must never call `.transition()`
- **DEPENDENCIES**: TASK-702
- **TESTS**: Unit test for all 21 state values → color category mapping completeness
- **STOP CONDITION**: All 21 states render in correct color; transition timeline shows timestamps

---

### TASK-705: Quality Report Panel
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Display `UnifiedQualityReport` as decision badge + score gauge + domain score chart + findings table + blockers list.
- **INPUT**: `GET /api/jobs/{id}/quality-report` (from TASK-702)
- **OUTPUT**: Quality panel in job detail view
- **INVARIANTS**: Decision badge is NOT interactive; score values are display-only; findings table is read-only; hard blockers shown prominently; no quality re-computation from UI
- **DEPENDENCIES**: TASK-702
- **TESTS**: Unit test for all 4 `ExportDecision` values → badge color mapping; findings pagination above 200 entries
- **STOP CONDITION**: Quality panel renders for all 4 decision outcomes; domain scores display as chart

---

### TASK-706: Repair History & Convergence Panel
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Display per-iteration repair history table + quality score trajectory line chart + convergence outcome display.
- **INPUT**: `GET /api/jobs/{id}/repair-history` + `GET /api/jobs/{id}/convergence`
- **OUTPUT**: Repair panel in job detail view
- **INVARIANTS**: Score trajectory uses Chart.js (CDN); convergence outcome labels match `ProductionConvergenceOutcome` enum values; no re-invocation of repair planner
- **DEPENDENCIES**: TASK-702
- **TESTS**: Unit test for all `ProductionConvergenceOutcome` values → human-readable label mapping
- **STOP CONDITION**: Repair table and score chart render correctly for a multi-iteration job

---

### TASK-707: Convergence Failure Viewer
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Render `convergence_failure.md` (all 13 sections) inline in dashboard for BLOCKED and MANUAL_REVIEW_REQUIRED jobs.
- **INPUT**: `GET /api/jobs/{id}/convergence` → `convergence_failure_md` field
- **OUTPUT**: Inline Markdown-rendered report in job detail view
- **INVARIANTS**: All 13 sections must render; no section may be hidden; report is read-only; viewer appears only for blocked/manual-review terminal states
- **DEPENDENCIES**: TASK-702, TASK-701 (convergence_failure.md must be written)
- **TESTS**: Visual test with synthetic 13-section Markdown fixture
- **STOP CONDITION**: All 13 sections render correctly for a BLOCKED job

---

### TASK-708: Review Queue Panel
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Display the live review queue with case list, priority scores, and evidence download links; add `/api/review/cases` and `/api/review/cases/{id}` endpoints.
- **INPUT**: `ReviewQueueRegistry` (read-only); `StaticReviewBundleGenerator` (server-side generation)
- **OUTPUT**: Review queue panel; new API endpoints
- **INVARIANTS**: Dashboard cannot create, modify, or close review cases; evidence bundle generated server-side; queue reflects registry state at poll time
- **DEPENDENCIES**: `app/review/queue/registry.py`, `app/review/static_bundle.py` (Phase 6)
- **TESTS**: `tests/unit/web/test_review_queue_api.py` — 5 tests
- **STOP CONDITION**: Review queue panel lists MANUAL_REVIEW_REQUIRED cases with priority, age, and evidence download

---

### TASK-709: Benchmark Command Center
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Display Golden Corpus summary, certification status, and regression alerts; add `/api/benchmarks/corpus` and `/api/benchmarks/certification` endpoints.
- **INPUT**: `GoldenCorpusRegistry`, `BenchmarkReport` (read-only)
- **OUTPUT**: Benchmarks panel; new API endpoints
- **INVARIANTS**: Cannot modify corpus from dashboard; regression alerts have no "dismiss" button; run trigger delegates to CLI subprocess only
- **DEPENDENCIES**: `app/benchmarking/golden_registry.py`, `app/benchmarking/reports.py` (Phase 5)
- **TESTS**: `tests/unit/web/test_benchmark_api.py` — 5 tests
- **STOP CONDITION**: Benchmark panel shows corpus size, certification status (all 4 artifact types), and regression alerts

---

### TASK-710: Artifact Library Enhancement
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Add filter by artifact type, quality decision, terminal state, and date range to the document library.
- **INPUT**: `outputs/web_runs/*/job_manifest.json` (filesystem scan); existing `GET /api/documents`
- **OUTPUT**: Enhanced library API and UI with filter controls
- **INVARIANTS**: Read-only; no file modification; no quality re-computation; filter logic server-side only
- **DEPENDENCIES**: TASK-701 (job_manifest.json files must exist)
- **TESTS**: Unit test for filter logic with mock manifests — 6 tests
- **STOP CONDITION**: Library correctly filters by artifact type and quality decision


---

# Phase 7.1 Tasks: Persistent Job Read Model Foundation

```text
STATUS: PHASE 7.1 FORENSIC AUDIT COMPLETE — AWAITING IMPLEMENTATION APPROVAL
```

---

### TASK-711: Canonical Read Model Contracts
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Create frozen Pydantic contracts defining JobReadModel, JobSnapshot, and domain-specific projection models.
- **INPUT**: Epistemic observation requirements from UQA, ProductionStateMachine, and RepairEngine
- **OUTPUT**: `app/dashboard/contracts/` (`projections.py`, `snapshots.py`, `references.py`, `enums.py`, `__init__.py`)
- **INVARIANTS**: All contracts must be frozen (`ConfigDict(frozen=True)`); schema_version must be explicit; summary separated from references; zero quality calculation formulas
- **DEPENDENCIES**: None (foundation)
- **TESTS**: `tests/unit/dashboard/test_job_read_model_contracts.py`
- **STOP CONDITION**: 100% type annotations, successful serialization/deserialization across all 4 artifact types.

---

### TASK-712: Job Identity & Snapshot Modeling
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Implement canonical identity projection distinguishing job ID, artifact ID, benchmark case ID, and review case ID.
- **INPUT**: `JobIdentityProjection` specification
- **OUTPUT**: Identity models and snapshot sequence generators
- **INVARIANTS**: No ambiguity between job, artifact, benchmark, and review identities; snapshot sequences are strictly monotonic (`000001`, `000002`, ...)
- **DEPENDENCIES**: TASK-711
- **TESTS**: Integrated in `test_job_read_model_contracts.py`
- **STOP CONDITION**: Canonical identities generated without collision across all contexts.

---

### TASK-713: Atomic Job Snapshot Writer
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Implement `AtomicJobSnapshotWriter` ensuring crash-resilient writes via POSIX `os.replace`.
- **INPUT**: Valid `JobSnapshot` object, target job directory
- **OUTPUT**: `app/dashboard/persistence/writer.py`
- **INVARIANTS**: Writes to `.tmp_<uuid>` in target directory; flushes and fsyncs; computes SHA-256; atomic rename to `snapshot_{seq:06d}.json`; atomic update of `latest.json` pointer; readers never see partial JSON
- **DEPENDENCIES**: TASK-711, TASK-712
- **TESTS**: `tests/unit/dashboard/test_atomic_snapshot_writer.py`
- **STOP CONDITION**: Concurrent reads and simulated interrupted writes leave existing snapshots undamaged.

---

### TASK-714: Read Model Projection Builder
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Implement `JobReadModelProjector` extracting signals from `ArtifactProductionContext` and domain reports without recalculating.
- **INPUT**: `ArtifactProductionContext`, `UnifiedQualityReport`, `RepairTransactionRecord`
- **OUTPUT**: `app/dashboard/projector/projector.py`
- **INVARIANTS**: READ MODEL NEVER CALCULATES QUALITY; exact scores and findings copied verbatim; no domain state mutations
- **DEPENDENCIES**: TASK-711
- **TESTS**: `tests/unit/dashboard/test_job_read_model_projector.py`
- **STOP CONDITION**: Projections match authoritative inputs with 100% numeric and categorical parity.

---

### TASK-715: Source Reference & Large Artifact Modeling
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Implement `SourceReference` modeling to link large files (PDF, HTML, images, raw manifests) by path and SHA-256 without binary embedding.
- **INPUT**: Render artifacts, forensics files, manifests
- **OUTPUT**: `app/dashboard/projector/references.py`
- **INVARIANTS**: Large artifacts are referenced, never duplicated; paths must resolve to valid filesystem locations or explicit missing status
- **DEPENDENCIES**: TASK-711, TASK-714
- **TESTS**: Reference integrity checks in snapshot tests
- **STOP CONDITION**: Snapshots remain < 100 KB regardless of multi-megabyte PDF artifact sizes.

---

### TASK-716: Job Read Model Registry
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Implement `JobReadModelRegistry` providing indexing, retrieval, and state filtering over `artifacts/read_models/jobs/`.
- **INPUT**: Persistent directory tree
- **OUTPUT**: `app/dashboard/registry/registry.py`
- **INVARIANTS**: Pure file-backed registry; no database; registry state can be completely rebuilt from disk snapshots if cache is lost
- **DEPENDENCIES**: TASK-713, TASK-714
- **TESTS**: `tests/unit/dashboard/test_read_model_registry.py`
- **STOP CONDITION**: Listing, filtering (by state, type, review requirement), and retrieval pass 100%.

---

### TASK-717: Staleness & Consistency Detectors
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Implement `ReadModelStalenessDetector` and `SnapshotConsistencyContract` to identify outdated snapshots or cross-iteration desynchronizations.
- **INPUT**: `JobSnapshot`, current disk artifacts, production context
- **OUTPUT**: `app/dashboard/governance/staleness.py`, `app/dashboard/governance/consistency.py`
- **INVARIANTS**: Explicit states: FRESH, STALE, PARTIALLY_STALE, CORRUPTED, UNKNOWN; CONSISTENT, CROSS_ITERATION; no silent failure
- **DEPENDENCIES**: TASK-711, TASK-714
- **TESTS**: `tests/unit/dashboard/test_staleness_detector.py`, `tests/unit/dashboard/test_snapshot_consistency.py`
- **STOP CONDITION**: All synthetic staleness and inconsistency scenarios detected deterministically.

---

### TASK-718: Job Read Model Rebuilder
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Implement `JobReadModelRebuilder` to rebuild snapshots and registry index from authoritative production artifacts.
- **INPUT**: `outputs/production_orchestration/{job_id}/` or `artifacts/read_models/jobs/{job_id}/snapshots/`
- **OUTPUT**: `app/dashboard/rebuilder/rebuilder.py`
- **INVARIANTS**: Zero LLM invocations; zero quality re-computations; rebuild produces identical latest.json and registry index
- **DEPENDENCIES**: TASK-713, TASK-714, TASK-716
- **TESTS**: `tests/unit/dashboard/test_read_model_rebuilder.py`
- **STOP CONDITION**: Deleting `latest.json` and registry index recovers identical state via rebuild.

---

### TASK-719: Production Observation Adapter & Failure Isolation
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Build `ProductionObservationAdapter` hooking production pipeline milestones with strict failure isolation.
- **INPUT**: Orchestrator lifecycle progression
- **OUTPUT**: `app/dashboard/adapter/observation_adapter.py`
- **INVARIANTS**: Observation failure produces `OBSERVABILITY_PROJECTION_WRITE_FAILED` but MUST NOT cause production pipeline failure; zero quality authority bypass
- **DEPENDENCIES**: TASK-713, TASK-714
- **TESTS**: `tests/unit/dashboard/test_read_model_adversarial.py` (Scenarios C & O)
- **STOP CONDITION**: Production completes successfully even when projection persistence raises disk I/O errors.

---

### TASK-720: CLI Inspection Harness & Adversarial Validation
- **STATUS**: [ ] PENDING
- **OBJECTIVE**: Implement CLI inspection commands (`inspect-job`, `list-jobs`, `verify-job-snapshot`, `rebuild-job-read-model`) and execute complete adversarial test suite.
- **INPUT**: Persistent snapshots, registry
- **OUTPUT**: `app/dashboard/cli.py`, `tests/unit/dashboard/test_read_model_adversarial.py`
- **INVARIANTS**: CLI is query-only; all 15 adversarial scenarios (A through O) pass without invariant breaches
- **DEPENDENCIES**: TASK-711 through TASK-719
- **TESTS**: `tests/unit/dashboard/test_read_model_adversarial.py`, `tests/integration/dashboard/test_production_read_model_projection.py`
- **STOP CONDITION**: 100% pass across all unit and integration tests; zero regressions on existing 649 tests.
