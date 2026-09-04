"""
Unit tests for Refinement determinism across 10 consecutive executions.
"""

import copy
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
from app.refinement.controller import IterativeRefinementController


def test_refinement_determinism_across_10_runs():
    content = ContentBlueprint(
        blueprint_id="bp_det",
        metadata=ContentMetadata(title="Torque Mechanics", domain=KnowledgeDomain.PHYSICS),
        objectives=[LearningObjective(id="o1", objective="Understand torque definition", target_concept="Torque")],
        concepts=[ConceptDefinition(id="c1", name="Torque", formal_definition="Rotational force analog.")],
    )
    pedagogy = PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="Rationale", sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")])
    prod = ProductionBlueprint(target_artifact=TargetArtifactType.TEACHING_PRESENTATION, requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")])
    bp = SemanticMaterialBlueprint(material_id="m_det", content=content, pedagogy=pedagogy, production=prod)

    journey = LearningJourney(
        journey_id="j_det",
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
        document_id="doc_det",
        title="Torque",
        mode=DocumentMode.PRESENTATION_16_9,
        theme_reference="default",
        source_blueprint_id="bp_det",
        pages=[page],
    )

    controller = IterativeRefinementController()
    results = [
        controller.refine(
            blueprint=copy.deepcopy(bp),
            composition=copy.deepcopy(comp),
            journey=copy.deepcopy(journey),
            target_format="presentation_16_9",
            max_iterations=2,
            artifact_id="art_det",
        )
        for _ in range(10)
    ]

    first_bundle, first_hist = results[0]
    for idx, (bundle, hist) in enumerate(results[1:], start=2):
        assert hist.total_iterations == first_hist.total_iterations, f"Iterations mismatch on run {idx}"
        assert hist.final_decision == first_hist.final_decision, f"Decision mismatch on run {idx}"
        assert hist.stop_reason == first_hist.stop_reason, f"Stop reason mismatch on run {idx}"
        assert len(hist.plans) == len(first_hist.plans), f"Plans count mismatch on run {idx}"
