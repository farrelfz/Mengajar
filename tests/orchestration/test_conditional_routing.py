"""
Unit tests for centralized Conditional Routing.
"""

import pytest
from app.orchestration.contracts import JobMetadata, ProductionJobContext, ProductionJobRequest
from app.orchestration.routing import ConditionalRouter
from app.quality.contracts import (
    QualityGateDecision,
    QualityGateResult,
    QualityLevel,
    QualityReport,
    QualityScore,
)


def test_routing_diverts_on_quality_failure():
    req = ProductionJobRequest(job_id="j1", raw_input="Sample", metadata=JobMetadata())
    ctx = ProductionJobContext(job_id="j1", request=req)

    # Inject failing quality report
    q_score = QualityScore(overall_score=0.55, dimensional_scores={}, quality_level=QualityLevel.POOR, is_passing=False)
    gate_res = QualityGateResult(decision=QualityGateDecision.FAIL, score=q_score, can_proceed=False, gate_reasoning="Score below threshold")
    ctx.shared_data["quality_report"] = QualityReport(
        job_id="j1",
        overall_score=0.55,
        quality_level=QualityLevel.POOR,
        gate_result=gate_res,
    )

    decision = ConditionalRouter.evaluate_quality_routing(ctx)
    assert decision.should_divert is True
    assert decision.target_stage == "critic_review"
