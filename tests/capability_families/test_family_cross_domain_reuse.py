"""
Tests proving Cross-Domain Family Template Reuse and Zero-Core Modification Extensibility.
"""

from app.blueprints.content import ContentBlueprint, ContentMetadata, KnowledgeDomain
from app.blueprints.pedagogical import PedagogicalBlueprint, PedagogicalStep, SemanticStepType
from app.blueprints.production import ProductionBlueprint, ProductionRequirement, TargetArtifactType
from app.capabilities.contracts import CapabilityMetadata, RenderTarget
from app.capabilities.families.contracts import ProcessSpec, ProcessStage
from app.capabilities.families.factory import register_family_capability
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


def test_one_template_reused_across_three_domains():
    """
    Proves that LinearProcessTemplate ('process.linear') is reused by:
    1. Domain: Research Education ('research.experiment_workflow')
    2. Domain: Physics ('physics.problem_solving_flow')
    3. Domain: Pedagogy / General ('pedagogy.learning_journey')
    WITHOUT creating three separate renderer classes.
    """
    reg = CapabilityRegistry()

    # 1. Research Education Capability
    cap_research = register_family_capability(
        registry=reg,
        capability_id="research.experiment_workflow_family",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="research.experiment_workflow_family",
            category="research_education",
            display_name="Experiment Workflow Pipeline",
            description="Protocol steps for empirical investigation",
            semantic_tags=["experiment", "protocol", "workflow", "procedure"],
            supported_artifacts=["presentation", "document"],
            domain="research_education",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.SCAFFOLD,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 2. Physics Problem Solving Flow
    cap_physics = register_family_capability(
        registry=reg,
        capability_id="physics.problem_solving_flow",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="physics.problem_solving_flow",
            category="physics",
            display_name="Physics Problem Solving Flow",
            description="Stepwise protocol: Identify -> FBD -> Equilibrium -> Solve",
            semantic_tags=["physics", "problem_solving", "equilibrium_protocol"],
            supported_artifacts=["presentation", "document"],
            domain="physics",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.WORKED_EXAMPLE,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 3. Pedagogy Learning Journey
    cap_pedagogy = register_family_capability(
        registry=reg,
        capability_id="pedagogy.learning_journey",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="pedagogy.learning_journey",
            category="pedagogy",
            display_name="Learning Journey Roadmap",
            description="Instructional roadmap for unit mastery",
            semantic_tags=["learning_journey", "roadmap", "pedagogy"],
            supported_artifacts=["presentation", "document"],
            domain="general",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.SCAFFOLD,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    assert len(reg.list_by_family(CapabilityFamily.PROCESS_VISUALIZATION)) == 3

    # Render all three using their domain-specific parameters
    spec_res = ProcessSpec(
        title="Plant Growth Protocol",
        stages=[ProcessStage(id="1", label="Sterilize"), ProcessStage(id="2", label="Inoculate")],
    )
    spec_phys = ProcessSpec(
        title="Rotational Statics Protocol",
        stages=[ProcessStage(id="1", label="Draw FBD"), ProcessStage(id="2", label="Sum Torques")],
    )
    spec_ped = ProcessSpec(
        title="Calculus Unit Map",
        stages=[ProcessStage(id="1", label="Limits"), ProcessStage(id="2", label="Derivatives")],
    )

    out_res = cap_research.renderer.render(spec_res)
    out_phys = cap_physics.renderer.render(spec_phys)
    out_ped = cap_pedagogy.renderer.render(spec_ped)

    assert "Plant Growth Protocol" in out_res.rendered_content
    assert "Rotational Statics Protocol" in out_phys.rendered_content
    assert "Calculus Unit Map" in out_ped.rendered_content


def test_future_chemistry_domain_extensibility_via_family_template():
    """
    Proves that a new domain (CHEMISTRY) can add a complex semantic capability
    ('chemistry.reaction_pathway') using an existing family template ('process.linear')
    with ZERO modifications to core pipeline code.
    """
    reg = CapabilityRegistry()

    # Register Chemistry reaction pathway using LinearProcessTemplate
    chem_cap = register_family_capability(
        registry=reg,
        capability_id="chemistry.reaction_pathway",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="chemistry.reaction_pathway",
            category="chemistry",
            display_name="Chemical Reaction Pathway",
            description="Multi-step reaction mechanism from Reactants to Intermediates to Products",
            semantic_tags=["reaction_mechanism", "activation_step", "catalysis", "chemistry"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="chemistry",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # Resolution test in Chemistry domain
    resolver = LibraryResolver(registry=reg)
    prod_bp = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[
            ProductionRequirement(
                step_id="step_chem_rxn",
                semantic_type="chemistry",
                semantic_intent={
                    "semantic_intent": "reaction_mechanism",
                    "domain": "chemistry",
                },
            )
        ],
    )

    res_map = resolver.resolve(prod_bp)
    assert "step_chem_rxn" in res_map
    res = res_map["step_chem_rxn"]
    assert res.selected_capability_id == "chemistry.reaction_pathway"
    assert res.family == CapabilityFamily.PROCESS_VISUALIZATION.value
    assert res.template_selected == "process.linear"
    assert not res.is_fallback
