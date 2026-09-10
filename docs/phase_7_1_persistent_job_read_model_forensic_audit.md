# Universal Document Intelligence System V5
# Phase 7.1 — Persistent Job Read Model Foundation
# Forensic Architecture Audit & CQRS Projection Strategy

**Status**: PHASE 7.1 FORENSIC AUDIT — COMPLETE  
**Audit Date**: 2026-09-08  
**Auditor Role**: Principal Software Architect, Staff Backend Engineer, Production Observability Engineer, Domain-Driven Design Specialist  
**Hard Constraint**: Strictly a forensic audit. Zero implementation code, pipeline modifications, or authority bypasses allowed in this phase.

---

## Executive Summary

Phase 7.1 addresses the primary architectural vulnerability discovered in Phase 7.0: **the lack of an immutable, deterministic, file-backed persistent read model for production jobs**. While the repository boasts mature, rigorous Level-0 quality authorities (UnifiedQualityAuthority), strict state transitions (ProductionStateMachine), multi-layer closed-loop repair actuators, benchmark certification guards (AntiLaunderingGuard), and human review governance (Phase 6), the observational telemetry and lifecycle progression of each job currently exist primarily as ephemeral in-memory state in RAM or as disparate output files in outputs/.

This audit establishes the blueprint for a **CQRS-inspired Read Model Projection layer** obeying the non-negotiable rule: **"Observation Without Authority"**. The Read Model is not an authority, not a decision engine, and not a duplicate domain store. It is an append-safe, disposable, rebuildable projection of authoritative production artifacts and events.

---

## Forensic Audit Findings: Dimensions A through X

### A. Production Job Creation Lifecycle
1. **Entry Points & Request Contracts**:
   - ProductionRequest (app/orchestration/production_orchestrator.py:101): Frozen dataclass specifying raw_input, artifact_type, output_dir, job_id, output_filename, source_filename, max_repair_iterations, resolution_provider, progress_callback.
   - ProductionOutcome (app/orchestration/production_orchestrator.py:115): Authoritative terminal return structure.
   - MaterialProductionPipeline (app/orchestration/production_pipeline.py:517): High-level multi-stage generation facade.
   - _run_job_pipeline() (app/web/server.py:419): Web server background worker invoking MaterialProductionPipeline.
2. **Job Identity & Artifact Identity Assignment**:
   - Web Server: Canonical job ID generated in app/web/server.py:592: job_id = f"job_{clean_slug}_{int(time.time())}".
   - Production Orchestrator: Canonical fallback generated in app/orchestration/production_orchestrator.py:150: job_id = request.job_id or f"job_{norm_type.lower()}_{int(time.time())}".
   - Benchmark Runner: Generated in app/benchmarking/benchmark_runner.py: job_id = f"bench_{case_id}_{int(time.time())}".
   - Artifact Identity: Derived as artifact_name = request.output_filename or f"{norm_type.lower()}_artifact".
3. **Safe Snapshot Emission Anchors**:
   - Emission Anchor 1 (Initialization): Immediately after ArtifactProductionContext instantiation (CREATED).
   - Emission Anchor 2 (Stage Milestones): Following KNOWLEDGE_READY, INTENT_READY, BLUEPRINT_READY, RENDERED.
   - Emission Anchor 3 (Initial Evaluation): Following QUALITY_EVALUATED (Iteration 0).
   - Emission Anchor 4 (Repair Iterations): At the conclusion of each repair cycle in _run_repair_loop() immediately after version_manager.record_iteration().
   - Emission Anchor 5 (Terminal States): At EXPORTED, MANUAL_REVIEW_REQUIRED, BLOCKED, FAILED, and CANCELLED.

### B. Production State Machine
1. **State Machine Architecture**: Defined in app/orchestration/production_state.py. ProductionState enum exposes 21 distinct lifecycle states. ProductionStateMachine.LEGAL_TRANSITIONS enforces an explicit transition whitelist. History is captured immutably via StateTransitionRecord dataclass in self._history.
2. **Persisted States & Terminal Immutability**: All 21 states are observable and can be recorded into the Read Model timeline. Terminal states: EXPORTED, MANUAL_REVIEW_REQUIRED, BLOCKED, FAILED, CANCELLED. Terminal states have an empty transition set (set()), guaranteeing mathematical immutability. Semantics of MANUAL_REVIEW_REQUIRED and BLOCKED remain untouched.
3. **Observation Mechanism**: ProductionStateMachine already exposes history: Tuple[StateTransitionRecord, ...]. The Read Model extracts this tuple without calling .transition() or altering internal state.

### C. Production Context
1. **Context Inspection (app/orchestration/production_context.py)**: ArtifactProductionContext holds identity, domain artifacts, quality & governance results, and timing metrics.
2. **Authoritative Sources vs. Projected Data**: The Read Model must NOT clone large objects (UniversalKnowledgeManifest, raw ASTs, full PDF binary). It extracts metadata, state enum, scalar scores, blocker arrays, timing numbers, and references files via absolute paths and SHA-256 digests.

### D. UnifiedQualityAuthority (UQA)
1. **UQA Contracts (app/quality/contracts/authority.py, decisions.py)**: UnifiedQualityReport: decision (ExportDecision), overall_quality_score, domain_scores, dimension_scores, hard_blockers, warnings, findings, provenance_graph.
2. **Mandatory Invariant**: READ MODEL NEVER CALCULATES QUALITY. The Read Model projector blindly copies authoritative scores and counts. No re-weighting, no re-averaging, no recalculation.

### E. Repair System
1. **Repair Entities**: RepairTransactionRecord (app/quality/repair/transaction.py:33), ConvergenceCheckResult (app/orchestration/convergence_controller.py:44), repair_forensics.json, repair_forensics.md, convergence_failure_report.md.
2. **Read Model Integration**: The Read Model projects total attempts, committed/rolled back counts, last mutation scope, current root cause, stagnation reason, and pointers (SourceReference) to the detailed forensics files.

### F. Benchmark System
1. **Benchmark Contracts (app/benchmarking/)**: BenchmarkEvaluation, CertificationEngine, CertificationDecision, GoldenCorpusRegistry, AntiLaunderingGuard.
2. **Read Model Projection**: Captures is_benchmark_job, fixture_id, corpus_version, certification_decision. The Read Model holds ZERO authority to mutate baselines or approve certification.

### G. Human Review System (Phase 6)
1. **Review Infrastructure (app/review/)**: ReviewCase, ReviewQueueRegistry, ReviewStateMachine, ReviewProvenanceLedger.
2. **Job Read Model Linkage**: When a job terminates in MANUAL_REVIEW_REQUIRED, the Read Model records review_required: bool = True, review_case_id, review_queue_path. Read Model never modifies ReviewCase or issues directives.

### H. Observability
1. **Observability Contracts (app/observability/contracts.py)**: ObservabilityReport, SpanRecord, MetricRecord, ErrorRecord, RunSummary.
2. **Read Model Strategy**: Summary projection of total duration, stage timings dictionary, error count, last error message. Reference pointer to observability_manifest.json if emitted.

### I. Existing Persistence Patterns
1. **Pattern Audit**: app/review/queue/registry.py uses temporary file in the target directory followed by os.replace for atomic JSON write. app/orchestration/versioning.py uses chunked SHA-256 hash calculation. app/review/provenance/immutable_ledger.py uses append-only JSONL.
2. **Adoption in Phase 7.1**: Use established .tmp_<uuid> + os.replace atomic replacement pattern and SHA-256 digest computation.

### J. Artifact Directory Conventions
1. **Repository Layout**: artifacts/ holds system governance and registries (artifacts/review_queue/, artifacts/review_provenance/). outputs/ holds output deliverables (outputs/web_runs/, outputs/production_orchestration/).
2. **Read Model Placement**: Canonical persistent location: artifacts/read_models/jobs/{job_id}/ with manifest.json, snapshots/ (snapshot_000001.json, etc.), and latest.json atomic pointer.

### K. Existing API & Server Boundaries
1. **Server Analysis (app/web/server.py)**: GET /api/jobs/{job_id} currently reads from in-memory _JOBS dictionary.
2. **Phase 7.1 Separation**: JobReadModelRegistry provides read-only inspection methods: get_job(), get_latest_snapshot(), list_jobs().

### L. Concurrency & Filesystem Safety
1. **Atomic Write Protocol**: Serialize -> write temp file snapshots/.tmp_snap_{uuid}.json -> flush & fsync -> compute SHA-256 -> os.replace() to snapshot_{seq:06d}.json -> atomic update latest.json.
2. **Concurrent Readers**: os.replace() guarantees POSIX atomicity on Linux. Readers opening latest.json read either previous valid JSON or new valid JSON, never partial data.

### M. Historical Versioning
- Snapshots are strictly append-only with monotonic sequence numbers (000001, 000002, ...). Historical snapshots are never overwritten or deleted.

### N. Failure Handling & Isolation
- **Hard Rule**: Observability write failure MUST NOT cause production pipeline failure.
- If AtomicJobSnapshotWriter raises an exception, it is caught, logged as OBSERVABILITY_PROJECTION_WRITE_FAILED, and pipeline execution continues unaffected.

### O. Rebuildability
- A job Read Model can be reconstructed from authoritative outputs (outputs/production_orchestration/{job_id}/final/manifest.json, quality_authority_report.json, convergence_failure_report.md, iteration_0/, iteration_1/).
- JobReadModelRebuilder can scan existing job folders and reconstruct valid snapshot_000001.json and latest.json without running generation or LLMs.

### P. Schema Evolution
- Every snapshot and manifest includes schema_version: str (initial: "1.0.0"). Schema status enum: SUPPORTED, MIGRATABLE, UNSUPPORTED.

### Q. Staleness Detection
- ReadModelStalenessDetector inspects: (1) Does latest.json point to a snapshot matching current pipeline state? (2) Have referenced files on disk changed since generation? (3) Is latest.json missing? Exposes FRESH, STALE, PARTIALLY_STALE, CORRUPTED, UNKNOWN.

### R. Snapshot Consistency Contract
- Coherence boundary: each snapshot tracks iteration: int across quality, repair, and state. Inconsistency detection detects if quality_iteration != repair_iteration != state_iteration. Exposes CONSISTENT, CROSS_ITERATION, PARTIALLY_CONSISTENT, UNKNOWN.

### S. Performance & Storage Invariants
- Snapshot files remain lightweight (< 100 KB typical). Large artifacts (PDF, HTML, images, raw source) are NEVER duplicated inside snapshot JSON. Snapshots record SourceReference with path, sha256_hash, size_bytes, authority.

### T. Authority Boundary Matrix
- Read Model MAY: project, summarize, link, detect staleness/inconsistency, verify integrity.
- Read Model MUST NEVER: calculate quality, approve export, mutate state, invoke repairs, modify baselines, change review verdicts.

### U. Backward Compatibility
- Existing core modules remain 100% backward compatible. Zero changes to UnifiedQualityAuthority, AuthorizedExportGate, ProductionStateMachine, RepairSafetyInvariants, CertificationEngine, AntiLaunderingGuard, ReviewStateMachine.

### V. Test Architecture
- Unit tests in tests/unit/dashboard/: test_job_read_model_contracts.py, test_atomic_snapshot_writer.py, test_read_model_registry.py, test_staleness_detector.py, test_snapshot_consistency.py, test_read_model_integrity.py, test_read_model_rebuilder.py, test_read_model_adversarial.py.
- Integration tests in tests/integration/dashboard/: test_production_read_model_projection.py.

### W. Security & Integrity
- Cryptographic SHA-256 checksum embedded in every snapshot header. Manual tampering triggers IntegrityVerificationError.

### X. Minimal Intervention Strategy
- Implement ObservationAdapter / ProductionObserver pattern. ProductionOrchestrator optionally accepts an observer callback or hooks an observation step at terminal transitions and iteration completions. If no observer provided, production behaves identically to Phase 6.

---

## Audit Conclusion & Stop Notice
The forensic architecture audit is complete. All 24 dimensions (A–X) are verified against the actual repository structure.

**STOP CONDITION APPLIED**: In accordance with the prompt directive, no production code or pipeline implementation has been created. Awaiting explicit authorization before proceeding to Phase 7.1 implementation.
