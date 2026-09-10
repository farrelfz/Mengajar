# Universal Document Intelligence System V5
# Phase 7.1 — Read Model Authority Boundary Specification

**Status**: FORENSIC AUDIT DELIVERABLE  
**Date**: 2026-09-08  
**Core Invariant**: "OBSERVATION WITHOUT AUTHORITY"

---

## 1. Tripartite Architectural Boundary

The architecture enforces a strict tripartite separation between the Authoritative Production Domain, the Persistent Read Model Projection, and the Future Query / Dashboard Layer:

```
+-------------------------------------------------------------------------+
|                  AUTHORITATIVE PRODUCTION DOMAIN                        |
|                                                                         |
|  - UnifiedQualityAuthority (Level-0 Quality Sovereign)                 |
|  - AuthorizedExportGate (Sole Export Clearance Gate)                    |
|  - ProductionStateMachine (21-State Immutable Terminal Transitions)    |
|  - MinimalInterventionRepairPlanner + RepairTransactionManager          |
|  - CertificationEngine + AntiLaunderingGuard                            |
|  - DirectiveSafetyValidator + ReviewDecisionEngine                      |
+-------------------------------------------------------------------------+
                                     |
                                     | emits observational snapshots
                                     | (read-only, decoupled)
                                     v
+-------------------------------------------------------------------------+
|                    PERSISTENT JOB READ MODEL                            |
|                                                                         |
|  - JobReadModel / JobSnapshot (Frozen Pydantic Models)                  |
|  - AtomicJobSnapshotWriter (POSIX os.replace, .tmp_<uuid>)              |
|  - JobReadModelRegistry (Index & Lookup on Disk)                        |
|  - ReadModelStalenessDetector (Freshness & Integrity Monitor)           |
|  - SnapshotConsistencyContract (Cross-Iteration Validation)             |
|  - JobReadModelRebuilder (100% Rebuildable from Authoritative Artifacts)|
+-------------------------------------------------------------------------+
                                     |
                                     | query-only projection
                                     | (zero mutation path)
                                     v
+-------------------------------------------------------------------------+
|                  FUTURE DASHBOARD / API / CLI                           |
|                                                                         |
|  - FastAPI Endpoints (GET /api/jobs/{id}/...)                           |
|  - Dashboard SPA (Vanilla JS + HTML + CSS)                              |
|  - CLI Tools (inspect-job, verify-job-snapshot, list-jobs)              |
|  - Human Review Studio (Evidence & Queue Visualization)                 |
+-------------------------------------------------------------------------+
```

---

## 2. Production Authority vs. Read Model Projection vs. Future Dashboard

| System Capability | Production Domain Authority | Persistent Read Model Projection | Future Dashboard / Query Layer |
|---|---|---|---|
| **Quality Evaluation** | **SOVEREIGN AUTHORITY** (`UnifiedQualityAuthority`) | **OBSERVER ONLY** (Copies scores/findings verbatim) | **VIEWER ONLY** (Displays gauges & tables) |
| **Export Clearance** | **SOVEREIGN AUTHORITY** (`AuthorizedExportGate`) | **OBSERVER ONLY** (Records export_package reference) | **VIEWER ONLY** (Provides download links) |
| **Lifecycle State Transitions** | **SOVEREIGN AUTHORITY** (`ProductionStateMachine`) | **OBSERVER ONLY** (Records timeline of state changes) | **VIEWER ONLY** (Displays status badges) |
| **Repair Mutation & Planning** | **SOVEREIGN AUTHORITY** (`RepairTransactionManager`) | **OBSERVER ONLY** (Records transaction history) | **VIEWER ONLY** (Renders repair charts) |
| **Benchmark Certification** | **SOVEREIGN AUTHORITY** (`CertificationEngine`) | **OBSERVER ONLY** (Records benchmark metadata) | **VIEWER ONLY** (Displays regression alerts) |
| **Golden Corpus Governance** | **SOVEREIGN AUTHORITY** (`AntiLaunderingGuard`) | **OBSERVER ONLY** (Records corpus version) | **VIEWER ONLY** (Shows fixture summary) |
| **Human Review Governance** | **SOVEREIGN AUTHORITY** (`DirectiveSafetyValidator`) | **OBSERVER ONLY** (Records review case pointers) | **VIEWER / INPUT ONLY** (Forms submit to safety gate) |
| **State Mutation** | **EXCLUSIVE** | **FORBIDDEN** (Zero write methods to domain) | **FORBIDDEN** (Zero direct pipeline access) |
| **Persistence Target** | `outputs/` and `final/` | `artifacts/read_models/jobs/{job_id}/` | Ephemeral client memory / DOM |
| **Source of Truth** | **YES** | **NO** (Disposable, rebuildable projection) | **NO** (Rendering client) |

---

## 3. Explicit Prohibitions for Read Model

The Read Model:
1. **MUST NOT calculate quality scores** (e.g., re-computing weighted averages or applying penalties).
2. **MUST NOT issue export approval** (even if all quality scores in the snapshot are 1.0).
3. **MUST NOT transition ProductionStateMachine** (state is strictly read-only).
4. **MUST NOT trigger repair transactions** or select repair strategies.
5. **MUST NOT alter benchmark baselines** or suppress regression alerts.
6. **MUST NOT approve review directives** or bypass `DirectiveSafetyValidator`.
7. **MUST NOT embed raw binary payloads** (PDFs, high-res assets) or clone complete domain ASTs.
8. **MUST NOT block or crash the production pipeline** if projection writing fails.

---

## 4. Failure Isolation Contract

```
+---------------------------+        +---------------------------+
|    Production Pipeline    |        |    Read Model Writer      |
|                           |        |                           |
|  Status: SUCCESS          |        |  Status: WRITE EXCEPTION  |
|  Artifacts: VALID         |   !=   |  Cause: Disk full / IO    |
|  Quality: EXPORT_APPROVED |        |                           |
+---------------------------+        +---------------------------+
              |                                    |
              v                                    v
+---------------------------+        +---------------------------+
| Result: PRODUCTION SUCCEEDS        | Result: OBSERVABILITY     |
| Artifact export proceeds  |        |         DIAGNOSTIC LOGGED |
| Deliverables undamaged    |        | (No pipeline crash)       |
+---------------------------+        +---------------------------+
```

Observability failure must never corrupt or invalidate authoritative production execution.
