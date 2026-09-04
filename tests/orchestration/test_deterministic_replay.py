"""
Unit tests for Deterministic Replay across multiple runs.
"""

import pytest
from app.orchestration.contracts import JobMetadata, ProductionJobRequest
from app.orchestration.engine import ProductionOrchestrator
from app.orchestration.idempotency import IdempotencyRegistry
from app.orchestration.replay import ExecutionSnapshot, ReplayEngine


def test_deterministic_replay_matches_snapshot():
    IdempotencyRegistry.clear()
    orch = ProductionOrchestrator()

    req = ProductionJobRequest(
        job_id="job_replay_test",
        raw_input="Constructivist scaffolding in educational psychology.",
        metadata=JobMetadata(domain="general", profile="standard", seed=42),
    )

    res1 = orch.run(req)

    snapshot = ExecutionSnapshot(
        snapshot_id="snap_1",
        request=req,
        stage_execution_order=res1.stage_history,
        gate_decisions=[g.decision.value for g in res1.gate_results],
        final_status=res1.status.value,
    )

    # Replay comparison
    replay_res = ReplayEngine.compare_runs(snapshot, res1)
    assert replay_res.is_identical is True
    assert len(replay_res.differences) == 0
