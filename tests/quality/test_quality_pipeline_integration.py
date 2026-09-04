"""
End-to-End integration test for MaterialProductionPipeline with Quality Evaluation.
"""

from pathlib import Path
import pytest

from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.orchestration.production_pipeline import MaterialProductionPipeline
from app.quality.contracts import QualityGateDecision
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


@pytest.mark.asyncio
async def test_pipeline_with_automated_quality_evaluation(tmp_path: Path):
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)

    res = await pipeline.produce_artifact(
        raw_input="# Research Methodology: Problem Formulation\nIdentifying clear research gaps in academic literature.",
        source_hint="research_problem.md",
        domain=KnowledgeDomain.RESEARCH_METHODOLOGY,
        audience=AudienceLevel.UNDERGRADUATE,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        output_dir=tmp_path,
        output_filename="research_problem_evaluated",
        target_format="presentation_16_9",
        director_enabled=True,
        evaluate_quality=True,
    )

    assert res.success is True
    assert res.quality_report is not None
    assert res.quality_gate is not None
    assert res.quality_gate.decision in [QualityGateDecision.PASS, QualityGateDecision.PASS_WITH_WARNINGS]
    assert res.quality_gate.can_proceed is True
    assert res.quality_report.overall_score >= 0.75
    assert len(res.quality_report.metrics) >= 3
