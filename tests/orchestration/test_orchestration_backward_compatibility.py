"""
Unit tests for Backward Compatibility of existing MaterialProductionPipeline.
"""

import pytest
from app.blueprints.content import KnowledgeDomain
from app.orchestration.production_pipeline import MaterialProductionPipeline


@pytest.mark.asyncio
async def test_legacy_production_pipeline_compatibility():
    pipeline = MaterialProductionPipeline()

    raw_input = "Torque mechanics, formula tau = r * F sin(theta), rotational equilibrium."
    res = await pipeline.produce_artifact(
        raw_input=raw_input,
        source_hint="legacy_test.txt",
        domain=KnowledgeDomain.PHYSICS,
        evaluate_quality=True,
    )

    assert res.success is True
    assert res.pdf_path is not None
    assert res.quality_report is not None
