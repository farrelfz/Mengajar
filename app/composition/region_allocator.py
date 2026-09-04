"""
KIR AI Document Intelligence — Region Allocator.
"""
from app.composition.schemas import RegionRole, PageRegion, ContentBlock
from app.design.schemas import ComponentFamily


def allocate_to_regions(blocks: list[ContentBlock]) -> dict[RegionRole, PageRegion]:
    """
    Distributes content blocks into semantic regions.
    """
    regions = {}
    
    for block in blocks:
        # Determine region based on component family
        role = RegionRole.PRIMARY
        
        if block.component_family == ComponentFamily.TITLE_BLOCK:
            role = RegionRole.HEADER
        elif block.component_family in {ComponentFamily.DATA_BLOCK, ComponentFamily.IMAGE_PLACEHOLDER, ComponentFamily.DIAGRAM_PLACEHOLDER}:
            role = RegionRole.VISUAL
        elif block.component_family in {ComponentFamily.WARNING_BLOCK, ComponentFamily.CALLOUT, ComponentFamily.COMPARISON_BLOCK}:
            role = RegionRole.SECONDARY
        elif block.component_family in {ComponentFamily.STEP_BLOCK, ComponentFamily.TIMELINE_ITEM}:
            role = RegionRole.SEQUENCE
        elif block.component_family == ComponentFamily.REFERENCE_BLOCK:
            role = RegionRole.FOOTER
            
        # Ensure region exists
        if role not in regions:
            regions[role] = PageRegion(role=role, blocks=[])
            
        regions[role].blocks.append(block)
        
    return regions
