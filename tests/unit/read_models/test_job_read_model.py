from types import SimpleNamespace
from app.read_models.service import JobReadModelService
from app.read_models.observer import (
    OBSERVATION_TERMINAL,
    ProductionObservationAdapter,
)

def job(status="queued"):
    return SimpleNamespace(job_id="job_phase7", title="Phase 7", model="local", created_at=1.0,
        status=status, current_step="observed", pdf_url=None, pdf_filename=None, percent=0, error=None)

def test_append_is_monotonic_atomic_and_rebuildable(tmp_path):
    service=JobReadModelService(tmp_path)
    first, diagnostic=service.observe_web_job(job())
    second, diagnostic2=service.observe_web_job(job("completed"))
    assert diagnostic is diagnostic2 is None
    assert (first.snapshot_number, second.snapshot_number)==(1,2)
    assert (tmp_path/"job_phase7"/"latest.json").exists()
    (tmp_path/"job_phase7"/"latest.json").unlink()
    rebuilt, diagnostics=service.rebuild_latest("job_phase7")
    assert rebuilt.snapshot_number==2
    assert not diagnostics

def test_corrupted_historical_snapshot_is_isolated(tmp_path):
    service=JobReadModelService(tmp_path)
    service.observe_web_job(job())
    broken=tmp_path/"job_phase7"/"snapshots"/"snapshot_999999.json"
    broken.write_text("not json", encoding="utf-8")
    rebuilt, diagnostics=service.rebuild_latest("job_phase7")
    assert rebuilt.snapshot_number==1
    assert diagnostics[0].code=="CORRUPTED_SNAPSHOT_IGNORED"

def test_manifest_hash_mismatch_is_not_used_as_latest(tmp_path):
    service=JobReadModelService(tmp_path)
    service.observe_web_job(job())
    path=tmp_path/"job_phase7"/"snapshots"/"snapshot_000001.json"
    path.write_text(path.read_text(encoding="utf-8").replace("queued", "tampered"), encoding="utf-8")
    latest, diagnostics=service.rebuild_latest("job_phase7")
    assert latest is None
    assert diagnostics[0].code=="SNAPSHOT_HASH_MISMATCH"

def test_projection_failure_is_returned_not_raised(tmp_path):
    service=JobReadModelService(tmp_path/"read_models")
    bad=SimpleNamespace(job_id="../escape")
    snapshot, diagnostic=service.observe_web_job(bad)
    assert snapshot is None
    assert diagnostic.code=="OBSERVABILITY_PROJECTION_WRITE_FAILED"

def test_identical_observation_is_deduplicated(tmp_path):
    service=JobReadModelService(tmp_path)
    first, error=service.observe_web_job(job("failed"), observation_event="TERMINAL")
    second, error2=service.observe_web_job(job("failed"), observation_event="TERMINAL")
    assert error is error2 is None
    assert first.snapshot_number == second.snapshot_number == 1
    assert len(list((tmp_path/"job_phase7"/"snapshots").glob("*.json"))) == 1

def test_terminal_adapter_does_not_raise_on_writer_failure(tmp_path):
    class BrokenService:
        def observe_web_job(self, *args, **kwargs):
            raise OSError("read-only filesystem")
    result=SimpleNamespace(success=False, job_id="terminal_failure", pdf_path=None, errors=["renderer failed"], export_decision=None)
    ProductionObservationAdapter(service=BrokenService()).observe_material_result(result)

def test_context_terminal_states_are_visible_and_test_isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "read model isolation")
    for state in ("EXPORTED", "BLOCKED", "MANUAL_REVIEW_REQUIRED", "FAILED", "CANCELLED"):
        context=SimpleNamespace(
            job_id=f"terminal_{state.lower()}", artifact_type="HANDOUT", source_metadata={},
            source_input="fixture", output_dir=tmp_path, state=SimpleNamespace(value=state),
            state_machine=SimpleNamespace(history=()), quality_authority_result=None,
            repair_history=(), convergence_state=None, iteration=0, timing_metrics={}, errors=(), warnings=(),
        )
        adapter=ProductionObservationAdapter(service=JobReadModelService(tmp_path/"test"/"jobs"))
        adapter.observe_context(context, OBSERVATION_TERMINAL)
        snapshot=JobReadModelService(tmp_path/"test"/"jobs").rebuild_latest(context.job_id)[0]
        assert snapshot.state.current_state == state
        assert snapshot.state.terminal is True

def test_concurrent_writers_preserve_monotonic_snapshots(tmp_path):
    import concurrent.futures
    service = JobReadModelService(tmp_path)
    
    def write_worker(idx):
        j = SimpleNamespace(
            job_id="concurrent_job", title=f"Worker {idx}", model="local", created_at=1.0,
            status="running", current_step=f"step_{idx}", pdf_url=None, pdf_filename=None,
            percent=idx * 10, error=None,
        )
        return service.observe_web_job(j, observation_event=f"EVENT_{idx}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(write_worker, i) for i in range(10)]
        results = [f.result() for f in futures]

    assert all(diag is None for snap, diag in results)
    rebuilt, diags = service.rebuild_latest("concurrent_job")
    assert not diags
    assert rebuilt.snapshot_number == 10
    assert len(list((tmp_path / "concurrent_job" / "snapshots").glob("snapshot_*.json"))) == 10

def test_observer_never_mutates_context_or_invokes_quality_authority(tmp_path):
    orig_state = "CREATED"
    context = SimpleNamespace(
        job_id="boundary_test_job", artifact_type="PRESENTATION", source_metadata={"title": "Keep"},
        source_input="immutable input", output_dir=tmp_path, state=SimpleNamespace(value=orig_state),
        state_machine=SimpleNamespace(history=()), quality_authority_result=None,
        repair_history=(), convergence_state=None, iteration=0, timing_metrics={}, errors=(), warnings=(),
    )
    adapter = ProductionObservationAdapter(service=JobReadModelService(tmp_path))
    adapter.observe_context(context, "CHECKPOINT")
    
    # Assert context attributes were not modified
    assert context.state.value == orig_state
    assert context.source_input == "immutable input"
    assert context.iteration == 0

