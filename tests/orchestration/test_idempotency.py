"""
Unit tests for Idempotency and duplicate request result reuse.
"""

import pytest
from app.orchestration.contracts import JobMetadata, ProductionJobRequest
from app.orchestration.engine import ProductionOrchestrator
from app.orchestration.idempotency import IdempotencyRegistry


def test_idempotency_reuses_result_for_identical_request():
    IdempotencyRegistry.clear()
    orch = ProductionOrchestrator()

    req1 = ProductionJobRequest(
        job_id="job_idemp_1",
        raw_input="Research variables and methodology.",
        metadata=JobMetadata(domain="research_methodology", profile="fast_preview", seed=100),
    )

    res1 = orch.run(req1)
    assert res1.success is True

    # Same request with different job_id but identical payload/seed
    req2 = ProductionJobRequest(
        job_id="job_idemp_2",
        raw_input="Research variables and methodology.",
        metadata=JobMetadata(domain="research_methodology", profile="fast_preview", seed=100),
    )

    res2 = orch.run(req2)
    # Reused cached result from first execution
    assert res2.job_id == res1.job_id
    assert res2.execution_duration_ms == res1.execution_duration_ms
