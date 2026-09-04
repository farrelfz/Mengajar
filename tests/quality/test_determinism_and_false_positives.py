"""
Unit tests for evaluation determinism and false-positive safeguards.
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
from app.blueprints.pedagogical import (
    PedagogicalBlueprint,
    PedagogicalPattern,
    PedagogicalStep,
    SemanticStepType,
)
from app.blueprints.production import (
    ProductionBlueprint,
    ProductionRequirement,
    SemanticIntentSpec,
    TargetArtifactType,
)
from app.composition.schemas import (
    ContentBlock,
    DocumentComposition,
    PageComposition,
    PageRegion,
    RegionRole,
)
from app.design.schemas import ComponentFamily
from app.director.contracts import (
    LearningJourney,
    LearningStage,
    LearningStageType,
    MaterialStrategyType,
)
from app.intelligence.schemas import DocumentMode
from app.quality.contracts import QualityGateDecision
from app.quality.engine import QualityEvaluationEngine


def test_quality_evaluation_is_strictly_deterministic():
    # Construct standard valid inputs
    content_bp = ContentBlueprint(
        blueprint_id="bp_det",
        metadata=ContentMetadata(
            title="Thermodynamics Basics",
            domain=KnowledgeDomain.PHYSICS,
        ),
        objectives=[LearningObjective(id="obj_1", objective="Understand the 1st Law of Thermodynamics")],
        concepts=[ConceptDefinition(id="c_1", name="Internal Energy", formal_definition="Total microscopic energy")],
        facts=[],
    )
    step1 = PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Heat intro")
    pedagogy_bp = PedagogicalBlueprint(
        primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
        narrative_rationale="Intuitive explanation before formal definition",
        sequence=[step1],
    )
    production_bp = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")],
    )
    material_bp = SemanticMaterialBlueprint(
        material_id="mat_det",
        content=content_bp,
        pedagogy=pedagogy_bp,
        production=production_bp,
    )
    journey = LearningJourney(
        journey_id="j_det",
        strategy=MaterialStrategyType.CONCEPTUAL_DISCOVERY,
        stages=[
            LearningStage(
                stage_type=LearningStageType.HOOK,
                title="Heat and Work",
                purpose="Engage curiosity",
            ),
            LearningStage(
                stage_type=LearningStageType.CONCEPT_FORMALIZATION,
                title="First Law",
                purpose="Define mathematical statement",
            ),
        ],
    )
    page1 = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content="Heat exchange intro.")],
            )
        },
    )
    comp = DocumentComposition(
        document_id="doc_det",
        title="Determinism Test",
        mode=DocumentMode.A4_PORTRAIT,
        theme_reference="default",
        source_blueprint_id="bp_det",
        pages=[page1],
    )

    # Run 3 consecutive evaluations
    r1 = QualityEvaluationEngine.evaluate_artifact("job_det", material_bp=material_bp, journey=journey, composition=comp, target_format="a4_portrait")
    r2 = QualityEvaluationEngine.evaluate_artifact("job_det", material_bp=material_bp, journey=journey, composition=comp, target_format="a4_portrait")
    r3 = QualityEvaluationEngine.evaluate_artifact("job_det", material_bp=material_bp, journey=journey, composition=comp, target_format="a4_portrait")

    assert r1.overall_score == r2.overall_score == r3.overall_score
    assert r1.quality_level == r2.quality_level == r3.quality_level
    assert r1.gate_result.decision == r2.gate_result.decision == r3.gate_result.decision
    assert len(r1.findings) == len(r2.findings) == len(r3.findings)
    assert len(r1.metrics) == len(r2.metrics) == len(r3.metrics)
    assert [m.score for m in r1.metrics] == [m.score for m in r2.metrics] == [m.score for m in r3.metrics]


def test_format_aware_density_differentiation():
    # Same content evaluated on 16:9 presentation vs A4 portrait
    moderate_text = "This is a detailed conceptual explanation of kinetic theory. " * 25  # ~1500 chars
    page = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content=moderate_text)],
            )
        },
    )
    comp = DocumentComposition(
        document_id="doc_format_diff",
        title="Format Density Diff",
        mode=DocumentMode.A4_PORTRAIT,
        theme_reference="default",
        source_blueprint_id="bp_diff",
        pages=[page],
    )

    # On A4 Portrait: 1500 chars is well within limit (< 3500)
    rep_a4 = QualityEvaluationEngine.evaluate_artifact("job_a4", composition=comp, target_format="a4_portrait")
    # On 16:9 Presentation: 1500 chars is over limit (> 1200)
    rep_pres = QualityEvaluationEngine.evaluate_artifact("job_pres", composition=comp, target_format="presentation_16_9")

    assert rep_a4.gate_result.decision in [QualityGateDecision.PASS, QualityGateDecision.PASS_WITH_WARNINGS]
    # Presentation should have a density finding
    assert any("excessive textual density" in f.finding.lower() for f in rep_pres.findings)
