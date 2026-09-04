"""
Unit tests for individual stage adapters.
"""

import pytest
from app.orchestration.contracts import (
    JobMetadata,
    ProductionJobContext,
    ProductionJobRequest,
    StageState,
)
from app.orchestration.stages.director import DirectorStage
from app.orchestration.stages.validation import RequestValidationStage


def test_validation_stage_fails_on_empty_input():
    stage = RequestValidationStage()
    req = ProductionJobRequest(job_id="j1", raw_input="", metadata=JobMetadata())
    ctx = ProductionJobContext(job_id="j1", request=req)

    res = stage.execute(ctx)
    assert res.state == StageState.FAILED
    assert res.failure is not None
    assert "Empty raw_input" in res.failure.message


def test_director_stage_plans_journey():
    stage = DirectorStage()
    req = ProductionJobRequest(job_id="j2", raw_input="Physics basics", metadata=JobMetadata(domain="physics"))
    ctx = ProductionJobContext(job_id="j2", request=req)

    res = stage.execute(ctx)
    assert res.state == StageState.SUCCEEDED
    assert "material_direction" in ctx.shared_data
