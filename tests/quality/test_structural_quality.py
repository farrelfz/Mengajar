"""
Unit tests for StructuralEvaluator.
"""

import pytest

from app.blueprints.content import ContentBlueprint, ContentMetadata, KnowledgeDomain
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
from app.intelligence.schemas import DocumentMode
from app.quality.contracts import QualityDimension, QualitySeverity
from app.quality.structural_evaluator import StructuralEvaluator


def test_structural_evaluator_flags_empty_blueprint():
    # Blueprint without objectives, concepts, or facts
    content_bp = ContentBlueprint(
        blueprint_id="bp_empty",
        metadata=ContentMetadata(
            title="Empty Topic",
            domain=KnowledgeDomain.GENERAL_SCIENCE,
        ),
        objectives=[],
        concepts=[],
        facts=[],
    )
    pedagogy_bp = PedagogicalBlueprint(
        primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
        narrative_rationale="Test rationale",
        sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")],
    )
    prod_bp = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")],
    )
    material_bp = SemanticMaterialBlueprint(
        material_id="mat_empty",
        content=content_bp,
        pedagogy=pedagogy_bp,
        production=prod_bp,
    )

    metrics, findings = StructuralEvaluator.evaluate(blueprint=material_bp)

    assert len(findings) >= 2
    assert any(f.severity == QualitySeverity.ERROR for f in findings)
    assert any(f.severity == QualitySeverity.WARNING for f in findings)
    assert metrics[0].score < 0.6


def test_structural_evaluator_flags_empty_pages_in_composition():
    # Document composition with an empty page (0 blocks)
    empty_page = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={},
    )
    valid_page = PageComposition(
        page_number=2,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content="Some content")],
            )
        },
    )
    comp = DocumentComposition(
        document_id="doc_empty_pages",
        title="Empty Page Test",
        mode=DocumentMode.A4_PORTRAIT,
        theme_reference="default",
        source_blueprint_id="bp_test",
        pages=[empty_page, valid_page],
    )

    metrics, findings = StructuralEvaluator.evaluate(composition=comp)

    assert len(findings) == 1
    assert findings[0].severity == QualitySeverity.ERROR
    assert "empty pages detected" in findings[0].finding.lower()
    assert metrics[0].score < 1.0
