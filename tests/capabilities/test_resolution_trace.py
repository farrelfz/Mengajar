"""
Tests for Resolver V2 ResolutionTrace and Explainable Scoring.
"""

from app.capabilities.registry import CapabilityRegistry
from app.capabilities.resolver import LibraryResolver
from app.blueprints.production import ProductionBlueprint, ProductionRequirement, SemanticIntentSpec, TargetArtifactType
from app.libraries import register_all_default_capabilities


def test_resolution_trace_contains_breakdown_and_candidates():
    """Verify that resolution outputs inspectable ScoreBreakdown and ranked candidates."""
    reg = CapabilityRegistry()
    register_all_default_capabilities(reg)
    resolver = LibraryResolver(registry=reg)

    pb = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[
            ProductionRequirement(
                step_id="step_compare",
                semantic_type="comparison",
                semantic_intent=SemanticIntentSpec(
                    semantic_intent="compare",
                    domain="general",
                ),
            )
        ],
    )

    plan = resolver.resolve_material_plan(pb)
    assert len(plan.step_resolutions) == 1

    res = plan.step_resolutions[0]
    assert res.score > 0
    assert len(res.candidates) >= 2

    # Check breakdown fields
    bd = res.breakdown
    assert bd.intent_score == 30.0
    assert "semantic_intent" in bd.matched_dimensions

    # Check candidate ordering is strictly descending by score
    scores = [c.score for c in res.candidates]
    assert scores == sorted(scores, reverse=True)

    # Winner matches top candidate
    assert res.selected_capability_id == res.candidates[0].capability_id
    assert res.score == res.candidates[0].score
