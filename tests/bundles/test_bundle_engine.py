"""
Tests for Multi-Artifact Bundle Planning, Allocation, Coherence, and Production.
"""

import pytest

from app.blueprints.content import AudienceLevel
from app.bundles import (
    ArtifactBundleProducer,
    ArtifactBundleRequest,
    ArtifactRole,
    BundleCoherenceValidator,
    BundleItemResult,
    BundlePlanner,
    ContentAllocationPolicy,
    ObjectiveCoverageMatrix,
)
from app.orchestration.production_pipeline import MaterialProductionPipeline
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


def test_bundle_planner_and_coverage_matrix():
    planner = BundlePlanner()
    req = ArtifactBundleRequest(
        concept="Torque",
        audience=AudienceLevel.HIGH_SCHOOL,
        artifacts=[
            ArtifactRole.PRESENTATION,
            ArtifactRole.HANDOUT,
            ArtifactRole.WORKSHEET,
            ArtifactRole.ASSESSMENT,
        ],
    )
    objectives, matrix = planner.plan_bundle(req)

    assert len(objectives) == 3
    assert "presentation" in matrix
    assert "handout" in matrix
    assert "worksheet" in matrix
    assert "assessment" in matrix

    # Presentation focuses on LO1
    assert matrix["presentation"]["LO1"] is True
    # Assessment covers LO1, LO2, LO3
    assert matrix["assessment"]["LO1"] is True
    assert matrix["assessment"]["LO2"] is True
    assert matrix["assessment"]["LO3"] is True


def test_coherence_validator_and_redundancy_metrics():
    planner = BundlePlanner()
    objectives = planner.plan_objectives("Torque")
    roles = [ArtifactRole.PRESENTATION, ArtifactRole.HANDOUT, ArtifactRole.WORKSHEET]
    matrix = ObjectiveCoverageMatrix.build_matrix(objectives, roles)

    items = [
        BundleItemResult(role=ArtifactRole.PRESENTATION, format_id="presentation_16_9", pdf_path="pres.pdf", page_count=4, journey_stages=["hook", "concept"]),
        BundleItemResult(role=ArtifactRole.HANDOUT, format_id="a4_portrait", pdf_path="hand.pdf", page_count=4, journey_stages=["context", "formalization", "worked_example"]),
        BundleItemResult(role=ArtifactRole.WORKSHEET, format_id="a4_portrait", pdf_path="work.pdf", page_count=3, journey_stages=["worked_example", "guided_practice", "independent_practice"]),
    ]

    is_valid, red_score, comp_score, warnings = BundleCoherenceValidator.validate_bundle(items, objectives, matrix)
    assert is_valid is True
    assert red_score == 0.0
    assert comp_score == 1.0


@pytest.mark.asyncio
async def test_bundle_producer_end_to_end():
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)
    producer = ArtifactBundleProducer(pipeline=pipeline)

    req = ArtifactBundleRequest(
        concept="Classical Mechanics Torque",
        audience=AudienceLevel.HIGH_SCHOOL,
        duration_minutes=45,
        artifacts=[
            ArtifactRole.PRESENTATION,
            ArtifactRole.HANDOUT,
            ArtifactRole.WORKSHEET,
            ArtifactRole.ASSESSMENT,
        ],
        raw_input="# Torque\nRotational force equilibrium.",
    )

    bundle_res = await producer.produce_bundle(req, output_dir="outputs/bundles_test")

    assert bundle_res.coherence_valid is True
    assert len(bundle_res.items) == 4
    assert bundle_res.items[0].role == ArtifactRole.PRESENTATION
    assert bundle_res.items[1].role == ArtifactRole.HANDOUT
    assert bundle_res.items[2].role == ArtifactRole.WORKSHEET
    assert bundle_res.items[3].role == ArtifactRole.ASSESSMENT
    assert bundle_res.redundancy_score == 0.0
    assert bundle_res.complementarity_score == 1.0
