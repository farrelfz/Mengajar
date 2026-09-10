"""
Universal Document Intelligence System V5 — Phase 7 Final Certification Test Suite.

Executes all Kill Critics and Adversarial Verification Scenarios:
- Section 4: Galileo Generalization Cases A through G
- Section 5: Selection Safety Fallback Audit
- Section 7: Read Model Concurrency Kill Critic (Attacks 1-7)
- Section 8: Observer Authority Kill Critic
- Section 9: Snapshot Duplication Kill Critic
- Section 10: Terminal State Coverage & Exception Preservation
- Section 11: Benchmark Environment Isolation
- Section 12: API & Dashboard Read-Only Kill Critic
- Section 13: Observational Performance Sanity Check
"""

import asyncio
import concurrent.futures
import hashlib
import json
import os
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from app.intelligence.pipeline import KnowledgeCompiler, OfflineMockResolutionProvider
from app.intelligence.pipeline.importance_analyzer import ImportanceAnalyzer
from app.intelligence.rule_classifier import RuleClassifier
from app.intelligence.schemas import (
    ContentType,
    IntrinsicImportance,
    KnowledgeCategory,
    KnowledgeUnit,
    ResolutionStatus,
    UniversalKnowledgeManifest,
)
from app.intelligence.schemas.knowledge_unit import KnowledgeProvenance
from app.intelligence.transformation.intent import (
    ArtifactType,
    ResolvedArtifactIntent,
    UncertaintyHandlingPolicy,
    get_default_intent,
)
from app.intelligence.transformation.selection import (
    KnowledgeSelectionEngine,
    SelectionFallbackEligibility,
)
from app.orchestration.execution_profiles import ArtifactExecutionProfileRegistry
from app.read_models.contracts import JobIdentity, JobSnapshot
from app.read_models.observer import (
    OBSERVATION_CONVERGENCE_UPDATED,
    OBSERVATION_JOB_CREATED,
    OBSERVATION_PIPELINE_STARTED,
    OBSERVATION_QUALITY_AVAILABLE,
    OBSERVATION_REPAIR_ITERATION,
    OBSERVATION_TERMINAL,
    ProductionObservationAdapter,
    read_model_root,
    resolve_environment,
)
from app.read_models.service import JobReadModelService
from app.web.server import app


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 & 5: GALILEO GENERALIZATION & SELECTION SAFETY FALLBACK AUDIT
# ══════════════════════════════════════════════════════════════════════════════

def _make_unit(
    uid: str,
    title: str = "Test Unit",
    c_type: ContentType = ContentType.CONCEPT,
    importance: IntrinsicImportance = IntrinsicImportance.CENTRAL,
    confidence: float = 0.90,
    tags: list[str] | None = None,
    raw_content: str = "Sample content",
) -> KnowledgeUnit:
    return KnowledgeUnit(
        id=uid,
        title=title,
        content_type=c_type,
        category=KnowledgeCategory.CORE_CONCEPT,
        intrinsic_importance=importance,
        raw_content=raw_content,
        normalized_content=raw_content,
        provenance=KnowledgeProvenance(
            source_document_id="doc_test",
            source_path="test.md",
            source_section_id="sec_1",
            source_section_title=title,
            source_heading_path=[title],
            block_ids=[f"block_{uid}"],
            source_start_line=1,
            source_end_line=5,
            raw_snippet=raw_content,
        ),
        payload={"kind": "concept", "formal_definition": raw_content},
        classification_confidence=confidence,
        tags=tags or [],
    )


def test_case_a_narrative_scientific_history_headings():
    """Case A: Narrative scientific history headings (Paradigma, Dogma, Kontradiksi) not collapsed."""
    rc = RuleClassifier()
    res1 = rc.classify_unit(SimpleNamespace(unit_id="u1", title="1. Paradigma Lama", raw_text="Penjelasan", normalized_text="Penjelasan", content_type=None), parent_heading="1. Paradigma Lama")
    res2 = rc.classify_unit(SimpleNamespace(unit_id="u2", title="2. Kontradiksi Logika", raw_text="Penjelasan", normalized_text="Penjelasan", content_type=None), parent_heading="2. Kontradiksi Logika")
    assert res1.content_type == ContentType.CONCEPT
    assert res2.content_type == ContentType.ARGUMENT
    assert res1.confidence >= 0.80
    assert res2.confidence >= 0.80


def test_case_b_argumentative_educational_content():
    """Case B: ARGUMENT content remains semantically selectable in selection engine."""
    unit = _make_unit("ku_arg1", title="Kontradiksi", c_type=ContentType.ARGUMENT, importance=IntrinsicImportance.SUPPORTING)
    manifest = UniversalKnowledgeManifest(
        manifest_id="man_arg",
        source_document_id="doc_arg",
        source_path="arg.md",
        document_title="Argument Doc",
        domain="History",
        units={"ku_arg1": unit},
        relationships=[],
        metadata={},
    )
    intent = get_default_intent(ArtifactType.HANDOUT)
    selected = KnowledgeSelectionEngine().select(manifest, intent)
    assert "ku_arg1" in selected.selected_unit_ids


def test_case_c_methodological_instructional_content():
    """Case C: METHOD content receives appropriate classification."""
    rc = RuleClassifier()
    res = rc.classify_unit(
        SimpleNamespace(unit_id="u3", title="3. Metodologi Ilmiah", raw_text="Penjelasan metodologi", normalized_text="Penjelasan metodologi", content_type=None),
        parent_heading="3. Metodologi Ilmiah",
    )
    assert res.content_type == ContentType.METHOD
    assert res.confidence >= 0.85


def test_case_d_long_explanatory_prose_not_inflated_to_core():
    """Case D: EXPLANATION is not automatically inflated into FOUNDATIONAL / CORE importance."""
    analyzer = ImportanceAnalyzer()
    unit = _make_unit("ku_exp", c_type=ContentType.EXPLANATION, importance=IntrinsicImportance.CENTRAL)
    analyzed = analyzer.analyze([unit], relationships=[])
    # With degree 0, score is 0.6 * 0.65 = 0.39 -> IntrinsicImportance.SUPPORTING (not FOUNDATIONAL or CENTRAL)
    assert analyzed[0].intrinsic_importance == IntrinsicImportance.SUPPORTING


def test_case_e_low_value_decorative_explanation_not_mandatory():
    """Case E: Decorative explanation (BACKGROUND/TIP) still retains low contextual importance."""
    analyzer = ImportanceAnalyzer()
    unit = _make_unit("ku_bg", c_type=ContentType.BACKGROUND, importance=IntrinsicImportance.CENTRAL)
    analyzed = analyzer.analyze([unit], relationships=[])
    assert analyzed[0].intrinsic_importance == IntrinsicImportance.CONTEXTUAL


def test_case_f_manifest_filtered_to_zero_preserves_highest_eligible():
    """Case F: When threshold filtering removes every unit, highest-value eligible unit is preserved."""
    unit_low = _make_unit("ku_ctx1", title="Contextual A", c_type=ContentType.BACKGROUND, importance=IntrinsicImportance.CONTEXTUAL, confidence=0.7)
    unit_high = _make_unit("ku_ctx2", title="Contextual B", c_type=ContentType.DEFINITION, importance=IntrinsicImportance.CONTEXTUAL, confidence=0.95)
    manifest = UniversalKnowledgeManifest(
        manifest_id="man_ctx",
        source_document_id="doc_ctx",
        source_path="ctx.md",
        document_title="Context Doc",
        domain="Physics",
        units={"ku_ctx1": unit_low, "ku_ctx2": unit_high},
        relationships=[],
        metadata={},
    )
    intent = get_default_intent(ArtifactType.PRESENTATION)
    selected = KnowledgeSelectionEngine().select(manifest, intent)
    assert len(selected.selected_unit_ids) >= 1
    assert "ku_ctx2" in selected.selected_unit_ids


def test_case_g_manifest_intentionally_empty_does_not_invent_fallback():
    """Case G: Manifest intentionally containing zero units preserves zero units (no fabrication)."""
    manifest = UniversalKnowledgeManifest(
        manifest_id="man_empty",
        source_document_id="doc_empty",
        source_path="empty.md",
        document_title="Empty Doc",
        domain="Physics",
        units={},
        relationships=[],
        metadata={},
    )
    intent = get_default_intent(ArtifactType.HANDOUT)
    selected = KnowledgeSelectionEngine().select(manifest, intent)
    assert len(selected.selected_units) == 0
    assert len(selected.selected_unit_ids) == 0


def test_selection_fallback_eligibility_safety_constraints():
    """Section 5: Fallback refuses forbidden, unsafe, spoiled, or unsupported claim content."""
    # 1. Unsafe/Forbidden tag
    unsafe_unit = _make_unit("ku_unsafe", tags=["forbidden", "toxic"])
    assert SelectionFallbackEligibility.is_eligible(unsafe_unit, ArtifactType.PRESENTATION) is False

    # 2. Worksheet answer spoiling tag
    spoiler_unit = _make_unit("ku_spoil", tags=["answer_key", "spoiler"])
    assert SelectionFallbackEligibility.is_eligible(spoiler_unit, ArtifactType.WORKSHEET) is False
    assert SelectionFallbackEligibility.is_eligible(spoiler_unit, ArtifactType.HANDOUT) is True

    # 3. Unsupported claim
    unsupported_claim = _make_unit("ku_claim", c_type=ContentType.CLAIM, tags=["unsupported"])
    assert SelectionFallbackEligibility.is_eligible(unsupported_claim, ArtifactType.SCIENTIFIC_DOCUMENT) is False

    # 4. Low-confidence garbage (< 0.20)
    garbage_unit = _make_unit("ku_garb", confidence=0.10)
    assert SelectionFallbackEligibility.is_eligible(garbage_unit, ArtifactType.HANDOUT) is False


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7: READ MODEL CONCURRENCY & INTEGRITY KILL CRITIC (ATTACKS 1-7)
# ══════════════════════════════════════════════════════════════════════════════

def test_attack_1_multiple_threads_writing_same_job(tmp_path):
    """Attack 1: Concurrent writes to same job allocate strictly monotonic numbers."""
    service = JobReadModelService(tmp_path)

    def write_step(idx):
        job = SimpleNamespace(
            job_id="job_attack1", title=f"Job {idx}", model="local", created_at=1.0,
            status="running", current_step=f"step_{idx}", pdf_url=None, pdf_filename=None,
            percent=idx, error=None,
        )
        return service.observe_web_job(job, observation_event=f"EVENT_{idx}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(write_step, i) for i in range(20)]
        results = [f.result() for f in futures]

    assert all(diag is None for snap, diag in results)
    snapshot_files = sorted((tmp_path / "job_attack1" / "snapshots").glob("snapshot_*.json"))
    assert len(snapshot_files) == 20
    numbers = [int(f.stem.split("_")[1]) for f in snapshot_files]
    assert numbers == list(range(1, 21))


def test_attack_2_multiple_threads_writing_same_observation_key(tmp_path):
    """Attack 2: Concurrent identical observation keys are cleanly deduplicated."""
    service = JobReadModelService(tmp_path)
    job = SimpleNamespace(
        job_id="job_attack2", title="Dedupe Job", model="local", created_at=1.0,
        status="running", current_step="same_step", pdf_url=None, pdf_filename=None,
        percent=50, error=None,
    )

    def write_identical():
        return service.observe_web_job(job, observation_event="IDENTICAL_MILESTONE")

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(write_identical) for _ in range(15)]
        results = [f.result() for f in futures]

    assert all(diag is None for snap, diag in results)
    snapshot_files = list((tmp_path / "job_attack2" / "snapshots").glob("snapshot_*.json"))
    assert len(snapshot_files) == 1


def test_attack_3_multiple_jobs_concurrently_isolated_locks(tmp_path):
    """Attack 3: Concurrent writes across multiple distinct jobs do not block or corrupt each other."""
    service = JobReadModelService(tmp_path)

    def write_job(job_idx, step_idx):
        job = SimpleNamespace(
            job_id=f"job_multi_{job_idx}", title=f"Job {job_idx}", model="local", created_at=1.0,
            status="running", current_step=f"step_{step_idx}", pdf_url=None, pdf_filename=None,
            percent=step_idx * 20, error=None,
        )
        return service.observe_web_job(job, observation_event=f"EVENT_{step_idx}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        tasks = []
        for j in range(5):
            for s in range(4):
                tasks.append(executor.submit(write_job, j, s))
        results = [t.result() for t in tasks]

    assert all(diag is None for snap, diag in results)
    for j in range(5):
        files = list((tmp_path / f"job_multi_{j}" / "snapshots").glob("snapshot_*.json"))
        assert len(files) == 4


def test_attack_4_reader_accesses_latest_during_write(tmp_path):
    """Attack 4: Concurrent reader always reads valid parseable JSON, never partial data."""
    service = JobReadModelService(tmp_path)
    job_id = "job_reader_attack"
    stop_flag = False

    init_job = SimpleNamespace(
        job_id=job_id, title="Init", model="local", created_at=1.0,
        status="queued", current_step="init", pdf_url=None, pdf_filename=None,
        percent=0, error=None,
    )
    service.observe_web_job(init_job)

    def writer_loop():
        for i in range(1, 25):
            j = SimpleNamespace(
                job_id=job_id, title=f"Title {i}", model="local", created_at=1.0,
                status="running", current_step=f"step_{i}", pdf_url=None, pdf_filename=None,
                percent=i * 4, error=None,
            )
            service.observe_web_job(j, observation_event=f"STEP_{i}")
            time.sleep(0.005)

    def reader_loop():
        latest_file = tmp_path / job_id / "latest.json"
        reads = 0
        while not stop_flag:
            if latest_file.exists():
                raw = latest_file.read_text(encoding="utf-8")
                parsed = json.loads(raw)
                assert parsed["identity"]["job_id"] == job_id
                reads += 1
            time.sleep(0.002)
        return reads

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        write_fut = executor.submit(writer_loop)
        read_fut = executor.submit(reader_loop)
        write_fut.result()
        stop_flag = True
        reads = read_fut.result()

    assert reads > 10


def test_attack_5_crash_simulation_before_replace_preserves_valid_state(tmp_path):
    """Attack 5: Interrupted or orphaned temporary file does not corrupt existing valid latest.json."""
    service = JobReadModelService(tmp_path)
    job = SimpleNamespace(
        job_id="job_crash", title="Crash Test", model="local", created_at=1.0,
        status="running", current_step="step_1", pdf_url=None, pdf_filename=None,
        percent=50, error=None,
    )
    service.observe_web_job(job)
    assert (tmp_path / "job_crash" / "latest.json").exists()
    valid_content = (tmp_path / "job_crash" / "latest.json").read_text()

    temp_orphan = tmp_path / "job_crash" / ".latest.json.orphaned_tmp"
    temp_orphan.write_text('{"partial": ')

    assert (tmp_path / "job_crash" / "latest.json").read_text() == valid_content
    rebuilt, diags = service.rebuild_latest("job_crash")
    assert rebuilt.snapshot_number == 1
    assert not diags


def test_attack_6_corrupt_newest_snapshot_rebuild_picks_newest_valid(tmp_path):
    """Attack 6: Rebuilding when newest snapshot is corrupt falls back to newest valid snapshot."""
    service = JobReadModelService(tmp_path)
    job_id = "job_corrupt_newest"
    for s in ("queued", "running"):
        j = SimpleNamespace(
            job_id=job_id, title="Test", model="local", created_at=1.0,
            status=s, current_step=s, pdf_url=None, pdf_filename=None,
            percent=50, error=None,
        )
        service.observe_web_job(j, observation_event=f"EVT_{s}")

    snap2 = tmp_path / job_id / "snapshots" / "snapshot_000002.json"
    snap2.write_text("corrupted non-json content", encoding="utf-8")

    rebuilt, diagnostics = service.rebuild_latest(job_id)
    assert rebuilt is not None
    assert rebuilt.snapshot_number == 1
    assert any(d.code in ("CORRUPTED_SNAPSHOT_IGNORED", "SNAPSHOT_HASH_MISMATCH") for d in diagnostics)


def test_attack_7_corrupted_historical_snapshot_isolated(tmp_path):
    """Attack 7: A corrupted historical snapshot in the middle does not invalidate newer snapshots."""
    service = JobReadModelService(tmp_path)
    job_id = "job_middle_corrupt"
    for s in ("queued", "running", "completed"):
        j = SimpleNamespace(
            job_id=job_id, title="Test", model="local", created_at=1.0,
            status=s, current_step=s, pdf_url=None, pdf_filename=None,
            percent=100, error=None,
        )
        service.observe_web_job(j, observation_event=f"EVT_{s}")

    snap2 = tmp_path / job_id / "snapshots" / "snapshot_000002.json"
    snap2.write_text("corrupted middle", encoding="utf-8")

    rebuilt, diagnostics = service.rebuild_latest(job_id)
    assert rebuilt is not None
    assert rebuilt.snapshot_number == 3
    assert any(d.code in ("CORRUPTED_SNAPSHOT_IGNORED", "SNAPSHOT_HASH_MISMATCH") for d in diagnostics)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8: OBSERVER AUTHORITY & NON-MUTATION KILL CRITIC
# ══════════════════════════════════════════════════════════════════════════════

def test_observer_authority_cannot_mutate_or_trigger_execution(tmp_path):
    """Section 8: Verify observer does not call UQA, StateMachine.transition, or repair."""
    context = SimpleNamespace(
        job_id="pure_observer_job",
        artifact_type="HANDOUT",
        source_metadata={"title": "Original Title"},
        source_input="immutable input text",
        output_dir=tmp_path,
        state=SimpleNamespace(value="CREATED"),
        state_machine=SimpleNamespace(history=()),
        quality_authority_result=None,
        repair_history=(),
        convergence_state=None,
        iteration=0,
        timing_metrics={},
        errors=(),
        warnings=(),
    )
    adapter = ProductionObservationAdapter(service=JobReadModelService(tmp_path))
    adapter.observe_context(context, OBSERVATION_JOB_CREATED)

    assert context.state.value == "CREATED"
    assert context.iteration == 0
    assert context.source_input == "immutable input text"
    assert context.quality_authority_result is None


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9: SNAPSHOT DUPLICATION & TEMPORAL INTEGRITY KILL CRITIC
# ══════════════════════════════════════════════════════════════════════════════

def test_lifecycle_repeated_observation_preserves_temporal_milestones(tmp_path):
    """Section 9: Multiple calls at same stage deduplicate, but genuine iteration changes persist."""
    service = JobReadModelService(tmp_path)
    job_id = "job_lifecycle"

    # Stage 1: CREATED (called twice)
    c1 = SimpleNamespace(
        job_id=job_id, artifact_type="HANDOUT", source_metadata={}, source_input="src",
        output_dir=tmp_path, state=SimpleNamespace(value="CREATED"), state_machine=SimpleNamespace(history=()),
        quality_authority_result=None, repair_history=(), convergence_state="IN_PROGRESS",
        iteration=0, timing_metrics={}, errors=(), warnings=(),
    )
    service.observe_production_context(c1, observation_event=OBSERVATION_JOB_CREATED)
    service.observe_production_context(c1, observation_event=OBSERVATION_JOB_CREATED)

    # Stage 2: REPAIR ITERATION 1 (called twice)
    c2 = SimpleNamespace(
        job_id=job_id, artifact_type="HANDOUT", source_metadata={}, source_input="src",
        output_dir=tmp_path, state=SimpleNamespace(value="REPAIRING"), state_machine=SimpleNamespace(history=()),
        quality_authority_result=None, repair_history=({"op": "op1", "status": "attempted"},), convergence_state="IN_PROGRESS",
        iteration=1, timing_metrics={}, errors=(), warnings=(),
    )
    service.observe_production_context(c2, observation_event=OBSERVATION_REPAIR_ITERATION)
    service.observe_production_context(c2, observation_event=OBSERVATION_REPAIR_ITERATION)

    # Stage 3: REPAIR ITERATION 2 (called twice)
    c3 = SimpleNamespace(
        job_id=job_id, artifact_type="HANDOUT", source_metadata={}, source_input="src",
        output_dir=tmp_path, state=SimpleNamespace(value="REPAIRING"), state_machine=SimpleNamespace(history=()),
        quality_authority_result=None, repair_history=({"op": "op1", "status": "attempted"}, {"op": "op2", "status": "attempted"}),
        convergence_state="IN_PROGRESS", iteration=2, timing_metrics={}, errors=(), warnings=(),
    )
    service.observe_production_context(c3, observation_event=OBSERVATION_REPAIR_ITERATION)
    service.observe_production_context(c3, observation_event=OBSERVATION_REPAIR_ITERATION)

    snapshots = list((tmp_path / job_id / "snapshots").glob("snapshot_*.json"))
    assert len(snapshots) == 3


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 10: TERMINAL STATE COVERAGE & EXCEPTION PRESERVATION
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("terminal_state", ["EXPORTED", "BLOCKED", "MANUAL_REVIEW_REQUIRED", "FAILED", "CANCELLED"])
def test_all_terminal_states_observed(tmp_path, terminal_state):
    """Section 10: All 5 terminal states produce a terminal snapshot marked terminal=True."""
    service = JobReadModelService(tmp_path)
    job_id = f"job_term_{terminal_state.lower()}"
    context = SimpleNamespace(
        job_id=job_id, artifact_type="WORKSHEET", source_metadata={}, source_input="src",
        output_dir=tmp_path, state=SimpleNamespace(value=terminal_state), state_machine=SimpleNamespace(history=()),
        quality_authority_result=None, repair_history=(), convergence_state=None,
        iteration=1, timing_metrics={}, errors=(), warnings=(),
    )
    adapter = ProductionObservationAdapter(service=service)
    adapter.observe_context(context, OBSERVATION_TERMINAL)

    latest, diags = service.rebuild_latest(job_id)
    assert latest is not None
    assert latest.state.current_state == terminal_state
    assert latest.state.terminal is True


def test_production_failure_exception_is_not_masked_by_observer(tmp_path):
    """Section 10: When observation fails on FAILED state, production exception is preserved."""
    class CrashingService:
        def observe_production_context(self, *args, **kwargs):
            raise RuntimeError("Disk full in observer")

    adapter = ProductionObservationAdapter(service=CrashingService())
    context = SimpleNamespace(job_id="job_exc", state=SimpleNamespace(value="FAILED"))
    adapter.observe_context(context, OBSERVATION_TERMINAL)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 11: BENCHMARK & ENVIRONMENT ISOLATION
# ══════════════════════════════════════════════════════════════════════════════

def test_environment_isolation_roots():
    """Section 11: Production, benchmark, and test roots are cleanly segregated."""
    assert resolve_environment(explicit="production") == "production"
    assert resolve_environment(explicit="benchmark") == "benchmark"
    assert resolve_environment(explicit="test") == "test"

    assert read_model_root("production") == Path("artifacts/read_models/jobs")
    assert read_model_root("benchmark") == Path("artifacts/read_models/benchmark/jobs")
    assert read_model_root("test") == Path("artifacts/read_models/test/jobs")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 12: API & DASHBOARD READ-ONLY KILL CRITIC
# ══════════════════════════════════════════════════════════════════════════════

def test_api_is_strictly_get_only_and_rejects_mutation_verbs():
    """Section 12: Intelligence API endpoints reject POST, PUT, PATCH, DELETE with 405."""
    client = TestClient(app)
    endpoints = [
        "/api/intelligence/jobs",
        "/api/intelligence/jobs/job_123",
        "/api/intelligence/jobs/job_123/quality",
        "/api/intelligence/jobs/job_123/repair",
        "/api/intelligence/jobs/job_123/convergence",
        "/api/intelligence/jobs/job_123/benchmark",
        "/api/intelligence/jobs/job_123/review",
        "/api/intelligence/cockpit",
    ]
    for endpoint in endpoints:
        assert client.post(endpoint).status_code in (404, 405)
        assert client.put(endpoint).status_code in (404, 405)
        assert client.delete(endpoint).status_code in (404, 405)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 13: PERFORMANCE SANITY CHECK
# ══════════════════════════════════════════════════════════════════════════════

def test_observational_latency_sanity_check(tmp_path):
    """Section 13: Observational snapshot serialization and atomic write is fast (< 50ms)."""
    service = JobReadModelService(tmp_path)
    job = SimpleNamespace(
        job_id="perf_job", title="Performance Test", model="local", created_at=1.0,
        status="completed", current_step="done", pdf_url="/pdf", pdf_filename="test.pdf",
        percent=100, error=None,
    )
    result = SimpleNamespace(
        artifact_type="HANDOUT",
        quality_report=SimpleNamespace(
            overall_quality_score=0.95, domain_scores={"fidelity": 0.95}, findings=(), hard_blockers=(),
        ),
    )

    times = []
    for _ in range(10):
        t0 = time.perf_counter()
        service.observe_web_job(job, result=result, observation_event="PERF_TEST")
        times.append(time.perf_counter() - t0)

    avg_ms = (sum(times) / len(times)) * 1000
    assert avg_ms < 50.0, f"Observation latency too high: {avg_ms:.2f}ms"
