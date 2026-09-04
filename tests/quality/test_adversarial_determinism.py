"""
Unit tests for evaluation determinism under adversarial defect conditions (10 consecutive runs).
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


def test_adversarial_determinism_across_10_iterations():
    content = ContentBlueprint(
        blueprint_id="bp_adv_det",
        metadata=ContentMetadata(title="Quantum Mechanics", domain=KnowledgeDomain.PHYSICS),
        objectives=[LearningObjective(id="o1", objective="Wavefunction")],
        concepts=[ConceptDefinition(id="c1", name="Wavefunction", formal_definition="Probability amplitude.")],
        facts=[],
    )
    pedagogy = PedagogicalBlueprint(
        primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
        narrative_rationale="Rationale",
        sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")],
    )
    prod = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")],
    )
    material_bp = SemanticMaterialBlueprint(material_id="m_det", content=content, pedagogy=pedagogy, production=prod)

    # Intentionally imperfect journey
    journey = LearningJourney(
        journey_id="j_adv_det",
        strategy=MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
        stages=[
            LearningStage(stage_type=LearningStageType.WORKED_EXAMPLE, title="Calculation", purpose="Calc"),
            LearningStage(stage_type=LearningStageType.CONCEPT_FORMALIZATION, title="Schrodinger Eq", purpose="Eq"),
        ],
    )

    page = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content="Quantum intro paragraph.")],
            )
        },
    )
    comp = DocumentComposition(
        document_id="doc_adv_det",
        title="Adv Det",
        mode=DocumentMode.PRESENTATION_16_9,
        theme_reference="default",
        source_blueprint_id="bp_adv_det",
        pages=[page],
    )

    reports = [
        QualityEvaluationEngine.evaluate_artifact(
            "job_adv_det",
            material_bp=material_bp,
            journey=journey,
            composition=comp,
            target_format="presentation_16_9",
        )
        for _ in range(10)
    ]

    first = reports[0]
    for idx, rep in enumerate(reports[1:], start=2):
        assert rep.overall_score == first.overall_score, f"Score mismatch on iteration {idx}"
        assert rep.quality_level == first.quality_level, f"Level mismatch on iteration {idx}"
        assert rep.gate_result.decision == first.gate_result.decision, f"Gate decision mismatch on iteration {idx}"
        assert len(rep.findings) == len(first.findings), f"Finding count mismatch on iteration {idx}"
        assert [f.finding for f in rep.findings] == [f.finding for f in first.findings], f"Finding order mismatch on iteration {idx}"
