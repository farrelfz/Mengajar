"""
Adversarial refinement tests: Multi-defect repair, density rebalancing, and sequence alignment.
"""

import pytest
from app.blueprints.content import (
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    KnowledgeDomain,
    LearningObjective,
)
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.blueprints.pedagogical import PedagogicalBlueprint, PedagogicalPattern, PedagogicalStep, SemanticStepType
from app.blueprints.production import ProductionBlueprint, ProductionRequirement, TargetArtifactType
from app.composition.schemas import (
    ContentBlock,
    DocumentComposition,
    PageComposition,
    PageRegion,
    RegionRole,
)
from app.design.schemas import ComponentFamily
from app.director.contracts import LearningJourney, LearningStage, LearningStageType, MaterialStrategyType
from app.intelligence.schemas import DocumentMode
from app.refinement.contracts import ImprovementDecision
from app.refinement.controller import IterativeRefinementController


def test_adversarial_case_wrong_pedagogical_order_refined_to_acceptance():
    content = ContentBlueprint(
        blueprint_id="bp_adv",
        metadata=ContentMetadata(title="Torque Mechanics", domain=KnowledgeDomain.PHYSICS),
        objectives=[LearningObjective(id="o1", objective="Understand torque definition", target_concept="Torque")],
        concepts=[ConceptDefinition(id="c1", name="Torque", formal_definition="Rotational analog of force.")],
    )
    pedagogy = PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="Rationale", sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")])
    prod = ProductionBlueprint(target_artifact=TargetArtifactType.TEACHING_PRESENTATION, requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")])
    bp = SemanticMaterialBlueprint(material_id="m_adv", content=content, pedagogy=pedagogy, production=prod)

    # Intentionally inverted stage order: WORKED_EXAMPLE before CONCEPT_FORMALIZATION
    journey = LearningJourney(
        journey_id="j_adv",
        strategy=MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
        stages=[
            LearningStage(stage_type=LearningStageType.WORKED_EXAMPLE, title="Problem 1", purpose="Solve"),
            LearningStage(stage_type=LearningStageType.CONCEPT_FORMALIZATION, title="Theory", purpose="Define"),
        ],
    )

    page = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content="Torque intro.")],
            )
        },
    )
    comp = DocumentComposition(
        document_id="doc_adv",
        title="Torque",
        mode=DocumentMode.PRESENTATION_16_9,
        theme_reference="default",
        source_blueprint_id="bp_adv",
        pages=[page],
    )

    controller = IterativeRefinementController()
    refined_bundle, history = controller.refine(
        blueprint=bp,
        composition=comp,
        journey=journey,
        target_format="presentation_16_9",
        max_iterations=2,
        artifact_id="art_adv_test",
    )

    # Verify stage order was fixed in refined bundle
    assert refined_bundle.journey.stages[0].stage_type == LearningStageType.CONCEPT_FORMALIZATION
    assert history.final_decision in [ImprovementDecision.ACCEPT, ImprovementDecision.STOP_CONVERGED]
