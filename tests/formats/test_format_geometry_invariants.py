"""
Tests verifying format geometry invariants across Format Contract, HTML, and Physical Renderers.
"""
import pytest
from app.formats.presets import A4_PORTRAIT, A4_LANDSCAPE, PRESENTATION_16_9
from app.formats.registry import FormatRegistry
from app.rendering.html.assembler import HTMLAssembler
from app.composition.schemas import DocumentComposition, PageComposition, PageRegion, ContentBlock, RegionRole
from app.intelligence.schemas import DocumentMode
from app.design.schemas import ComponentFamily


def test_format_geometry_invariants_css_rules():
    """Verify that CSS page rules generated match canonical geometry."""
    assert A4_PORTRAIT.to_css_page_rule() == "@page { size: 210mm 297mm; margin: 0; }"
    assert A4_LANDSCAPE.to_css_page_rule() == "@page { size: 297mm 210mm; margin: 0; }"
    assert PRESENTATION_16_9.to_css_page_rule() == "@page { size: 13.333in 7.5in; margin: 0; }"


def test_format_geometry_invariants_point_dimensions():
    """Verify point dimensions in pt match mm calculations precisely."""
    # A4 Portrait: 210mm * 72 / 25.4 = 595.2756 pt, 297mm * 72 / 25.4 = 841.8898 pt
    assert abs(A4_PORTRAIT.width_pt - 595.28) < 0.1
    assert abs(A4_PORTRAIT.height_pt - 841.89) < 0.1

    # A4 Landscape: 297mm x 210mm
    assert abs(A4_LANDSCAPE.width_pt - 841.89) < 0.1
    assert abs(A4_LANDSCAPE.height_pt - 595.28) < 0.1

    # 16:9 Presentation: 13.333in x 7.5in -> 960 pt x 540 pt
    assert abs(PRESENTATION_16_9.width_pt - 960.0) < 0.1
    assert abs(PRESENTATION_16_9.height_pt - 540.0) < 0.1


from pathlib import Path

def test_html_assembler_injects_matching_page_class(tmp_path: Path):
    """Verify HTMLAssembler injects canonical format page class without collisions."""
    templates_dir = Path("app/rendering/html/templates")
    assembler = HTMLAssembler(templates_dir)

    block = ContentBlock(
        block_id="b1",
        component_family=ComponentFamily.TEXT_BLOCK,
        source_unit_ids=["u1"],
        rendered_html="<p>Test</p>",
    )
    region = PageRegion(role=RegionRole.PRIMARY, blocks=[block])
    page = PageComposition(
        page_number=1,
        page_type="document_page",
        composition_type="standard",
        regions={RegionRole.PRIMARY: region},
        source_unit_ids=["u1"],
    )
    comp = DocumentComposition(
        mode=DocumentMode.A4_LANDSCAPE,
        format_id="a4_landscape",
        theme_reference="default",
        source_blueprint_id="mat_1",
        pages=[page],
    )

    out_file = assembler.assemble(comp, assets=[], output_dir=tmp_path)
    html = out_file.read_text(encoding="utf-8")
    assert "size: 297mm 210mm;" in html
    assert 'class="page page-a4-landscape"' in html
    assert 'class="page page-a4-portrait"' not in html
