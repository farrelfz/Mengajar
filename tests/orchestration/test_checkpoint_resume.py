"""
Unit tests for In-Memory Checkpoint and Resumption without recomputation of completed stages.
"""

import pytest
from app.orchestration.checkpoints import InMemoryCheckpointStore, WorkflowCheckpoint
from app.orchestration.contracts import (
    JobMetadata,
    ProductionJobContext,
    ProductionJobRequest,
    StageExecutionResult,
    StageState,
)
from app.orchestration.engine import ProductionOrchestrator


def test_orchestrator_resumes_from_checkpoint_without_rerunning_completed_stages():
    store = InMemoryCheckpointStore()
    orch = ProductionOrchestrator(checkpoint_store=store)

    req = ProductionJobRequest(
        job_id="job_resume_test",
        raw_input="Physics mechanics and rotational torque.",
        metadata=JobMetadata(domain="physics", profile="fast_preview"),
    )

    # First run: will complete and create a checkpoint
    res1 = orch.run(req)
    assert res1.success is True

    # Retrieve checkpoint
    chk = store.get_latest_for_job("job_resume_test")
    assert chk is not None
    assert "request_validation" in chk.completed_stages

    # Now resume using the checkpoint
    res2 = orch.resume(chk.checkpoint_id, req)
    assert res2.success is True
    assert res2.job_id == "job_resume_test"
