"""
Unit tests for CapabilityRegistry and LibraryResolver.
"""

from app.capabilities.registry import CapabilityRegistry
from app.capabilities.resolver import LibraryResolver
from app.libraries import register_all_default_capabilities
from app.blueprints.production import ProductionBlueprint, ProductionRequirement, SemanticIntentSpec, TargetArtifactType


def test_registry_population_and_discovery():
    reg = CapabilityRegistry()
    register_all_default_capabilities(reg)

    assert len(reg.list_all()) >= 8
    
    # Discovery by category
    physics_caps = reg.list_by_category("scientific_visualization")
    assert len(physics_caps) >= 2
    assert any(c.metadata.capability_id == "physics.mechanics.torque_diagram" for c in physics_caps)

    # Discovery by tags
    torque_matches = reg.find(tags=["torque"])
    assert len(torque_matches) >= 1
    assert torque_matches[0].metadata.capability_id == "physics.mechanics.torque_diagram"


def test_resolver_intent_matching():
    reg = CapabilityRegistry()
    register_all_default_capabilities(reg)
    resolver = LibraryResolver(reg)

    req = ProductionRequirement(
        step_id="step_physics_01",
        semantic_type="visualization",
        semantic_intent=SemanticIntentSpec(
            semantic_intent="rotational_force_system",
            domain="physics",
        ),
    )
    prod_bp = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[req],
    )

    results = resolver.resolve(prod_bp)
    assert "step_physics_01" in results
    res = results["step_physics_01"]
    
    # Should resolve to physics.mechanics.torque_diagram
    assert res.selected_capability_id == "physics.mechanics.torque_diagram"
    assert res.score > 20.0
    assert not res.is_fallback


def test_resolver_direct_id_and_fallback():
    reg = CapabilityRegistry()
    register_all_default_capabilities(reg)
    resolver = LibraryResolver(reg)

    # 1. Direct explicit ID
    req1 = ProductionRequirement(
        step_id="step_we",
        semantic_type="worked_example",
        required_capability_id="pedagogy.worked_example",
    )
    # 2. Unknown intent with fallback
    req2 = ProductionRequirement(
        step_id="step_unknown",
        semantic_type="quantum_teleportation_viz",
        fallback_capability_ids=["presentation.concept_introduction"],
    )

    prod_bp = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[req1, req2],
    )

    results = resolver.resolve(prod_bp)
    assert results["step_we"].selected_capability_id == "pedagogy.worked_example"
    assert results["step_we"].score == 100.0

    assert results["step_unknown"].selected_capability_id == "presentation.concept_introduction"
    assert results["step_unknown"].is_fallback is True
