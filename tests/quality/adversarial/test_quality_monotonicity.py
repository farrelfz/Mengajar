"""
Adversarial Part 5: Quality score monotonicity validation across progressive artifact degradation.
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
from app.quality.engine import QualityEvaluationEngine


def test_quality_scores_degrade_monotonically():
    # Base clean components
    content_clean = ContentBlueprint(
        blueprint_id="bp_clean",
        metadata=ContentMetadata(title="Wave Optics", domain=KnowledgeDomain.PHYSICS),
        objectives=[LearningObjective(id="o1", objective="Understand interference", target_concept="Interference")],
        concepts=[ConceptDefinition(id="c1", name="Interference", formal_definition="Superposition of two waves.")],
        facts=[],
    )
    pedagogy_clean = PedagogicalBlueprint(
        primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
        narrative_rationale="Rationale",
        sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")],
    )
    prod_clean = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")],
    )
    material_clean = SemanticMaterialBlueprint(material_id="m_clean", content=content_clean, pedagogy=pedagogy_clean, production=prod_clean)

    journey_clean = LearningJourney(
        journey_id="j_clean",
        strategy=MaterialStrategyType.CONCEPTUAL_DISCOVERY,
        stages=[
            LearningStage(stage_type=LearningStageType.HOOK, title="Soap bubbles", purpose="Hook"),
            LearningStage(stage_type=LearningStageType.CONCEPT_FORMALIZATION, title="Wave Superposition", purpose="Formula"),
        ],
    )

    page_clean = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content="Light wave interference intro.")],
            )
        },
    )
    comp_clean = DocumentComposition(
        document_id="doc_clean",
        title="Clean Doc",
        mode=DocumentMode.PRESENTATION_16_9,
        theme_reference="default",
        source_blueprint_id="bp_clean",
        pages=[page_clean],
    )

    # Level 0: Perfect Clean Artifact
    r0 = QualityEvaluationEngine.evaluate_artifact("j0", material_bp=material_clean, journey=journey_clean, composition=comp_clean, target_format="presentation_16_9")

    # Level 1: Minor Redundancy (2 duplicate pages)
    dup_page = PageComposition(
        page_number=2,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u2"], raw_content="Light wave interference intro.")],
            )
        },
    )
    comp_l1 = DocumentComposition(
        document_id="doc_l1",
        title="L1 Redundant",
        mode=DocumentMode.PRESENTATION_16_9,
        theme_reference="default",
        source_blueprint_id="bp_clean",
        pages=[page_clean, dup_page],
    )
    r1 = QualityEvaluationEngine.evaluate_artifact("j1", material_bp=material_clean, journey=journey_clean, composition=comp_l1, target_format="presentation_16_9")

    # Level 2: Moderate Density Overload added
    dense_text = "Extreme dense slide text without breaks. " * 35  # ~1400 chars on 16:9
    page_dense = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content=dense_text)],
            )
        },
    )
    comp_l2 = DocumentComposition(
        document_id="doc_l2",
        title="L2 Dense",
        mode=DocumentMode.PRESENTATION_16_9,
        theme_reference="default",
        source_blueprint_id="bp_clean",
        pages=[page_dense, dup_page],
    )
    r2 = QualityEvaluationEngine.evaluate_artifact("j2", material_bp=material_clean, journey=journey_clean, composition=comp_l2, target_format="presentation_16_9")

    # Level 3: Pedagogical Inversion added
    journey_bad = LearningJourney(
        journey_id="j_bad",
        strategy=MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
        stages=[
            LearningStage(stage_type=LearningStageType.WORKED_EXAMPLE, title="Math problem", purpose="Problem"),
            LearningStage(stage_type=LearningStageType.CONCEPT_FORMALIZATION, title="Theory", purpose="Theory"),
        ],
    )
    r3 = QualityEvaluationEngine.evaluate_artifact("j3", material_bp=material_clean, journey=journey_bad, composition=comp_l2, target_format="presentation_16_9")

    # Level 4: Semantic Incompleteness (0 concepts)
    content_bad = ContentBlueprint(
        blueprint_id="bp_bad",
        metadata=ContentMetadata(title="Optics", domain=KnowledgeDomain.PHYSICS),
        objectives=[LearningObjective(id="o1", objective="Interference")],
        concepts=[],
        facts=[],
    )
    material_l4 = SemanticMaterialBlueprint(material_id="m_l4", content=content_bad, pedagogy=pedagogy_clean, production=prod_clean)
    r4 = QualityEvaluationEngine.evaluate_artifact("j4", material_bp=material_l4, journey=journey_bad, composition=comp_l2, target_format="presentation_16_9")

    # Monotonicity Assertions
    assert r0.overall_score >= r1.overall_score
    assert r1.overall_score >= r2.overall_score
    assert r2.overall_score >= r3.overall_score
    assert r3.overall_score >= r4.overall_score
    assert r0.overall_score > r4.overall_score
