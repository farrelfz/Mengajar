# Universal Document Intelligence System V5
# Phase 7.0 — Production UX & Dashboard Integration
# Forensic Architecture Audit

**Status**: PHASE 7.0 FORENSIC AUDIT — COMPLETE  
**Audit Date**: 2026-09-08  
**Auditor Role**: Principal Software Architect, Production Observability Engineer, UX Systems Architect  
**Hard Constraint**: This document MUST be finalized before any implementation begins.

---

## A. System Entry Points

### A.1 All Publicly Accessible Entry Points

| Entry Point | File | Interface Type | Consumer |
|---|---|---|---|
| `POST /api/generate` | `app/web/server.py:584` | HTTP REST (FastAPI) | User via Dashboard SPA |
| `GET /api/status` | `app/web/server.py:258` | HTTP REST | Dashboard status panel |
| `GET /api/models` | `app/web/server.py:281` | HTTP REST | Model selector UI |
| `POST /api/active-model` | `app/web/server.py:294` | HTTP REST | Model switcher UI |
| `POST /api/test-model` | `app/web/server.py:306` | HTTP REST | Model ping UI |
| `GET /api/benchmarks` | `app/web/server.py:323` | HTTP REST | Benchmark command center |
| `GET /api/sample-input` | `app/web/server.py:340` | HTTP REST | Sample loader |
| `GET /api/jobs/{job_id}` | `app/web/server.py:613` | HTTP REST | Job status poll |
| `GET /api/jobs/{job_id}/stream` | `app/web/server.py:633` | SSE (streaming) | Live progress stream |
| `GET /api/documents` | `app/web/server.py:688` | HTTP REST | Document library |
| `GET /api/documents/{filename}` | `app/web/server.py:709` | HTTP file serve | PDF preview & download |
| `GET /` | `app/web/server.py:738` | HTTP SPA serve | Browser root |
| `MaterialProductionPipeline` | `app/orchestration/production_pipeline.py` | Python async API | Server backend |
| `app/cli/kir_cli.py` | CLI | Terminal | Developer |
| `app/cli/mengajar_cli.py` | CLI | Terminal | Developer |
| `app/review/cli.py` | CLI | Terminal | Reviewer |

### A.2 Entry Points NOT Exposed to Dashboard

- `UnifiedQualityAuthority.evaluate_artifact()` — called exclusively by production pipeline
- `AuthorizedExportGate.verify_and_export()` — called exclusively by production orchestrator
- `ProductionStateMachine.transition()` — called exclusively within `ArtifactProductionContext`
- `RepairTransactionManager` — called exclusively by orchestrator repair loop
- `AntiLaunderingGuard` — called exclusively by benchmark governance
- `CertificationEngine` — called exclusively by benchmark runner
- `ReviewDecisionEngine` — called exclusively by CLI / review bridge

**Critical Invariant**: The dashboard's `POST /api/generate` is the ONLY permitted UI-facing generation entry point. It initiates `MaterialProductionPipeline` asynchronously via `BackgroundTasks`. All authority decisions happen downstream, invisible to the dashboard.

---

## B. Observability Surfaces

### B.1 What Observability Infrastructure Currently Exists

| Module | Path | Mechanism | Current Dashboard Exposure |
|---|---|---|---|
| `ObservabilityReport` | `app/observability/contracts.py` | In-memory, per-run | NONE |
| `active_reports` | `app/observability/tracing.py:33` | In-memory dict | NONE |
| `SpanRecord` | `app/observability/contracts.py:69` | Per-span w/ timing & status | NONE |
| `ErrorRecord` | `app/observability/contracts.py:92` | Exception + traceback | NONE |
| `ArtifactLineageRecord` | `app/observability/contracts.py:102` | Artifact-level lineage | NONE |
| `RunSummary` | `app/observability/contracts.py:114` | Aggregate per-run stats | NONE |
| `StateTransitionRecord` | `app/orchestration/production_state.py:76` | Per-state audit | NONE |
| `RepairTransactionRecord` | `app/quality/repair/transaction.py` | Per-repair-cycle | NONE |
| `ConvergenceProgressVector` | `app/quality/repair/vector_convergence.py` | Quality score trajectory | NONE |
| `ConvergenceFailureReporter` | `app/orchestration/failure_reporter.py` | Markdown report on disk | INDIRECT |
| `JobState.logs` | `app/web/server.py:75` | Plain string list | YES — SSE + poll |
| `JobState.status` | `app/web/server.py:68` | Status string | YES — poll + SSE |
| `_pipeline_log_listener` | `app/web/server.py:161` | structlog hook → SSE substep | PARTIAL |

### B.2 Observability Gaps for Dashboard

1. **No `ObservabilityReport` serialization endpoint** — `active_reports` is never queried by any HTTP endpoint
2. **No span timeline endpoint** — `SpanRecord` list is never surfaced
3. **No error record endpoint** — `ErrorRecord` traceback summaries unreachable from browser
4. **No state machine transition history endpoint** — `StateTransitionRecord.history` is local to `ProductionStateMachine` per job
5. **No quality score trajectory endpoint** — `ConvergenceProgressVector` only exists in RAM during repair loop
6. **No repair history endpoint** — `RepairTransactionRecord` flushed to file only upon successful export
7. **No convergence report live endpoint** — `convergence_report.json` only written upon export completion

**Design Constraint for Phase 7**: A read-model projection layer must extract and serialize this data at job terminal state, without mutating any authority object.

---

## C. Artifact Lifecycle Visualization

### C.1 Full Artifact Lifecycle

The canonical `ProductionState` enum (`app/orchestration/production_state.py:18`) defines 21 states:

```
CREATED
  ├─► SOURCE_VALIDATING → SOURCE_PARSED
  ├─► KNOWLEDGE_PROCESSING → KNOWLEDGE_READY
  ├─► INTENT_RESOLUTION → INTENT_READY
  ├─► TRANSFORMATION → BLUEPRINT_READY
  ├─► GROUPING → COMPOSITION_READY
  ├─► RENDERING → RENDERED
  └─► QUALITY_EVALUATING → QUALITY_EVALUATED
        ├─► APPROVED → EXPORTING → EXPORTED  [success]
        ├─► APPROVED_WITH_WARNINGS → EXPORTING → EXPORTED  [success]
        ├─► REPAIR_ANALYZING → REPAIR_PLANNING → REPAIRING
        │     └─► RE_RENDERING → RE_VALIDATING → QUALITY_EVALUATED  [loop]
        ├─► MANUAL_REVIEW_REQUIRED  [terminal / blocked]
        └─► BLOCKED  [terminal / blocked]
     └─► FAILED  [terminal / error]
     └─► CANCELLED  [terminal / error]
```

### C.2 What Dashboard Currently Shows

- Job `status` string: `queued | running | completed | failed | blocked`
- `percent` (0–100, computed from stage number)
- `current_step` (human-readable stage description)
- Plain log lines via SSE `substep` events

### C.3 What Dashboard Does NOT Show

- Exact `ProductionState` value (only maps to 5 simple statuses)
- Repair iteration count and loop transitions
- Re-render cycle detection (OSCILLATION)
- Quality score at each repair iteration
- Specific quality authority decision
- Whether export was approved vs. approved-with-warnings
- State machine transition history

### C.4 Phase 7 Dashboard Visualization Requirements

- **Pipeline Stage Stepper**: 10-stage progress bar mirroring `PIPELINE_STAGES`
- **State Machine View**: Live `ProductionState` badge
- **Repair Loop Indicator**: Iteration counter + convergence trajectory
- **Quality Decision Badge**: `EXPORT_APPROVED` / `APPROVED_WITH_WARNINGS` / `MANUAL_REVIEW_REQUIRED` / `BLOCKED`
- **Terminal State Explainer**: Surface convergence failure report for blocked states

---

## D. State Machine UI Representation

### D.1 State Machine Truth

`ProductionStateMachine` is authoritative. The dashboard NEVER calls `.transition()`. It may only READ `.current_state` and `.history`.

### D.2 State Categories for UI

| Category | States | UI Color |
|---|---|---|
| Pre-processing | CREATED, SOURCE_VALIDATING, SOURCE_PARSED | Blue |
| Intelligence | KNOWLEDGE_PROCESSING, KNOWLEDGE_READY, INTENT_RESOLUTION, INTENT_READY | Purple |
| Generation | TRANSFORMATION, BLUEPRINT_READY, GROUPING, COMPOSITION_READY | Indigo |
| Rendering | RENDERING, RENDERED | Cyan |
| Quality | QUALITY_EVALUATING, QUALITY_EVALUATED | Yellow |
| Repair | REPAIR_ANALYZING, REPAIR_PLANNING, REPAIRING, RE_RENDERING, RE_VALIDATING | Orange |
| Terminal OK | APPROVED, APPROVED_WITH_WARNINGS, EXPORTED | Green |
| Terminal Blocked | MANUAL_REVIEW_REQUIRED, BLOCKED | Red |
| Terminal Failure | FAILED, CANCELLED | Gray |

### D.3 Read-Model Access Pattern

```
ArtifactProductionContext.state_machine.history
  → List[StateTransitionRecord]
  → Serialize to read model at terminal state
  → Dashboard polls /api/jobs/{id}/state-timeline
```

---

## E. Quality Authority Visualization

### E.1 What UQA Emits

`UnifiedQualityAuthority.evaluate_artifact()` returns `UnifiedQualityReport` containing:
- `decision: ExportDecision` — authoritative verdict
- `overall_quality_score: float` — 0.0–1.0
- `domain_scores: Dict[str, float]` — per-domain breakdown
- `hard_blockers: List[str]` — blocking issues
- `warnings: List[str]` — non-blocking issues
- `findings: List[QualityFinding]` — all individual findings

### E.2 Dashboard Permitted Views

| View | Permitted | Notes |
|---|---|---|
| Show `decision` badge | YES | Read-only |
| Show `overall_quality_score` as gauge | YES | Read-only |
| Show `domain_scores` as radar/bar chart | YES | Read-only |
| Show `hard_blockers` list | YES | Read-only |
| Show `warnings` list | YES | Read-only |
| Show `findings` detail table | YES | Read-only |
| Modify any quality score | NO — FORBIDDEN | UQA is sole authority |
| Override any decision | NO — FORBIDDEN | UQA is sole authority |
| Re-run UQA from dashboard | NO — FORBIDDEN | Only pipeline can invoke UQA |

---

## F. Repair Convergence Explainability

### F.1 Repair Infrastructure (Existing)

| Component | Path | Dashboard-Relevant Data |
|---|---|---|
| `ProductionConvergenceController` | `app/orchestration/convergence_controller.py` | `score_history`, `decisions`, `hard_blocker_history` |
| `ConvergenceCheckResult` | `convergence_controller.py:44` | `outcome`, `stagnation_reason`, `cycle_detected`, `rationale` |
| `ConvergenceFailureReporter` | `app/orchestration/failure_reporter.py` | Full 13-section Markdown |
| `RepairTransactionRecord` | `app/quality/repair/transaction.py` | Per-iteration repair summary |
| `ConvergenceProgressVector` | `app/quality/repair/vector_convergence.py` | 4-dimensional quality vector |

### F.2 Repair Convergence Dashboard Requirements

- **Score Trajectory Chart**: `score_history[]` per repair iteration
- **Blocker Reduction Chart**: `hard_blocker_count` per iteration
- **Termination Reason Display**: `outcome` + `stagnation_reason` + `rationale`
- **Repair History Table**: Each `RepairTransactionRecord` row
- **Convergence Failure Report Viewer**: 13-section Markdown rendered inline

### F.3 Data Availability Constraint

`ConvergenceProgressVector` and `score_history` are currently in-memory only. Phase 7 must emit them to the job-level read model at pipeline completion.

---

## G. Human Review UX Integration Points

### G.1 Existing Review Infrastructure (Phase 6)

| Component | Path | Dashboard Integration Opportunity |
|---|---|---|
| `ReviewQueueRegistry` | `app/review/queue/registry.py` | List pending review cases |
| `ReviewCase` | `app/review/contracts/review_case.py` | Display case metadata |
| `ReviewEvidencePackage` | `app/review/contracts/evidence.py` | Display evidence bundle |
| `StaticReviewBundleGenerator` | `app/review/static_bundle.py` | Generate static HTML bundle |
| `ReviewProvenanceLedger` | `app/review/provenance/immutable_ledger.py` | Display audit ledger |
| `ReviewDecisionEngine` | `app/review/decisions/review_engine.py` | NOT directly callable from UI |
| `DirectiveSafetyValidator` | `app/review/safety/directive_safety_validator.py` | NOT directly callable from UI |

### G.2 Human Review Dashboard Permitted Actions

| Action | Permitted | Enforcement |
|---|---|---|
| List pending review cases | YES | Read from `ReviewQueueRegistry` |
| View review case detail | YES | Read `ReviewCase` + evidence bundle |
| Download static review HTML bundle | YES | `StaticReviewBundleGenerator` |
| View convergence failure report | YES | Read from file |
| Submit review decision | YES (gated) | Via bridged API → `ReviewDecisionEngine` |
| Submit repair directive | YES (gated) | Must pass `DirectiveSafetyValidator` |
| View ledger entries | YES | Read-only from `ReviewProvenanceLedger` |
| Override quality decision | NO — FORBIDDEN | UQA is sole authority |
| Force export | NO — FORBIDDEN | Hard blocked by `DirectiveSafetyValidator` |
| Modify benchmark baselines | NO — FORBIDDEN | `AntiLaunderingGuard` |

---

## H. Artifact Preview Architecture

### H.1 Current Preview System

- **PDF Preview**: `GET /api/documents/{filename}` serves PDF with `inline` content-disposition
- **HTML Preview**: Not exposed via API (stored in `outputs/web_runs/`)
- **Evidence Bundle**: `static_review.html` — not served by web server

### H.2 Phase 7 Preview Requirements

| Artifact | Format | Delivery Method |
|---|---|---|
| PRESENTATION | PDF + HTML | Serve both via API |
| HANDOUT | PDF + HTML | Serve both via API |
| WORKSHEET | PDF + HTML | Server-side filtered (anti-spoiling) |
| SCIENTIFIC_DOCUMENT | PDF + HTML | Serve both via API |

### H.3 Anti-Spoiling Invariant for Preview

WORKSHEET HTML preview endpoint must NEVER render answer-containing content. Filtering happens at the **server layer** via a `SafeWorksheetPreviewAdapter`. Raw HTML file cannot be served directly. This is NOT client-side JavaScript responsibility.

---

## I. Visual Diff System

### I.1 Versioning Infrastructure

`ProductionVersionManager` tracks per-iteration `blueprint_hash`, `pdf_hash`, `pdf_path`, `html_path`. These hashes enable deterministic diff detection.

### I.2 Visual Diff Architecture

| Layer | Responsibility | Authority Boundary |
|---|---|---|
| Hash comparison | Detect change | Read-only from iteration records |
| Score delta | Numeric diff | Read from `ConvergenceProgressVector` |
| Finding delta | Set difference of `QualityFinding` lists | Read from `UnifiedQualityReport` per iteration |
| Inline PDF viewer | Visual rendering | Never modifies PDF |

---

## J. Benchmark Command Center

### J.1 Existing Benchmark Infrastructure (Not Yet Dashboard-Exposed)

| Component | Path | API Exposure |
|---|---|---|
| `/api/benchmarks` | `app/web/server.py:323` | Model latency only |
| `BenchmarkCorpusRegistry` | `app/benchmarking/corpus_registry.py` | NONE |
| `GoldenCorpusRegistry` | `app/benchmarking/golden_registry.py` | NONE |
| `CertificationEngine` | `app/benchmarking/` | NONE |
| `BenchmarkRunner` | `app/benchmarking/benchmark_runner.py` | NONE |
| `AntiLaunderingGuard` | `app/benchmarking/governance.py` | NONE |

### J.2 Benchmark Command Center Requirements

Dashboard benchmark view must:
- Display **Golden Corpus** summary: count by artifact type, last update date
- Display **certification status** per artifact type (CERTIFIED / REGRESSED / PENDING)
- Display latest **benchmark run metrics**: accuracy, pass rate, regression delta
- Display **leakage guard status**: contamination detection result
- Allow operator to **trigger benchmark run** (async; no corpus modification)
- Display **split summary**: train/test/adversarial counts

**Authority boundary**: READ reports only. TRIGGER runs via CLI subprocess delegation. CANNOT modify golden corpus, lower baselines, or override certifications.

---

## K. Regression Visualization

| View | Data Source | Chart Type |
|---|---|---|
| Score trend over time | Historical benchmark run results | Line chart per artifact type |
| Regression alert badge | `CertificationDecision = REGRESSED` | Color-coded badge |
| Regression delta table | Per-metric delta | Sortable table |
| Blocker regression highlight | Specific failing test cases | Expandable list |

**Authority boundary**: Display regression alerts — YES. Link to failing fixture — YES. Modify baseline — NO. "Dismiss regression" from UI — NO (must go through review → `AntiLaunderingGuard`).

---

## L. Four Artifact-Specific Dashboards

### L.1 PRESENTATION

| Panel | Data |
|---|---|
| Slide count | UnifiedQualityReport / pipeline result |
| Cognitive load distribution | Per-slide complexity score |
| Layout family distribution | Slide layout variety |
| Quality gate result | Per-dimension quality scores |
| Preview | 16:9 PDF viewer |

### L.2 HANDOUT

| Panel | Data |
|---|---|
| Page count | PDF metadata |
| Reading flow score | `domain_scores["reading_flow"]` |
| Section hierarchy | Blueprint structure |
| Self-containedness check | Cross-ref resolution status |
| Preview | A4 PDF viewer |

### L.3 WORKSHEET / LKS

| Panel | Data |
|---|---|
| Activity count | Blueprint activity count |
| Inquiry progression | observation → prediction → investigation → analysis → reflection |
| Anti-spoiling status | Answer-revelation directive rejection status |
| Student-facing preview | Filtered (spoil-safe) HTML/PDF |
| Instructor preview | Unfiltered PDF (reviewer auth) |

### L.4 SCIENTIFIC_DOCUMENT / KTI

| Panel | Data |
|---|---|
| Citation count | Bibliography section of blueprint |
| Citation format compliance | Indonesian scientific format check |
| IMRaD structure coverage | Introduction / Method / Result / Discussion presence |
| Plagiarism-prevention status | fabricate_citation directive rejection status |
| Preview | A4 PDF viewer |

---

## M. Information Architecture

### M.1 Proposed Navigation Structure

```
Dashboard Root (/)
├── Generate (/)              — Input form + active job monitor
├── Jobs (/jobs)              — Job history + status list
│   └── Job Detail (/jobs/{id})   — Full lifecycle, quality report, repair history
├── Library (/library)        — Document archive + preview
├── Review (/review)          — Review queue (MANUAL_REVIEW_REQUIRED cases)
│   └── Case (/review/{id})   — Evidence bundle, decision form
├── Benchmarks (/benchmarks)  — Golden corpus + certification + regression
└── System (/system)          — Status, model management, 9Router diagnostics
```

### M.2 Information Hierarchy Rules

1. **Generation-first**: Generate panel is default landing
2. **Quality is read-only**: Never rendered as interactive controls
3. **Review is gated**: Submission bridges to safety-validated API
4. **Benchmarks are observation-only**: Cannot modify from UI

---

## N. Operator Journeys

### N.1 Primary Journey: Generate → Observe → Inspect

1. User fills generation form
2. `POST /api/generate` → background task starts
3. SSE delivers live stage progress (10 stages)
4. If completed: PDF viewer + quality report badge
5. User inspects quality scores, findings
6. User downloads PDF

### N.2 Failure Journey: Blocked → Review

1. Generation terminates at `MANUAL_REVIEW_REQUIRED` or `BLOCKED`
2. Dashboard shows red terminal badge + convergence failure reason
3. Operator navigates to Review panel
4. Case in queue with priority score
5. Operator downloads static review bundle
6. Operator submits decision (gated by `DirectiveSafetyValidator`)
7. If directive approved: governed repair re-run initiated

### N.3 Benchmark Journey: Certify → Observe → Alert

1. Navigate to Benchmarks panel
2. View current certification status
3. Trigger benchmark run (async)
4. If regression detected: alert badge + delta table
5. Submit review case (cannot modify baseline from UI)

---

## O. API / Adapter Boundary

### O.1 Existing API: Keep As-Is

All 11 existing endpoints preserved without modification.

### O.2 New API Endpoints Required (Phase 7)

| Endpoint | Method | Purpose | Authority |
|---|---|---|---|
| `/api/jobs/{id}/quality-report` | GET | UnifiedQualityReport JSON from read model | Read-only |
| `/api/jobs/{id}/repair-history` | GET | Repair iteration records | Read-only |
| `/api/jobs/{id}/state-timeline` | GET | StateTransitionRecord[] | Read-only |
| `/api/jobs/{id}/convergence` | GET | Convergence failure report | Read-only |
| `/api/review/cases` | GET | List pending review cases | Read-only |
| `/api/review/cases/{id}` | GET | Review case detail | Read-only |
| `/api/review/cases/{id}/evidence` | GET | Evidence bundle download | Read-only |
| `/api/benchmarks/corpus` | GET | Golden corpus summary | Read-only |
| `/api/benchmarks/certification` | GET | Certification status per type | Read-only |
| `/api/benchmarks/run` | POST | Trigger benchmark run | CLI subprocess delegation |

---

## P. Read Model Architecture

### P.1 Job Read Model Structure

```
outputs/web_runs/{job_id}/
  ├── job_manifest.json          — Job identity, status, timestamps
  ├── quality_report.json        — Copy of UnifiedQualityReport at terminal state
  ├── state_timeline.json        — List[StateTransitionRecord] serialized
  ├── repair_history.json        — List[RepairTransactionRecord] serialized
  ├── convergence.json           — ConvergenceCheckResult + score_history[]
  └── convergence_failure.md     — ConvergenceFailureReporter output (if applicable)
```

### P.2 Write Trigger

`JobReadModelWriter` (non-authority, pure I/O adapter) invoked at terminal state:
- `EXPORTED` → full success read model
- `MANUAL_REVIEW_REQUIRED` → partial read model (no export package)
- `BLOCKED` → partial read model + convergence failure report
- `FAILED` → minimal read model with error details

`JobReadModelWriter` is NOT an authority. It only serializes data already decided by authorities.

---

## Q. Static vs. Interactive Frontend

### Q.1 Current Frontend

`app/web/static/`: vanilla JavaScript SPA (no build step, no bundler, no framework). Architecture must be preserved.

### Q.2 Phase 7 Frontend Expansion

| Component | Approach |
|---|---|
| Stage progress stepper | Pure JavaScript + CSS |
| State machine visualizer | SVG-based state diagram |
| Quality score charts | Chart.js (CDN, no bundler) |
| Repair convergence chart | Chart.js line chart |
| PDF viewer | Browser native `<embed>` |
| Review queue list | HTML table + pure JS |

The frontend may: submit forms, stream SSE events, download files, navigate panels.  
The frontend must NOT: make quality/export decisions, render unfiltered worksheet content, cache quality decisions as authoritative.

---

## R. Performance & Large Artifacts

| Scenario | Concern | Mitigation |
|---|---|---|
| PRESENTATION > 20 slides | PDF preview | Browser native `<embed>` handles paging |
| SCIENTIFIC_DOCUMENT with full bibliography | JSON > 500KB | Paginate findings above 200 entries |
| Repair loop (3 iterations) | Multiple JSON reports | Merge into single `repair_history.json` |
| Concurrent jobs | SSE subscriber lists | `_JOBS` dict supports multiple subscribers per job |
| 13-section convergence failure report | Markdown render | Server-side Markdown → HTML |

**Performance Invariants**:
- All API responses complete within 2 seconds (excluding streaming endpoints)
- Quality report JSON does not exceed 2MB per job
- PDF preview loads within 5 seconds via browser native renderer
- SSE keepalive ping every 20 seconds (already implemented)

---

## S. Forensic Search

| Search Type | Data Source | Index |
|---|---|---|
| By job ID | `_JOBS` dict + `job_manifest.json` | In-memory + filename |
| By artifact type | `job_manifest.json` | Filesystem scan |
| By quality decision | `quality_report.json` | Filesystem scan |
| By terminal state | `job_manifest.json` | Filesystem scan |
| By date range | `job_manifest.json: created_at` | Filesystem scan |

**Design principle**: No database. All search is filesystem-scan over `outputs/web_runs/`. Acceptable for local developer tool scale.

---

## T. Security & Local File Safety

**Security Model**: Localhost-only tool (`host="127.0.0.1"`, port 20129). CORS wildcard acceptable for localhost.

| Risk | Mitigation |
|---|---|
| Path traversal via `/api/documents/{filename}` | `OUTPUTS_DIR.rglob(filename)` limits to `outputs/` subtree |
| Serving raw worksheet HTML with answers | `SafeWorksheetPreviewAdapter` required |
| Serving private system files | All served files within `outputs/` or `app/web/static/` |
| Injecting malicious content via job title | `clean_slug` sanitizes to alphanumeric only |
| Review evidence.json contains internal findings | Serve only within localhost; document constraint |
| Benchmark corpus fixture content | Read-only served; no upload/modify endpoints |

---

## U. Design System Integration

The **document design system** (`app/design_system/`) governs generated PDF/HTML artifacts. The dashboard's `app.css` is a separate web UI concern. These two systems MUST NOT be co-mingled.

Phase 7 may define shared CSS variables for status colors (matching state categories in Section D.2) but the design systems remain architecturally independent.

---

## V. Failure-First UX

| Failure Type | Dashboard Behavior |
|---|---|
| `FAILED` (system error) | Error message + truncated stack trace + retry button |
| `BLOCKED` (non-convergence) | 13-section convergence failure report + blockers + recommendation |
| `MANUAL_REVIEW_REQUIRED` | Review queue link + case ID + evidence download button |
| `OSCILLATION_DETECTED` | Repair loop visualization + stagnation reason |
| `BUDGET_EXHAUSTED` | Repair history + final quality score + blockers |

**No bypass buttons**: A `BLOCKED` status must NEVER have a "Retry bypassing UQA" action. Only available actions:
- "View Convergence Report" (read)
- "Open in Review Queue" (submit to human review pipeline)

---

## W. Observability Without Authority

**Core Principle**: The dashboard observes; it never decides.

| System | Dashboard Role |
|---|---|
| `UnifiedQualityAuthority` | Display its output, NEVER re-invoke it |
| `ProductionStateMachine` | Display history, NEVER call `.transition()` |
| `AuthorizedExportGate` | Display export package contents, NEVER trigger export |
| `AntiLaunderingGuard` | Display governance status, NEVER bypass it |
| `CertificationEngine` | Display certification results, NEVER modify them |
| `ReviewDecisionEngine` | Display decisions; submit new via bridged API |
| `DirectiveSafetyValidator` | All directives must pass through it server-side |

**Implementation Pattern**:
```
Browser → POST/GET → FastAPI Endpoint
                        ↓
                   Read model JSON (written by pipeline at terminal state)
                        ↓
                   JSON response → Browser renders
```

No browser → Authority pipeline shortcut permitted.

---

## X. Phase 7 Implementation Roadmap

### X.1 Atomic Implementation Stages

Implementation begins ONLY after this audit document is approved.

| Stage | Name | Scope |
|---|---|---|
| 7.1 | Job Read Model Writer | Non-authority adapter serializing pipeline state to JSON at terminal states |
| 7.2 | Job Read Model API | Extend `/api/jobs/{id}` with quality, repair, state-timeline endpoints |
| 7.3 | Pipeline Stage Stepper UI | 10-stage progress visualization |
| 7.4 | State Machine Badge UI | Live `ProductionState` display + transition timeline |
| 7.5 | Quality Report Panel | Domain scores radar, findings table, decision badge |
| 7.6 | Repair History Panel | Per-iteration score chart, blocker evolution |
| 7.7 | Convergence Failure Viewer | 13-section Markdown render for BLOCKED/MANUAL_REVIEW |
| 7.8 | Review Queue Panel | Case list, priority scores, evidence download |
| 7.9 | Benchmark Command Center | Corpus summary, certification status, regression alerts |
| 7.10 | Artifact Library Enhancement | Filter by type/decision, enhanced metadata display |

### X.2 What Is Explicitly Excluded from Phase 7

- No database installation (SQLite, PostgreSQL, Redis, MongoDB)
- No frontend framework (React, Next.js, Vue, Svelte)
- No WebSocket (SSE is sufficient)
- No authentication system (localhost only)
- No cloud deployment configuration
- No new quality evaluation logic
- No modification of `ProductionStateMachine`, `UnifiedQualityAuthority`, `AuthorizedExportGate`
- No new repair strategies
- No modification of `ReviewDecisionEngine` or `DirectiveSafetyValidator`

---

## Audit Conclusion

### What Exists

| Component | Status |
|---|---|
| FastAPI web server with SSE streaming | EXISTS |
| Static SPA frontend (vanilla JS, no build step) | EXISTS |
| In-memory job store with 5-state simplified status | EXISTS |
| 10-stage pipeline progress via `PipelineStageRegistry` | EXISTS |
| Structured observability (ObservabilityReport, spans) | EXISTS — NOT surfaced to dashboard |
| ProductionStateMachine with 21 auditable states | EXISTS — NOT surfaced to dashboard |
| UnifiedQualityAuthority rich UnifiedQualityReport | EXISTS — only partially surfaced |
| ConvergenceFailureReporter 13-section Markdown | EXISTS — NOT surfaced to dashboard |
| Full Phase 6 human review infrastructure | EXISTS — ZERO dashboard exposure |
| Full Phase 5 benchmark/golden corpus infrastructure | EXISTS — ZERO dashboard exposure |

### Critical Gap: No Persistent Read Model

The single most critical gap is: **there is no job-level read model written to disk at terminal state**. The rich quality, repair, convergence, and state machine data exists in RAM during execution but is not persisted in a dashboard-accessible format.

This makes **Phase 7.1 (Job Read Model Writer)** the foundational prerequisite for all subsequent dashboard work.

### Authority Boundary: Confirmed Clean

The existing web server correctly calls `MaterialProductionPipeline` without bypassing any authority. `_run_job_pipeline()` delegates completely to the pipeline; it never calls `UnifiedQualityAuthority`, `AuthorizedExportGate`, or `ProductionStateMachine` directly. This must be preserved in Phase 7.

---

**HARD STOP**: This forensic audit document must be reviewed before Phase 7 implementation begins.
