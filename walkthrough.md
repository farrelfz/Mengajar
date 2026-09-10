# Universal Document Intelligence System V5
# Phase 6 Architectural Walkthrough: Governed Human Review Lifecycle

> **IMPLEMENTATION COMPLETE**: The governed human review lifecycle described below is fully implemented and validated across all 4 canonical formats with 649 green tests.

---

## The End-to-End Review Lifecycle Flow

```text
       Production Failure / Stagnation / Regression
                           │
                           ▼
                 [ 1. Review Intake ]
                 - ReviewabilityClassifier
                 - ReviewIntakeRouter
                           │
                           ▼
              [ 2. Queue Prioritization ]
                 - ReviewPriorityModel (P0-P3)
                 - LeaseManager (Atomic locks)
                           │
                           ▼
               [ 3. Evidence Assembly ]
                 - ReviewLineageAdapter
                 - EvidenceSufficiencyAnalyzer
                 - StaticReviewBundleGenerator
                           │
                           ▼
                  [ 4. Human Review ]
                 - BlindReviewPolicy
                 - ReviewerCapabilityProfile
                 - ReviewerCalibrationEngine
                           │
                           ▼
               [ 5. Structured Decision ]
                 - Epistemic separation (Obs -> Interp -> Dec -> Dir)
                 - ConfidenceEvaluator
                           │
                           ▼
               [ 6. Disagreement Check ]
                 - DisagreementAnalyzer
                 - AdjudicationManager (Senior Expert)
                           │
                           ▼
             [ 7. Directive Safety Gateway ]
                 - DirectiveSafetyValidator (Zero force-export)
                 - AuthorityBoundaryGuard (Zero UQA bypass)
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
   [ 8A. Repair ]   [ 8B. Governance ] [ 8C. Escalation ]
   ReviewRepair      BenchmarkGov      Senior Adjudicator
      Bridge            Bridge               Queue
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
               [ 9. Provenance Commit ]
                 - Append-only ReviewProvenanceLedger
                 - Cryptographic SHA-256 Hash Chain
                           │
                           ▼
                   [ 10. Resolution ]
                 - ReviewStateMachine -> RESOLVED
```

---

## Validated Artifact Format Lifecycles

1. **PRESENTATION (`tests/fixtures/oobleck_experiment.md`)**:
   - Detected 85-word slide violating 60-word threshold.
   - Evidence package generated with visual render and bounding box coordinates.
   - Reviewer leased case, confirmed defect, and issued `SPLIT_SLIDE` directive.
   - Directive passed safety gateway and was translated into `LEVEL_R3_ARTIFACT_STRUCTURE` hint.
   - State transitioned cleanly to `DIRECTIVE_PROPOSED`, provenance committed to ledger.

2. **WORKSHEET (`tests/fixtures/oobleck_experiment.md`)**:
   - Flagged for potential inquiry answer disclosure in activity prompt.
   - Reviewer issued `WITHHOLD_EXPLANATION` pedagogical directive.
   - Direct attempts to disclose answers (`reveal_answers=True` or `answer key`) structurally blocked by `DirectiveSafetyValidator`.
   - Directive translated to `LEVEL_R4_SEMANTIC_TRANSFORMATION`.

3. **SCIENTIFIC_DOCUMENT / KTI (`tests/fixtures/kti_bab1.md`)**:
   - Flagged for ungrounded scientific claim in Chapter 1.
   - Reviewer issued `REQUEST_CITATION_BACKING` evidence directive.
   - Direct attempts to fabricate citation (`fabricate_citation=True`) blocked by safety gateway.
   - Directive translated to `LEVEL_R5_SOURCE_INTELLIGENCE`.

4. **HANDOUT (`tests/fixtures/hand_fire_full.md`)**:
   - Flagged for reading density imbalance exceeding 0.85 scannability bound.
   - Reviewer issued `REDUCE_COGNITIVE_LOAD` pedagogical directive.
   - Directive translated to `LEVEL_R3_ARTIFACT_STRUCTURE`.

---

# Phase 7 Operator Journey: Production UX & Dashboard

```text
STATUS: PHASE 7.0 FORENSIC AUDIT COMPLETE — WALKTHROUGH DEFINED
```

The Phase 7 system operator journey describes the complete experience of using the production dashboard to observe, inspect, understand, repair, review, certify, and export document artifacts.

---

## System Operator Journey: Generate → Observe → Inspect → Understand → Repair → Review → Certify → Export

```text
┌──────────────────────────────────────────────────────────────────────┐
│  1. GENERATE                                                          │
│  - Operator fills form: title, raw content, format, subject, level   │
│  - POST /api/generate → background pipeline starts                   │
│  - Job assigned ID; SSE stream URL returned                          │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  2. OBSERVE (Real-time)                                               │
│  - SSE stream delivers live stage progress events                    │
│  - 10-stage pipeline stepper advances: Parsing → Semantics → AI      │
│    → Manifest → Architecture → Visual Grammar → Composition          │
│    → PDF Rendering → Quality Assurance → Repair (if needed)         │
│  - ProductionState badge updates: CREATED → ... → QUALITY_EVALUATING │
│  - Log substeps stream in real-time (9Router, Playwright, QA events) │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  3. INSPECT (Post-completion)                                         │
│  - Job terminal state: EXPORTED or BLOCKED/MANUAL_REVIEW_REQUIRED    │
│  - Job Read Model Writer fires: writes quality_report.json,          │
│    state_timeline.json, repair_history.json, convergence.json        │
│  - Operator navigates to Job Detail panel                            │
│  - Quality Report Panel renders:                                     │
│    - Decision badge: EXPORT_APPROVED / APPROVED_WITH_WARNINGS /      │
│      MANUAL_REVIEW_REQUIRED / BLOCKED                                │
│    - Overall quality score gauge (0.0–1.0)                           │
│    - Domain score chart (radar: semantic, fidelity, rendered, etc.)  │
│    - Hard blockers list (prominent, red)                             │
│    - Warnings list (orange)                                          │
│    - Findings table (expandable, read-only)                          │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  4. UNDERSTAND (Repair Forensics)                                     │
│  - Repair History Panel (if repair iterations occurred):             │
│    - Per-iteration table: strategy, scope, quality before/after      │
│    - Score trajectory line chart (quality per iteration)             │
│    - Blocker reduction chart (blockers remaining per iteration)      │
│  - Convergence Failure Viewer (if BLOCKED or MANUAL_REVIEW):         │
│    - 13-section Markdown report rendered inline                      │
│    - Sections: initial defects, root cause, hypotheses, mutations,   │
│      quality vectors, blocker evolution, drift, budget, local min,   │
│      termination cause, recommended intervention                     │
│  - State Machine Timeline:                                           │
│    - Chronological list of all state transitions with timestamps     │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
                    ▼                    ▼
         [5A. SUCCESS PATH]    [5B. BLOCKED PATH]
         PDF viewer opens      Navigate to Review
         Download PDF          Queue panel
         Export complete            │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│  5B. REPAIR (Human Review)                                            │
│  - Review Queue Panel lists pending cases:                            │
│    - Priority score (P0–P3)                                          │
│    - Artifact type and convergence failure reason                    │
│    - Time in queue                                                   │
│  - Operator downloads static evidence bundle (HTML)                  │
│  - Operator inspects:                                                │
│    - Render previews (bounding boxes, geometry violations)           │
│    - Repair history and quality trajectory                           │
│    - Source-to-render traceability links                             │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  6. REVIEW (Structured Decision)                                      │
│  - Operator submits structured review decision via form:             │
│    - Observation (what was seen)                                     │
│    - Interpretation (epistemic status: CONFIRMED / DISPUTED)         │
│    - Decision (APPROVE_WITH_REPAIRS / ESCALATE)                      │
│    - Directive (SPLIT_SLIDE / REDUCE_COGNITIVE_LOAD / etc.)         │
│  - Form submits to POST /api/review/cases/{id}/decide                │
│  - Server validates directive via DirectiveSafetyValidator           │
│    - force_export → REJECTED                                         │
│    - reveal_answers → REJECTED                                       │
│    - fabricate_citation → REJECTED                                   │
│    - Valid directives → approved, bridge translates to repair hint   │
│  - Decision committed to immutable ledger (append-only JSONL)        │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  7. CERTIFY (Benchmark Governance)                                    │
│  - Operator navigates to Benchmarks panel                            │
│  - Views: Golden Corpus summary, certification status per type       │
│  - Triggers benchmark run → async; no corpus modification            │
│  - Certification panel updates:                                      │
│    - CERTIFIED: all metrics above baseline                           │
│    - REGRESSED: delta alert with failing fixture links               │
│  - If regression: operator submits review case for affected fixture  │
│    (cannot dismiss from UI; must go through AntiLaunderingGuard)     │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  8. EXPORT (After Successful Re-run)                                  │
│  - After review directive triggers governed repair re-run:            │
│    - New job created; full pipeline executes                         │
│    - If UQA issues EXPORT_APPROVED: export gate authorizes           │
│    - final/ directory written: PDF, HTML, quality report, provenance │
│  - Dashboard Job Detail shows: EXPORTED terminal state (green)       │
│  - PDF preview opens; download link active                           │
│  - Quality report shows: decision = EXPORT_APPROVED                  │
│  - Export is COMPLETE                                                │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Authority Invariants Throughout the Journey

At every step, the following invariants are enforced:

1. **The dashboard never calls `UnifiedQualityAuthority`** — quality evaluations happen only in the pipeline
2. **The dashboard never calls `ProductionStateMachine.transition()`** — state is read-only
3. **The dashboard never calls `AuthorizedExportGate`** — export is the pipeline's responsibility
4. **All human directives pass through `DirectiveSafetyValidator` server-side** before any repair is initiated
5. **The benchmark corpus is never modified from the dashboard** — `AntiLaunderingGuard` governs all corpus changes
6. **WORKSHEET artifacts are only previewed through server-side anti-spoiling filter** — never raw HTML


---

# Phase 7.1 Lifecycle Walkthrough: Persistent Job Read Model Projection

```text
STATUS: PHASE 7.1 FORENSIC AUDIT COMPLETE — OBSERVATIONAL LIFECYCLE AUDITED
```

The diagram below illustrates the exact chronological progression of observational data from production domain events to persistent, query-safe read models:

```text
               +----------------------------------+
               |        1. JOB CREATED            |
               | - Canonical job_id assigned      |
               | - ArtifactProductionContext init |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |      2. PIPELINE EXECUTES        |
               | - Parsing -> Knowledge -> Intent |
               | - Blueprint -> Composition       |
               | - Render -> Quality -> Repair    |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               | 3. OBSERVATIONAL SIGNAL EMITTED  |
               | - State transition recorded      |
               | - Iteration snapshot generated   |
               | - Terminal outcome reached       |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |     4. PROJECTION ASSEMBLED      |
               | - JobReadModelProjector extracts |
               | - Zero quality recalculation     |
               | - Large artifacts referenced     |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |          5. VALIDATED            |
               | - Schema version verified (1.0.0)|
               | - Coherence checked (iterations) |
               | - Strict Pydantic model valid    |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |    6. ATOMIC SNAPSHOT WRITE      |
               | - Serialized to deterministic JSON|
               | - Written to .tmp_snap_{uuid}.json|
               | - Flushed and fsynced to disk    |
               | - Atomic os.replace() applied    |
               | - Saved: snapshot_{seq:06d}.json |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |       7. HASH GENERATED          |
               | - SHA-256 digest computed        |
               | - Source reference hashes bound  |
               | - Tamper-evident integrity sealed|
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |      8. REGISTRY UPDATED         |
               | - latest.json pointer updated    |
               | - JobReadModelRegistry reloaded  |
               | - Job index state indexed        |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |     9. DASHBOARD READABLE        |
               | - Read model queryable via API   |
               | - CLI inspect-job functional     |
               | - 100% decoupled from live RAM   |
               | - Zero authority contamination   |
               +----------------------------------+
```

---

## Observational Isolation Invariants

1. **Step 3 (Signal Emission)** is completely one-way. The production domain emits facts; it never accepts state feedback from the projection layer.
2. **Step 4 (Projection Assembly)** extracts scalar numbers, strings, and enums. It never re-runs quality algorithms or repair heuristics.
3. **Step 6 (Atomic Write)** uses Linux `os.replace` to prevent race conditions. Concurrent readers at Step 9 will never observe partial JSON or a half-written snapshot.
4. **Step 8 (Registry Update)** updates an atomic pointer. If `latest.json` or the registry index is ever deleted, the system can rebuild them from the immutable snapshots directory (`snapshots/`) without loss of data.
