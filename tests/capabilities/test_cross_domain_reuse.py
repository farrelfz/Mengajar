"""
Tests for Cross-Domain Capability Family Reuse and Future Domain Extensibility (Chemistry).
"""

from app.capabilities.contracts import Capability, CapabilityMetadata, CapabilityOutput, CapabilityRenderer, CapabilitySpec
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.resolver import LibraryResolver
from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)
from app.blueprints.production import ProductionBlueprint, ProductionRequirement, SemanticIntentSpec, TargetArtifactType
from app.libraries import register_all_default_capabilities


def test_process_flow_family_cross_domain_reuse():
    """Verify that PROCESS_VISUALIZATION family spans multiple domains."""
    reg = CapabilityRegistry()
    register_all_default_capabilities(reg)

    process_caps = reg.list_by_family(CapabilityFamily.PROCESS_VISUALIZATION)
    assert len(process_caps) >= 3

    cap_ids = {c.metadata.capability_id for c in process_caps}
    assert "diagram.process_flow" in cap_ids
    assert "research.scientific.reasoning_pathway" in cap_ids
    assert "research.experiment_workflow" in cap_ids


def test_comparative_reasoning_family_cross_domain_reuse():
    """Verify that COMPARATIVE_REASONING family spans Pedagogy, Research, and Universal domains."""
    reg = CapabilityRegistry()
    register_all_default_capabilities(reg)

    comp_caps = reg.list_by_family(CapabilityFamily.COMPARATIVE_REASONING)
    assert len(comp_caps) >= 3

    cap_ids = {c.metadata.capability_id for c in comp_caps}
    assert "pedagogy.misconception_correction" in cap_ids
    assert "research.problem.gap_matrix" in cap_ids
    assert "universal.comparison_matrix" in cap_ids


def test_future_chemistry_domain_extensibility_without_core_modification():
    """Simulate future Chemistry Domain capability registration, resolution, and rendering."""
    reg = CapabilityRegistry()
    register_all_default_capabilities(reg)

    class ReactionEnergySpec(CapabilitySpec):
        activation_energy_kj: float = 45.0
        delta_h_kj: float = -120.0
        reaction_name: str = "Exothermic Combustion"

    class ReactionEnergyRenderer(CapabilityRenderer[ReactionEnergySpec]):
        def validate_spec(self, spec: ReactionEnergySpec) -> bool:
            return True
        def measure(self, spec: ReactionEnergySpec, context=None):
            return {"height_px": 280}
        def render(self, spec: ReactionEnergySpec, context=None) -> CapabilityOutput:
            return CapabilityOutput(
                capability_id="chemistry.reaction.energy_profile",
                output_format="svg",
                rendered_content=f"<svg><text>{spec.reaction_name} ΔH={spec.delta_h_kj} kJ</text></svg>",
            )

    chemistry_cap = Capability(
        metadata=CapabilityMetadata(
            capability_id="chemistry.reaction.energy_profile",
            category="chemistry",
            display_name="Reaction Energy Profile Diagram",
            description="Energy curve showing activation barrier and enthalpy change.",
            semantic_tags=["chemistry", "reaction", "activation_energy", "enthalpy", "exothermic", "endothermic"],
            domain="chemistry",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.SPATIAL_SYSTEMS,
                primary_intent=SemanticIntent.EXPLAIN,
                supported_intents=[SemanticIntent.ANALYZE],
                structure=InformationStructure.TRANSFORMATION,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.ANNOTATED_DIAGRAM,
                density=DensityProfile.FOCUSED,
            ),
        ),
        spec_model=ReactionEnergySpec,
        renderer=ReactionEnergyRenderer(),
        parameter_extractor=lambda step, mat: {"reaction_name": "Methane Combustion", "delta_h_kj": -890.0},
    )

    # Register in registry without any core modification
    reg.register(chemistry_cap)

    # Discover via multi-axis query
    found = reg.find(domain="chemistry", semantic_intent=SemanticIntent.EXPLAIN)
    assert any(c.metadata.capability_id == "chemistry.reaction.energy_profile" for c in found)

    # Resolve requirement in Chemistry domain
    resolver = LibraryResolver(registry=reg)
    pb = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[
            ProductionRequirement(
                step_id="step_chem",
                semantic_type="chemistry",
                semantic_intent=SemanticIntentSpec(semantic_intent="activation_energy", domain="chemistry"),
            )
        ],
    )
    res_map = resolver.resolve(pb)
    assert res_map["step_chem"].selected_capability_id == "chemistry.reaction.energy_profile"
    assert res_map["step_chem"].score >= 45.0
