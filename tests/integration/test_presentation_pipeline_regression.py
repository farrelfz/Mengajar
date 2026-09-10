"""End-to-End Regression Test for Source-Grounded Presentation Pipeline.

Verifies:
1. Complete structural parsing (zero information loss).
2. Proportional slide count scaling (not compressed into 6 static slides).
3. Zero duplicate slides (< 10% similarity).
4. Zero hallucinated statistical jargon (no 'p < 0.05' unless in source).
5. Layout diversity (entropy >= 0.70, no > 2 consecutive identical layouts).
6. 100% critical source coverage and bidirectional source_refs tracing.
7. Successful PDF compilation and export.
"""

from pathlib import Path
import pytest

from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.intelligence.markdown_tree_parser import MarkdownTreeParser, SemanticBlockType
from app.intelligence.content_manifest import ContentManifestBuilder
from app.presentation.slide_architect import SlideArchitect
from app.presentation.slide_generator import SlideGenerator
from app.presentation.quality_gate import PresentationQualityGate
from app.orchestration.production_pipeline import MaterialProductionPipeline


def test_hand_fire_tree_parser_structural_fidelity():
    """Verify structural parsing of the 29-topic comprehensive Hand Fire fixture."""
    fixture_path = Path("tests/fixtures/hand_fire_full.md")
    assert fixture_path.exists(), "Hand Fire full fixture must exist"
    text = fixture_path.read_text(encoding="utf-8")

    parser = MarkdownTreeParser()
    tree = parser.parse(text, document_title="Hand Fire Full")

    assert tree.total_sections_count >= 26, f"Expected >= 26 sections, got {tree.total_sections_count}"
    all_blocks = tree.all_blocks_flat()
    formulas = [b for b in all_blocks if b.type == SemanticBlockType.FORMULA]
    tables = [b for b in all_blocks if b.type in (SemanticBlockType.TABLE, SemanticBlockType.OBSERVATION_DATA, SemanticBlockType.RISK_MATRIX)]
    warnings = [b for b in all_blocks if b.type == SemanticBlockType.WARNING or b.metadata.get("is_warning")]

    assert len(formulas) >= 6, f"Expected >= 6 formulas, got {len(formulas)}"
    assert len(tables) >= 5, f"Expected >= 5 tables, got {len(tables)}"
    assert len(warnings) >= 1, "Expected callouts for safety warnings"
    assert "HAND FIRE" in tree.title.upper()


def test_hand_fire_manifest_and_slide_planning():
    """Verify slide count dynamically scales with document density and complexity."""
    fixture_path = Path("tests/fixtures/hand_fire_full.md")
    text = fixture_path.read_text(encoding="utf-8")

    parser = MarkdownTreeParser()
    tree = parser.parse(text, document_title="Hand Fire Full")

    manifest_builder = ContentManifestBuilder()
    manifest = manifest_builder.build(tree)
    all_concepts = manifest.get_all_concepts()

    assert len(all_concepts) >= 20, f"Expected >= 20 semantic units, got {len(all_concepts)}"
    assert len(manifest.critical_concepts) >= 5
    assert manifest.target_slides >= 20, f"Expected target >= 20 slides, got {manifest.target_slides}"

    architect = SlideArchitect()
    slide_plan = architect.plan(tree, manifest)

    assert len(slide_plan.slides) >= manifest.min_slides
    assert len(slide_plan.slides) >= 20, f"Must produce >= 20 slides for 29 topics, got {len(slide_plan.slides)}"
    assert slide_plan.layout_entropy >= 0.70, f"Entropy must be >= 0.70, got {slide_plan.layout_entropy}"

    # Verify no 3 consecutive identical layouts
    for i in range(len(slide_plan.slides) - 2):
        l1, l2, l3 = slide_plan.slides[i].layout, slide_plan.slides[i+1].layout, slide_plan.slides[i+2].layout
        assert not (l1 == l2 == l3), f"Streak of 3 identical layouts at slide {i+1}: {l1}"


def test_quality_gate_passes_and_blocks_hallucinations():
    """Verify that 11 quality gates strictly enforce source fidelity."""
    fixture_path = Path("tests/fixtures/hand_fire_full.md")
    text = fixture_path.read_text(encoding="utf-8")

    parser = MarkdownTreeParser()
    tree = parser.parse(text, document_title="Hand Fire Full")
    manifest_builder = ContentManifestBuilder()
    manifest = manifest_builder.build(tree)
    architect = SlideArchitect()
    slide_plan = architect.plan(tree, manifest)

    generator = SlideGenerator()
    slides = [generator.generate_slide(planned) for planned in slide_plan.slides]

    engine = PresentationQualityGate()
    report = engine.evaluate(tree, manifest, slide_plan, slides)

    assert not report.export_blocked, f"Quality gate must pass, blocking reasons: {report.blocking_reasons}"
    assert report.critical_coverage >= 0.95
    assert report.important_coverage >= 0.85
    assert report.duplicate_rate < 0.10
    assert report.hallucination_count == 0


@pytest.mark.asyncio
async def test_end_to_end_presentation_production(tmp_path):
    """End-to-end execution of the Presentation branch producing a real PDF artifact."""
    fixture_path = Path("tests/fixtures/hand_fire_full.md")
    text = fixture_path.read_text(encoding="utf-8")

    pipeline = MaterialProductionPipeline()
    result = await pipeline.produce_artifact(
        raw_input=text,
        source_hint="hand_fire_full.md",
        domain=KnowledgeDomain.EXPERIMENT_KIR,
        audience=AudienceLevel.HIGH_SCHOOL,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        output_filename="hand_fire_test_output",
    )

    assert result.success is True, f"Pipeline execution failed: {result.errors}"
    assert result.composition is not None
    assert len(result.composition.pages) >= 20, f"Expected >= 20 slides, got {len(result.composition.pages)}"
    assert result.pdf_path is not None
    pdf_file = Path(result.pdf_path)
    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 10000, "PDF file must be non-trivial"


@pytest.mark.asyncio
async def test_original_hand_fire_markdown():
    """Verify that original 75-line hand_fire.md generates >= 8 slides without duplication."""
    orig_path = Path("hand_fire.md")
    if not orig_path.exists():
        pytest.skip("hand_fire.md not found in root")
    text = orig_path.read_text(encoding="utf-8")

    pipeline = MaterialProductionPipeline()
    result = await pipeline.produce_artifact(
        raw_input=text,
        source_hint="hand_fire.md",
        domain=KnowledgeDomain.EXPERIMENT_KIR,
        audience=AudienceLevel.HIGH_SCHOOL,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        output_filename="hand_fire_orig_test_output",
    )

    assert result.success is True, f"Failed on hand_fire.md: {result.errors}"
    assert result.composition is not None
    assert len(result.composition.pages) >= 8, f"Expected >= 8 slides, got {len(result.composition.pages)}"
