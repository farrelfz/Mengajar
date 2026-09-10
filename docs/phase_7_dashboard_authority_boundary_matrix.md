# Universal Document Intelligence System V5
# Phase 7 — Dashboard Authority Boundary Matrix

**Status**: PHASE 7.0 FORENSIC AUDIT DELIVERABLE  
**Audit Date**: 2026-09-08  
**Invariant**: The dashboard is a VIEW + INTERACTION ADAPTER. It is NEVER a decision engine.

---

## Authority Boundary Matrix

| DOMAIN | AUTHORITY | DASHBOARD READ ACCESS | DASHBOARD WRITE ACCESS | ALLOWED DASHBOARD ACTIONS | FORBIDDEN DASHBOARD ACTIONS |
|---|---|---|---|---|---|
| **Quality Decision** | `UnifiedQualityAuthority` (Level-0) | Read `UnifiedQualityReport` from job read model JSON | NONE | Display decision badge, score gauges, domain score charts, findings table, blockers list, warnings list | Re-invoke UQA; modify any score; override any decision; filter out findings |
| **Export Authorization** | `AuthorizedExportGate` | Read export package file list from `final/manifest.json` | NONE | Display export status; link to download files from `final/` | Trigger export independently; bypass export gate; serve files not in `final/` |
| **Production Lifecycle State** | `ProductionStateMachine` | Read `StateTransitionRecord[]` from `state_timeline.json` read model | NONE | Display current state badge; render state transition history timeline | Call `.transition()`; simulate state changes; invent state transitions |
| **Repair Execution** | `RepairTransactionManager` + `MinimalInterventionRepairPlanner` | Read `RepairTransactionRecord[]` from `repair_history.json` read model | NONE | Display repair iteration table; show score per iteration; show mutation scope per iteration | Invoke repair planner; create repair transactions; select repair strategies |
| **Convergence Control** | `ProductionConvergenceController` | Read `convergence.json` from read model (score_history, stagnation_reason, outcome) | NONE | Display convergence trajectory charts; show termination reason; surface 13-section failure report | Modify convergence parameters; extend max_iterations from UI; suppress convergence warnings |
| **Benchmark Certification** | `CertificationEngine` | Read certification reports from `golden_corpus/` | Trigger benchmark run (delegates to CLI subprocess) | Display certification status per artifact type; show pass/fail metrics; trigger run | Modify certification decision; change baseline score; delete benchmark fixtures |
| **Golden Corpus Governance** | `AntiLaunderingGuard` + `GoldenCorpusVersionManager` | Read corpus manifest for summary stats | NONE | Display corpus size, artifact type counts, last update, split summary | Add/remove corpus fixtures; lower baseline scores; change corpus version; bypass anti-laundering |
| **Human Review Decision** | `ReviewDecisionEngine` | Read `ReviewCase`, `ReviewDecision` records | Submit new decisions via bridged `/api/review/cases/{id}/decide` endpoint (server-side gated) | List review cases; view case detail; download evidence bundle; submit structured decision with rationale | Submit decisions without rationale; submit decisions for cases not in LEASED state; submit decisions that override UQA |
| **Directive Safety** | `DirectiveSafetyValidator` | Read directive validation results | All directives submitted via dashboard must be validated server-side first | Display which directives were proposed; display rejection reason if rejected | Bypass `DirectiveSafetyValidator`; send raw directives directly to repair engine; suppress rejection logs |
| **Repair Directive Execution** | `ReviewRepairBridge` | Read resulting `DirectiveRepairHint` after validation | Submit approved directives via API (server-side safety gate mandatory) | Display proposed directive; show validation result; submit via API | Invoke `ReviewRepairBridge` directly from browser; skip safety validation; modify approved directive after validation |
| **Artifact Preview — Worksheet** | `SafeWorksheetPreviewAdapter` (to be built in Phase 7) | Read server-filtered HTML from adapter | NONE | Request filtered worksheet preview via `/api/jobs/{id}/preview?mode=student` | Request raw unfiltered worksheet HTML; render spoilable content client-side |
| **Benchmark Corpus Registry** | `BenchmarkCorpusRegistry` | Read fixture list and split summary | NONE | Display train/test/adversarial split counts per artifact type | Add fixtures; delete fixtures; change split assignments |
| **Review Provenance Ledger** | `ReviewProvenanceLedger` (append-only) | Read ledger entries from `ledger.jsonl` | NONE | Display ledger entries (case ID, decision type, reviewer, timestamp, hash) | Append to ledger directly; modify or delete ledger entries; verify hash chain from client |
| **Reviewer Calibration** | `ReviewerCalibrationEngine` | Read calibration scores per reviewer | NONE | Display reviewer calibration score; show leniency/harshness index; show whether reviewer is gated | Set calibration scores; bypass calibration gating; assign golden cases |
| **Observability Data** | `ObservabilityReport` + `active_reports` | Read `ObservabilityReport` serialized at job terminal state | NONE | Display span timeline; show run summary (span count, error count, stage count); display error records | Query live `active_reports` dict directly; modify observability events; add/remove spans |
| **Convergence Failure Report** | `ConvergenceFailureReporter` | Read `convergence_failure.md` from job read model | NONE | Render 13-section report inline; offer Markdown download | Modify report content; re-generate report with different parameters; suppress sections |
| **Model Routing** | `NineRouterClient` | Read available models and current active model | Set active model via `POST /api/active-model` (existing endpoint) | List models; show active model; trigger model test; set active model | Modify 9Router configuration files directly; bypass model routing; change routing policy |
| **Pipeline Stage Progression** | `PipelineStageRegistry` + `MaterialProductionPipeline` | Read `PipelineStageDefinition[]` and progress from SSE stream | NONE | Display 10-stage stepper with current progress; show stage name and description | Skip stages; re-order stages; invoke individual stages independently |
| **Artifact File Serving** | Filesystem (`outputs/` subtree) | Read files within `outputs/` | NONE | Download PDFs from `outputs/`; download final package from `outputs/.../final/`; preview HTML artifacts (filtered for worksheet) | Serve files outside `outputs/` or `app/web/static/`; write to `outputs/`; delete output files |
| **Disagreement Adjudication** | `AdjudicationManager` | Read adjudication result from review case | Submit adjudication escalation request via API (senior flag + calibration ≥ 0.85 enforced server-side) | Display disagreement analysis; display adjudication outcome | Resolve adjudication without senior flag; bypass calibration check; force adjudication outcome |

---

## Summary: Absolute Forbidden Actions (Dashboard)

Regardless of any user interaction, operator role, or system state, the following actions are PERMANENTLY FORBIDDEN from the dashboard layer:

1. **Calling `UnifiedQualityAuthority.evaluate_artifact()` directly** — UQA is invoked exclusively by the production pipeline
2. **Calling `ProductionStateMachine.transition()` directly** — state transitions are exclusive to `ArtifactProductionContext`
3. **Calling `AuthorizedExportGate.verify_and_export()` directly** — export is exclusive to the production orchestrator
4. **Bypassing `DirectiveSafetyValidator`** — all human directives must pass through the safety gate server-side
5. **Modifying `golden_corpus/manifest.json` directly** — all corpus mutations must pass through `AntiLaunderingGuard`
6. **Lowering any quality baseline** — forbidden by `AntiLaunderingGuard`
7. **Rendering unfiltered WORKSHEET content** — anti-spoiling invariant; server-side filtering mandatory
8. **Triggering export for `BLOCKED` or `MANUAL_REVIEW_REQUIRED` artifacts** — terminal state immutability
9. **Modifying or deleting `ledger.jsonl` entries** — append-only immutable ledger invariant
10. **Submitting review decisions for un-leased cases** — review lease management enforced server-side

---

## Read Model Access Protocol

All dashboard data flows MUST follow this protocol:

```
[Dashboard Browser]
      │
      │  HTTP GET /api/jobs/{id}/quality-report
      ▼
[FastAPI Endpoint — server.py]
      │
      │  Read ONLY from:
      │    outputs/web_runs/{job_id}/quality_report.json
      │    (written at terminal state by JobReadModelWriter)
      ▼
[JSON Response]
      │
      ▼
[Dashboard renders — no authority logic in browser]
```

The dashboard NEVER reads from:
- `app/orchestration/` Python objects directly
- `app/quality/` Python objects directly
- `app/review/` Python objects directly (except via bridged API endpoints with server-side gating)
- `app/benchmarking/` Python objects directly (except via `/api/benchmarks/` endpoints)
