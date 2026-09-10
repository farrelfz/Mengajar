# Phase 7 Production UX & Dashboard Integration

Phase 7 adds a non-authoritative Production Intelligence Cockpit at `/intelligence` and read-only APIs under `/api/intelligence`. It projects existing production facts; it does not own or alter them.

## Architecture

`Production / UQA / repair / benchmark / review domains -> JobReadModelService -> immutable filesystem snapshots -> JobReadQueryService -> cockpit`.

The read model lives at `artifacts/read_models/jobs/{job_id}/` and is intentionally separate from the in-memory web status and authoritative domain objects. `JobReadModelService.observe_production_context` adapts `ArtifactProductionContext`; `observe_web_job` records the existing studio lifecycle. Query responses include diagnostics for absent, stale, and corrupt data.

## Information architecture

The cockpit lists jobs and links to Timeline, Quality, Repair, Convergence, Benchmark, Review, and Artifacts. Each area is a source-labelled projection with progressive forensic JSON detail. Operations can list persisted jobs and use the diagnostic-bearing API; aggregation intentionally returns no invented historical metric.

## Authority boundaries

`UnifiedQualityAuthority` remains the sole source for quality fields copied into `QualityProjection`. The UI exposes no mutation endpoints. `AuthorizedExportGate`, `ProductionStateMachine`, `CertificationEngine`, `RegressionDetector`, `AntiLaunderingGuard`, and `DirectiveSafetyValidator` remain untouched. Review data is displayed as an independent lifecycle; directives remain canonical and safety-gated before a new production run.

## Failure isolation

Writes validate Pydantic contracts, serialize canonical JSON, fsync a temporary file, atomically replace the immutable snapshot, then atomically update manifest and latest pointer. Write exceptions return `OBSERVABILITY_PROJECTION_WRITE_FAILED`; web pipeline execution continues. A missing `latest.json` is reconstructed solely from snapshots.
