"""
End-to-End Unit & Integration tests for Master Production Orchestrator.
"""

import pytest
from app.orchestration.contracts import (
    JobMetadata,
    ProductionJobRequest,
    ProductionJobStatus,
)
from app.orchestration.engine import ProductionOrchestrator
from app.orchestration.idempotency import IdempotencyRegistry


def test_orchestrator_runs_end_to_end_job():
    IdempotencyRegistry.clear()
    orch = ProductionOrchestrator()

    req = ProductionJobRequest(
        job_id="job_e2e_orch",
        raw_input="Literature review methodologies and synthesis in academic research.",
        metadata=JobMetadata(domain="research_methodology", profile="standard"),
    )

    res = orch.run(req)

    assert res.success is True
    assert res.status == ProductionJobStatus.COMPLETED
    assert len(res.stage_history) >= 4
    assert res.pdf_path is not None
