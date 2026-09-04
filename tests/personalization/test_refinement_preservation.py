"""
Unit tests for Refinement preserving learner personalization constraints.
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
from app.blueprints.pedagogical import PedagogicalBlueprint, PedagogicalPattern
from app.blueprints.production import ProductionBlueprint, TargetArtifactType
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
from app.refinement.controller import IterativeRefinementController


def test_refinement_preserves_novice_scaffolding_stages():
    content = ContentBlueprint(
        blueprint_id="bp_nov_scaffold",
        metadata=ContentMetadata(title="Torque", domain=KnowledgeDomain.PHYSICS),
        objectives=[LearningObjective(id="o1", objective="Understand torque")],
        concepts=[ConceptDefinition(id="c1", name="Torque", formal_definition="Force times lever arm.")],
    )
    bp = SemanticMaterialBlueprint(material_id="m1", content=content, pedagogy=PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="R"), production=ProductionBlueprint(target_artifact=TargetArtifactType.TEACHING_PRESENTATION))

    # Novice journey with hook and scaffolding
    journey = LearningJourney(
        journey_id="j_nov",
        strategy=MaterialStrategyType.CONCRETE_TO_ABSTRACT,
        stages=[
            LearningStage(stage_type=LearningStageType.HOOK, title="Door Knob Intuition", purpose="Intuition"),
            LearningStage(stage_type=LearningStageType.CONCEPT_FORMALIZATION, title="Torque Equation", purpose="Define"),
            LearningStage(stage_type=LearningStageType.GUIDED_PRACTICE, title="Practice", purpose="Scaffolded Practice"),
        ],
    )

    page = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content="Door knob.")],
            )
        },
    )
    comp = DocumentComposition(document_id="d1", title="Torque", mode=DocumentMode.PRESENTATION_16_9, theme_reference="default", source_blueprint_id="bp_nov_scaffold", pages=[page])

    controller = IterativeRefinementController()
    refined_bundle, history = controller.refine(
        blueprint=bp,
        composition=comp,
        journey=journey,
        target_format="presentation_16_9",
        max_iterations=1,
    )

    # Invariant: Hook and scaffolding stages remain preserved in refined journey
    stage_types = [s.stage_type.value for s in refined_bundle.journey.stages]
    assert "hook" in stage_types
    assert "concept_formalization" in stage_types
