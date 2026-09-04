"""
Unit tests for Production Quality Gates.
"""

import pytest
from app.grounding.contracts import (
    GroundingFinding,
    GroundingReport,
    GroundingScore,
    GroundingTrace,
)
from app.orchestration.contracts import (
    GateDecisionEnum,
    JobMetadata,
    ProductionGateType,
    ProductionJobContext,
    ProductionJobRequest,
)
from app.orchestration.gates import ProductionGate


def test_grounding_gate_blocks_on_contradictions():
    req = ProductionJobRequest(job_id="j1", raw_input="Sample", metadata=JobMetadata())
    ctx = ProductionJobContext(job_id="j1", request=req)

    g_score = GroundingScore(coverage=0.5, support_strength=0.5, authority=0.8, freshness=1.0, consistency=0.0, overall_score=0.4)
    g_trace = GroundingTrace(trace_id="trc_1")
    g_rep = GroundingReport(
        claims_total=2,
        claims_contradicted=1,
        score=g_score,
        findings=[GroundingFinding(severity="critical", category="contradiction", message="Contradiction in physics")],
        trace=g_trace,
    )
    ctx.shared_data["grounding_report"] = g_rep

    res = ProductionGate.evaluate_grounding_gate(ctx)
    assert res.gate_type == ProductionGateType.GROUNDING_GATE
    assert res.decision == GateDecisionEnum.BLOCK
    assert "contradictions" in res.reasoning
