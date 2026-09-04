"""
KIR AI Document Intelligence — Hybrid Rendering Pipeline Test.
"""
from pathlib import Path
from app.composition.schemas import DocumentComposition, PageComposition, RegionRole, PageRegion, ContentBlock
from app.design.schemas import ComponentFamily
from app.intelligence.schemas import DocumentMode
from app.rendering.engine import MasterRenderEngine
from app.rendering.schemas import RenderTarget

def test_hybrid_rendering_pipeline(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    with open(templates_dir / "document.html", "w") as f:
        f.write("<html><body>Mock</body></html>")
        
    output_dir = tmp_path / "output"
    engine = MasterRenderEngine(templates_dir, output_dir)
    
    # Create mock composition
    block1 = ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["1"])
    block2 = ContentBlock(component_family=ComponentFamily.DIAGRAM_PLACEHOLDER, source_unit_ids=["2"])
    block3 = ContentBlock(component_family=ComponentFamily.DATA_BLOCK, source_unit_ids=["3"])
    
    region = PageRegion(role=RegionRole.PRIMARY, blocks=[block1, block2, block3])
    page = PageComposition(
        page_number=1,
        page_type="generic",
        composition_type="editorial",
        regions={RegionRole.PRIMARY: region},
        source_unit_ids=["1", "2", "3"]
    )
    
    comp = DocumentComposition(
        mode=DocumentMode.A4_TUTORIAL,
        theme_reference="default",
        source_blueprint_id="test",
        pages=[page]
    )
    
    result = engine.render(comp)
    
    assert result.success is True
    assert result.assets_generated == 2 # 1 reportlab, 1 matplotlib
    assert result.pages == 1
    assert result.pdf_path is not None
