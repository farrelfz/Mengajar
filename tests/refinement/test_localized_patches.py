"""
Unit tests for Localized Patch transformations without destructive regeneration.
"""

import pytest
from app.blueprints.content import ContentBlueprint, ContentMetadata
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
from app.refinement.contracts import (
    RefinedArtifactBundle,
    RefinementAction,
    RefinementIntent,
    RefinementScope,
    RefinementTargetLayer,
)
from app.refinement.patches import (
    CapabilityReplacementPatch,
    DensitySplitPatch,
    PedagogicalSequencePatch,
    RedundancyDeduplicationPatch,
)


def test_pedagogical_sequence_patch_reorders_stages_immutably():
    journey = LearningJourney(
        journey_id="j1",
        strategy=MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
        stages=[
            LearningStage(stage_type=LearningStageType.WORKED_EXAMPLE, title="Problem 1", purpose="Solve"),
            LearningStage(stage_type=LearningStageType.CONCEPT_FORMALIZATION, title="Theory", purpose="Formalize"),
        ],
    )
    bp = SemanticMaterialBlueprint(material_id="m1", content=ContentBlueprint(blueprint_id="b", metadata=ContentMetadata(title="T")), pedagogy=PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="R"), production=ProductionBlueprint(target_artifact=TargetArtifactType.DETAILED_HANDOUT))
    comp = DocumentComposition(document_id="d1", title="T", mode=DocumentMode.A4_PORTRAIT, theme_reference="default", source_blueprint_id="b", pages=[])
    bundle = RefinedArtifactBundle(artifact_id="art1", blueprint=bp, composition=comp, journey=journey)

    action = RefinementAction(
        action_id="act_reorder",
        target_layer=RefinementTargetLayer.DIRECTOR,
        target_scope=RefinementScope.SECTION,
        intent=RefinementIntent.REORDER,
        rationale="Reorder concept before practice",
        expected_benefit="Proper scaffolding",
    )
    patch_op = PedagogicalSequencePatch(action)
    new_bundle, patch_meta = patch_op.apply(bundle)

    # Verify new bundle has concept first, original bundle remains unchanged
    assert bundle.journey.stages[0].stage_type == LearningStageType.WORKED_EXAMPLE
    assert new_bundle.journey.stages[0].stage_type == LearningStageType.CONCEPT_FORMALIZATION
    assert patch_meta.patch_id == "patch_seq_act_reorder"


def test_capability_replacement_patch_updates_component_family():
    page = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[
                    ContentBlock(
                        component_family=ComponentFamily.COMPARISON_BLOCK,
                        source_unit_ids=["u1"],
                        raw_content="Step 1: Init. Step 2: Run. Step 3: Stop.",
                    )
                ],
            )
        },
    )
    comp = DocumentComposition(document_id="d1", title="T", mode=DocumentMode.A4_PORTRAIT, theme_reference="default", source_blueprint_id="b", pages=[page])
    bundle = RefinedArtifactBundle(artifact_id="art1", blueprint=SemanticMaterialBlueprint(material_id="m1", content=ContentBlueprint(blueprint_id="b", metadata=ContentMetadata(title="T")), pedagogy=PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="R"), production=ProductionBlueprint(target_artifact=TargetArtifactType.DETAILED_HANDOUT)), composition=comp)

    action = RefinementAction(
        action_id="act_cap",
        target_layer=RefinementTargetLayer.CAPABILITY_SELECTION,
        target_scope=RefinementScope.BLOCK,
        intent=RefinementIntent.REPLACE_CAPABILITY,
        rationale="Use STEP_BLOCK for sequence",
        expected_benefit="Clear direction",
    )
    patch_op = CapabilityReplacementPatch(action)
    new_bundle, patch_meta = patch_op.apply(bundle)

    block = new_bundle.composition.pages[0].regions[RegionRole.PRIMARY].blocks[0]
    assert block.component_family == ComponentFamily.STEP_BLOCK
