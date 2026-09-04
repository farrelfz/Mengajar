"""
Adversarial Case I: Multi-defect artifact evaluation (simultaneous structural, semantic, density, and format defects).
"""

from pathlib import Path
import pytest
import pymupdf

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
from app.quality.contracts import QualityGateDecision, QualityLevel, QualitySeverity
from app.quality.engine import QualityEvaluationEngine


def test_multi_defect_artifact_severely_penalized_and_fails_gate(tmp_path: Path):
    # 1. Semantic defect: 0 concepts
    content = ContentBlueprint(
        blueprint_id="bp_bad",
        metadata=ContentMetadata(title="Bad Topic", domain=KnowledgeDomain.PHYSICS),
        objectives=[LearningObjective(id="o1", objective="Learn X")],
        concepts=[],
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
    material_bp = SemanticMaterialBlueprint(material_id="m_bad", content=content, pedagogy=pedagogy, production=prod)

    # 2. Pedagogical defect: Worked example before concept
    journey = LearningJourney(
        journey_id="j_bad",
        strategy=MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
        stages=[
            LearningStage(stage_type=LearningStageType.WORKED_EXAMPLE, title="Ex", purpose="Ex"),
            LearningStage(stage_type=LearningStageType.CONCEPT_FORMALIZATION, title="Def", purpose="Def"),
        ],
    )

    # 3. Density & Redundancy defect: Duplicate huge text across pages on 16:9
    huge_text = "Extreme repetitive dense text across pages. " * 50  # ~2200 chars
    p1 = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content=huge_text)])},
    )
    p2 = PageComposition(
        page_number=2,
        page_type="content",
        composition_type="single_region",
        regions={RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u2"], raw_content=huge_text)])},
    )
    comp = DocumentComposition(
        document_id="doc_bad",
        title="Bad Doc",
        mode=DocumentMode.PRESENTATION_16_9,
        theme_reference="default",
        source_blueprint_id="bp_bad",
        pages=[p1, p2],
    )

    # 4. Format defect: Wrong PDF dimensions (A4 portrait file evaluated as presentation_16_9)
    pdf_path = tmp_path / "bad_artifact.pdf"
    doc = pymupdf.open()
    doc.new_page(width=595.0, height=841.9)
    doc.save(str(pdf_path))
    doc.close()

    report = QualityEvaluationEngine.evaluate_artifact(
        job_id="job_multi_defect",
        material_bp=material_bp,
        journey=journey,
        composition=comp,
        pdf_path=pdf_path,
        target_format="presentation_16_9",
    )

    assert report.gate_result.decision == QualityGateDecision.FAIL
    assert report.gate_result.can_proceed is False
    assert report.overall_score < 0.60
    assert report.quality_level in [QualityLevel.NEEDS_IMPROVEMENT, QualityLevel.POOR, QualityLevel.CRITICAL]
    assert len(report.findings) >= 4
