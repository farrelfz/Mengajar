"""
Unit tests for Backward Compatibility when no learner profile is supplied.
"""

import pytest
from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.orchestration.production_pipeline import MaterialProductionPipeline
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


@pytest.mark.asyncio
async def test_pipeline_with_none_learner_profile_retains_legacy_behavior():
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)

    res = await pipeline.produce_artifact(
        raw_input="# Mechanics: Energy\nConservation of mechanical energy.",
        source_hint="energy.md",
        domain=KnowledgeDomain.PHYSICS,
        audience=AudienceLevel.HIGH_SCHOOL,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        output_dir="outputs/test_compat",
        output_filename="test_compat_out",
        target_format="presentation_16_9",
        director_enabled=True,
        evaluate_quality=True,
        learner_profile=None,  # Explicitly None
    )

    assert res.success is True
    assert res.personalization_report is None  # Legacy behavior: no personalization report
    assert res.material_blueprint is not None
