"""
Unit tests for Production Job contracts and enums.
"""

import pytest
from app.orchestration.contracts import (
    ArtifactLifecycleState,
    FailureCategory,
    FailureSeverity,
    GateDecisionEnum,
    JobMetadata,
    JobPriority,
    ProductionGateType,
    ProductionJobRequest,
    ProductionJobStatus,
    StageState,
    WorkflowStageType,
)


def test_job_enums_and_request_contract():
    assert ArtifactLifecycleState.DECLARED == "declared"
    assert ProductionJobStatus.CREATED == "created"
    assert StageState.PENDING == "pending"
    assert JobPriority.HIGH == "high"
    assert FailureCategory.GROUNDING == "grounding"
    assert FailureSeverity.FATAL == "fatal"
    assert ProductionGateType.GROUNDING_GATE == "grounding_gate"
    assert GateDecisionEnum.PASS == "pass"
    assert WorkflowStageType.DIRECTING == "directing"

    req = ProductionJobRequest(
        job_id="job_001",
        raw_input="Torque physics lesson",
        metadata=JobMetadata(domain="physics", profile="standard"),
    )
    assert req.job_id == "job_001"
    assert req.metadata.domain == "physics"
