import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.composition.schemas import DocumentComposition, PageComposition, RegionRole, PageRegion, ContentBlock
from app.design.schemas import ComponentFamily
from app.intelligence.schemas import DocumentMode
from app.rendering.engine import MasterRenderEngine
import json

def build_kti_composition(mode: DocumentMode) -> DocumentComposition:
    block1 = ContentBlock(component_family=ComponentFamily.TITLE_BLOCK, source_unit_ids=["1"])
    block2 = ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["2"])
    block3 = ContentBlock(component_family=ComponentFamily.TIMELINE_ITEM, source_unit_ids=["3"])
    
    region1 = PageRegion(role=RegionRole.PRIMARY, blocks=[block1, block2, block3])
    page1 = PageComposition(
        page_number=1,
        page_type="cover",
        composition_type="editorial",
        regions={RegionRole.PRIMARY: region1},
        source_unit_ids=["1", "2", "3"]
    )
    
    block4 = ContentBlock(component_family=ComponentFamily.DATA_BLOCK, source_unit_ids=["4"])
    block5 = ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["5"])
    block6 = ContentBlock(component_family=ComponentFamily.DIAGRAM_PLACEHOLDER, source_unit_ids=["6"])
    
    region2 = PageRegion(role=RegionRole.PRIMARY, blocks=[block4, block5, block6])
    page2 = PageComposition(
        page_number=2,
        page_type="generic",
        composition_type="editorial",
        regions={RegionRole.PRIMARY: region2},
        source_unit_ids=["4", "5", "6"]
    )
    
    return DocumentComposition(
        mode=mode,
        theme_reference="default",
        source_blueprint_id="benchmark",
        pages=[page1, page2]
    )

def main():
    templates_dir = Path("app/rendering/html/templates")
    
    # A4 Benchmark
    output_a4 = Path("outputs/benchmark/tutorial_a4")
    engine_a4 = MasterRenderEngine(templates_dir, output_a4)
    comp_a4 = build_kti_composition(DocumentMode.A4_TUTORIAL)
    result_a4 = engine_a4.render(comp_a4)
    
    with open(output_a4 / "validation_report.json", "w") as f:
        json.dump(result_a4.model_dump(), f, indent=2)
        
    print(f"A4 Tutorial Result: {result_a4.success}")
    if result_a4.errors:
        print(f"Errors: {result_a4.errors}")
        
    # 16:9 Benchmark
    output_169 = Path("outputs/benchmark/presentation_16_9")
    engine_169 = MasterRenderEngine(templates_dir, output_169)
    comp_169 = build_kti_composition(DocumentMode.PRESENTATION_16_9)
    result_169 = engine_169.render(comp_169)
    
    with open(output_169 / "validation_report.json", "w") as f:
        json.dump(result_169.model_dump(), f, indent=2)
        
    print(f"16:9 Presentation Result: {result_169.success}")
    if result_169.errors:
        print(f"Errors: {result_169.errors}")

if __name__ == "__main__":
    main()
