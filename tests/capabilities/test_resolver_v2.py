"""
Tests for Library Resolver V2: Multi-Axis Scoring, Ranking, and Competition.
"""

from app.capabilities.registry import CapabilityRegistry
from app.capabilities.resolver import LibraryResolver
from app.blueprints.production import ProductionBlueprint, ProductionRequirement, SemanticIntentSpec, TargetArtifactType
from app.libraries import register_all_default_capabilities


def _make_resolver() -> LibraryResolver:
    reg = CapabilityRegistry()
    register_all_default_capabilities(reg)
    return LibraryResolver(registry=reg)


def test_resolver_exact_capability_override():
    """Verify that explicit required_capability_id receives 100.0 score."""
    resolver = _make_resolver()
    pb = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[
            ProductionRequirement(
                step_id="step_1",
                semantic_type="concept",
                required_capability_id="physics.mechanics.torque_diagram",
            )
        ],
    )
    result = resolver.resolve(pb)
    res = result["step_1"]
    assert res.selected_capability_id == "physics.mechanics.torque_diagram"
    assert res.score == 100.0
    assert res.is_fallback is False


def test_resolver_competition_and_domain_affinity():
    """Verify that when multiple capabilities match 'sequence', domain gives winning edge."""
    resolver = _make_resolver()

    # Research Domain -> should pick research pathway / experiment workflow
    pb_research = ProductionBlueprint(
        target_artifact=TargetArtifactType.RESEARCH_PRESENTATION,
        requirements=[
            ProductionRequirement(
                step_id="step_res",
                semantic_type="process",
                semantic_intent=SemanticIntentSpec(
                    semantic_intent="sequence_experiment",
                    domain="research_education",
                ),
            )
        ],
    )
    res_map = resolver.resolve(pb_research)
    winner_res = res_map["step_res"]
    assert "research" in winner_res.selected_capability_id
    assert winner_res.score >= 50.0

    # General Domain -> should pick universal process flow
    pb_general = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[
            ProductionRequirement(
                step_id="step_gen",
                semantic_type="process",
                semantic_intent=SemanticIntentSpec(
                    semantic_intent="process_flow",
                    domain="general",
                ),
            )
        ],
    )
    res_gen = resolver.resolve(pb_general)
    winner_gen = res_gen["step_gen"]
    assert winner_gen.selected_capability_id == "diagram.process_flow"


def test_resolver_partial_information_resilience():
    """Verify that resolver still finds a good match when only partial semantic_type is provided."""
    resolver = _make_resolver()
    pb = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[
            ProductionRequirement(
                step_id="step_partial",
                semantic_type="misconception",
            )
        ],
    )
    result = resolver.resolve(pb)
    res = result["step_partial"]
    assert res.selected_capability_id == "pedagogy.misconception_correction"
    assert res.score >= 40.0
