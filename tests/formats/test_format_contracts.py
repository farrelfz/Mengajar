"""
Unit and integration tests for Artifact Format Contracts, Registry, Resolution, and Validation.
"""
from pathlib import Path
import pytest

from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.formats.contracts import ArtifactFormat
from app.formats.presets import A4_PORTRAIT, A4_LANDSCAPE, PRESENTATION_16_9
from app.formats.registry import FormatRegistry, UnknownFormatError, get_format
from app.formats.resolution import resolve_format, DEFAULT_ARTIFACT_FORMAT_MAPPING
from app.intelligence.schemas import DocumentMode
from app.orchestration.production_pipeline import MaterialProductionPipeline
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


class TestFormatRegistry:
    def test_canonical_presets_exist(self):
        reg = FormatRegistry.get_instance()
        assert reg.get("a4_portrait").id == "a4_portrait"
        assert reg.get("a4_landscape").id == "a4_landscape"
        assert reg.get("presentation_16_9").id == "presentation_16_9"

    def test_aliases_resolve_deterministically(self):
        reg = FormatRegistry.get_instance()
        assert reg.get("16:9").id == "presentation_16_9"
        assert reg.get("presentation-16-9").id == "presentation_16_9"
        assert reg.get("presentation").id == "presentation_16_9"
        assert reg.get("a4-portrait").id == "a4_portrait"
        assert reg.get("a4_portrait").id == "a4_portrait"
        assert reg.get("a4").id == "a4_portrait"
        assert reg.get("a4-landscape").id == "a4_landscape"
        assert reg.get("a4-tutorial").id == "a4_landscape"

    def test_document_mode_enum_resolution(self):
        reg = FormatRegistry.get_instance()
        assert reg.get(DocumentMode.A4_PORTRAIT).id == "a4_portrait"
        assert reg.get(DocumentMode.A4_LANDSCAPE).id == "a4_landscape"
        assert reg.get(DocumentMode.A4_TUTORIAL).id == "a4_landscape"
        assert reg.get(DocumentMode.PRESENTATION_16_9).id == "presentation_16_9"

    def test_unknown_format_raises_error(self):
        reg = FormatRegistry.get_instance()
        with pytest.raises(UnknownFormatError) as exc_info:
            reg.get("billboard_canvas_unknown")
        assert "Unknown format identifier" in str(exc_info.value)


class TestFormatGeometry:
    def test_a4_portrait_geometry(self):
        fmt = A4_PORTRAIT
        assert fmt.width_mm == 210.0
        assert fmt.height_mm == 297.0
        assert fmt.orientation == "portrait"
        assert fmt.category == "document"
        assert pytest.approx(fmt.width_pt, rel=1e-2) == 595.28
        assert pytest.approx(fmt.height_pt, rel=1e-2) == 841.89
        assert fmt.to_css_page_rule() == "@page { size: 210mm 297mm; margin: 0; }"

    def test_a4_landscape_geometry(self):
        fmt = A4_LANDSCAPE
        assert fmt.width_mm == 297.0
        assert fmt.height_mm == 210.0
        assert fmt.orientation == "landscape"
        assert fmt.category == "document"
        assert pytest.approx(fmt.width_pt, rel=1e-2) == 841.89
        assert pytest.approx(fmt.height_pt, rel=1e-2) == 595.28
        assert fmt.to_css_page_rule() == "@page { size: 297mm 210mm; margin: 0; }"

    def test_presentation_16_9_geometry(self):
        fmt = PRESENTATION_16_9
        assert fmt.orientation == "landscape"
        assert fmt.category == "presentation"
        assert pytest.approx(fmt.aspect_ratio, rel=1e-2) == 16.0 / 9.0
        assert fmt.to_css_page_rule() == "@page { size: 13.333in 7.5in; margin: 0; }"


class TestFormatResolution:
    def test_explicit_format_overrides_artifact_default(self):
        # A handout requested explicitly as presentation 16:9
        resolved = resolve_format(
            explicit_format="presentation_16_9",
            artifact_type=TargetArtifactType.DETAILED_HANDOUT,
        )
        assert resolved.id == "presentation_16_9"

        # A presentation requested explicitly as A4 portrait
        resolved_pres_a4 = resolve_format(
            explicit_format="a4_portrait",
            artifact_type=TargetArtifactType.TEACHING_PRESENTATION,
        )
        assert resolved_pres_a4.id == "a4_portrait"

    def test_artifact_defaults_apply_when_explicit_absent(self):
        res_handout = resolve_format(artifact_type=TargetArtifactType.DETAILED_HANDOUT)
        assert res_handout.id == "a4_portrait"

        res_presentation = resolve_format(artifact_type=TargetArtifactType.TEACHING_PRESENTATION)
        assert res_presentation.id == "presentation_16_9"

        res_poster = resolve_format(artifact_type=TargetArtifactType.SCIENTIFIC_POSTER)
        assert res_poster.id == "a4_landscape"


@pytest.mark.asyncio
async def test_multiformat_rendering_same_semantic_content(tmp_path: Path):
    """Prove the same semantic material can be rendered into A4 Portrait, A4 Landscape, and 16:9."""
    raw_text = """
    # Physics of Torque and Equilibrium
    ## 1. Door Handle Observation
    Pushing at the edge makes rotation easy; pushing near hinges is difficult.
    ## 2. Formal Principle
    Torque is tau = r * F * sin(theta).
    """

    intel_agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=intel_agent)

    # 1. Render as A4 Portrait
    out_a4_portrait = tmp_path / "a4_portrait"
    res_portrait = await pipeline.produce_artifact(
        raw_input=raw_text,
        source_hint="torque_portrait.txt",
        domain=KnowledgeDomain.PHYSICS,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        target_format="a4_portrait",
        output_dir=out_a4_portrait,
        output_filename="torque_portrait",
    )
    assert res_portrait.success is True
    assert res_portrait.composition.format_id == "a4_portrait"

    # 2. Render as A4 Landscape
    out_a4_landscape = tmp_path / "a4_landscape"
    res_landscape = await pipeline.produce_artifact(
        raw_input=raw_text,
        source_hint="torque_landscape.txt",
        domain=KnowledgeDomain.PHYSICS,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        target_format="a4_landscape",
        output_dir=out_a4_landscape,
        output_filename="torque_landscape",
    )
    assert res_landscape.success is True
    assert res_landscape.composition.format_id == "a4_landscape"

    # 3. Render as 16:9 Presentation
    out_169 = tmp_path / "presentation_169"
    res_169 = await pipeline.produce_artifact(
        raw_input=raw_text,
        source_hint="torque_169.txt",
        domain=KnowledgeDomain.PHYSICS,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        target_format="presentation_16_9",
        output_dir=out_169,
        output_filename="torque_169",
    )
    assert res_169.success is True
    assert res_169.composition.format_id == "presentation_16_9"
