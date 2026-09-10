# Phase 7 Final Hardening — Forensic Entry-Point Coverage Audit

**Audit scope:** Phase 0 only. This document records current repository evidence as of the audit and makes no implementation or authority change. Source discovery used CodeGraph followed by repository-wide caller searches.

## A. Authoritative generation entry points

| Entry point | Invocation path / artifact scope | Production context | Current Phase 7 observation |
|---|---|---:|---|
| `app/web/server.py:_run_job_pipeline` via `POST /api/generate` | `MaterialProductionPipeline.produce_artifact`; presentation, handout, worksheet, KTI | No `ArtifactProductionContext`; web `JobState` | **Yes**, queued, started, terminal web-status snapshots via `_observe_job` |
| `app/cli/shared.py:_run_pipeline_async`, reached by `kir` and `mengajar` `cmd_generate` | `MaterialProductionPipeline.produce_artifact`; requested CLI artifact/format | No | No |
| `app/bundles/producer.py:ArtifactBundleProducer.produce_bundle` | one `MaterialProductionPipeline.produce_artifact` per bundle role; presentation/handout currently mapped | No | No |
| `app/orchestration/production_orchestrator.py:ProductionOrchestrator.produce` | canonical `ProductionRequest`; presentation, handout, worksheet, scientific document | **Yes**, `ArtifactProductionContext` at lines 157–163 | No automatic call to `observe_production_context` |
| `app/benchmarking/benchmark_runner.py:BenchmarkGeneralizationRunner.run_target` | canonical orchestrator across corpus artifact types | Yes | No |
| `scripts/replay_convergence_benchmark.py:run_single_benchmark` | intends canonical orchestration, but calls non-existent `produce_artifact` on `ProductionOrchestrator` | Would be Yes if corrected | No; currently stale/broken entrypoint |
| benchmark scripts using `MaterialProductionPipeline` | `generate_adaptive_benchmark`, `generate_personalization_benchmark`, `generate_capability_family_benchmark`, `generate_multiformat_benchmark`, `generate_research_education_benchmark`, `generate_quality_benchmark`, `generate_quality_adversarial_benchmark`, `generate_generative_critic_benchmark`, `generate_preflight_benchmark`, `generate_quality_evaluation_benchmark`, `generate_iterative_refinement_benchmark`, `generate_capability_grammar_benchmark`, `generate_all_visual_benchmarks`, `generate_director_benchmark`, `generate_massive_library_benchmark` | No | No |
| orchestration benchmark scripts | `generate_observability_benchmark`, `generate_orchestration_benchmark`; instantiate the orchestrator | Canonical context is expected | No evidence of read-model observation |
| production-pipeline test callers | rendering, quality, director, personalization, integration, bundle, regression, format, and backward-compatibility suites | usually No | No; however default read-model root is globally shared if future hooks are added naively |
| canonical-orchestrator test callers | orchestration, observability, convergence integration suites | Yes | No |

The searched direct callers are recorded in `rg` evidence: `app/web/server.py:533`, `app/cli/shared.py:574`, `app/bundles/producer.py:62`, `app/benchmarking/benchmark_runner.py:80`, 18 MaterialProductionPipeline benchmark scripts, and the listed test suites. `scripts/replay_convergence_benchmark.py:55` is a concrete API-drift finding: `ProductionOrchestrator` exposes `produce`, not `produce_artifact`.

## B/C. Lifecycle coverage matrix

`CREATED`, `RUNNING`, etc. below mean an **observable persisted milestone**, not merely an in-memory pipeline action.

| Entry point class | Created | Running | Rendered | Quality evaluated | Repair | Terminal | Read model persisted | Environment | Coverage |
|---|---|---|---|---|---|---|---|---|---|
| Web API | queued web state | started web state | no distinct checkpoint | only if available in returned result | no | completed/blocked/failed | yes | implicit default / production-intended | PARTIALLY_OBSERVED |
| CLI generation | no | no | no | no | no | no | no | unspecified | PARTIALLY_OBSERVED |
| Bundle generation | no | no | no | no | no | no | no | unspecified | PARTIALLY_OBSERVED |
| Canonical orchestrator | no | no | no | no | no | no | no | unspecified | PARTIALLY_OBSERVED |
| Benchmark runner/scripts | no | no | no | no | no | no | no | benchmark output only | INTENTIONALLY_EXCLUDED only in effect, not enforced |
| Test execution | no | no | no | no | no | no | no | test output/temp roots | INTENTIONALLY_EXCLUDED only in effect, not enforced |
| Stale replay script | n/a | n/a | n/a | n/a | n/a | n/a | no | benchmark | INTENTIONALLY_EXCLUDED pending API-drift repair |

The canonical orchestrator itself has authoritative transitions for `CREATED` through render, UQA evaluation, repair, terminal quality halt, export, and exceptions (`production_orchestrator.py:157–415`), but has no observational boundary. Therefore none of those actual transitions are persisted to Phase 7 today.

## D–P. Risks and coverage findings

- **Duplicate-observation risk:** web observation occurs at creation, start, and terminal with no projection-hash deduplication. Repeated calls create append-only snapshots even when state/evidence is unchanged. The `JobReadModelService.append` method increments from manifest count, so duplicates are currently possible.
- **Missing paths:** all non-web generators and the canonical orchestrator have no automatic observation. `observe_production_context` exists but has no caller.
- **Benchmark/test pollution:** current benchmark and test paths do not invoke the service, hence do not currently pollute. However the service default root is `artifacts/read_models/jobs`, has no environment dimension, and a future common hook would pollute production without isolation.
- **Failed web jobs:** yes, `_run_job_pipeline` invokes `_observe_job` after the handled failure/blocked branch and exception branch. A failure before `JobState` creation is not observable.
- **Manual-review terminal jobs:** not correctly represented by the web adapter: its terminal set omits `manual_review_required`; its native pipeline maps only completed/blocked/failed. Canonical orchestrator manual-review outcomes are never observed.
- **Blocked jobs:** web branch persists a `blocked` snapshot. Canonical blocked outcomes are not persisted.
- **Exported jobs:** web uses `completed`, not authoritative `EXPORTED`; canonical exported outcomes are not persisted.
- **Cancelled jobs:** neither web workflow nor canonical integration emits a read-model cancellation snapshot.
- **Race/order risks:** no lock spans manifest read, snapshot-number allocation, write, and manifest update. Concurrent observers for one job can select the same next number. Atomic individual-file writes prevent partial JSON readers, but do not provide multi-writer sequencing. `latest.json` can be temporarily stale relative to a newly written snapshot.
- **Job-ID collision risks:** web IDs use slug plus integer seconds (`server.py:607`), so same-title requests in one second can collide. Material pipeline defaults to `job_{source stem}` (`production_pipeline.py:167`), also collision-prone across repeated runs.
- **Stale projection risk:** `get_job` trusts parseable `latest.json`; it rebuilds only on missing/invalid latest, not when latest is older than a valid higher snapshot. Hash verification is performed in rebuild, not on the normal latest read.

## Q. Rebuild authority check

`rebuild_latest` only reads snapshot files and atomically rewrites `latest.json`/`manifest.json` in the read-model root. It does not invoke pipeline, renderer, repair, LLM, UQA, export, benchmark, or review code. It does not modify authoritative production artifacts. This boundary is correct, subject to the stale-latest/hash qualification above.

## R. API exposure audit

The discovered intelligence routes are four `GET` routes only: `/api/intelligence/jobs`, `/api/intelligence/jobs/{job_id}`, `/api/intelligence/jobs/{job_id}/{section}`, and `/intelligence`. No Phase 7 POST/PUT/PATCH/DELETE route was found. `JobReadModelService._dir` rejects slash and backslash, which blocks ordinary traversal, but query methods call it without catching `ValueError`; malformed/encoded identifier requests can become server errors rather than a clean client diagnostic. There is no explicit absolute-path, URL-decoding, length, or character allowlist policy.

## S. Static dashboard resilience audit

`app/web/static/intelligence.html` handles zero jobs and uses `not observed` for absent quality fields. It assumes every list entry contains `identity`, `metadata`, `state`, and `quality`; malformed server data can break client rendering. It offers forensic JSON links but no explicit `Unavailable` state for missing benchmark/review/artifact fields, no loading/rebuild state, no pagination/virtualisation for large history, and no user-facing stale-pointer diagnostic. The query layer does return diagnostics for missing/corrupt data.

## T. Test environment audit

`pyproject.toml` is the authoritative packaging configuration. It declares `pytest>=8.2,<9.0`, `pytest-asyncio`, and `pytest-cov` in the `dev` extra; `requirements.txt` intentionally contains runtime-only dependencies and no pytest. No lockfile, requirements-dev file, Poetry, uv, tox, or CI workflow was found. The workspace has two virtual environments:

- `./.venv/bin/python -m pytest --version` → **pytest 8.4.2**; imports `structlog`, FastAPI, and Pydantic successfully.
- `./venv/bin/python -m pytest --version` → pytest 9.1.1, outside the project’s declared `<9.0` range.
- System `/usr/bin/python` lacks pytest and `structlog`; this explains the previous non-certifying test attempt.

The intended command for subsequent phases is therefore `./.venv/bin/python -m pytest ...`, after confirming the virtualenv remains consistent with `pyproject.toml`.

## Phase 0 conclusion

Phase 7 is **not ready for certification**. The audit establishes one partially observed web path, a capable but uncalled canonical context adapter, missing environment segregation and idempotency, incomplete terminal semantics, concurrency/stale-pointer risks, and an unexecuted test suite. These findings define the minimal hardening work for phases F1–F10.
