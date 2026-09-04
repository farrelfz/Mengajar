"""
KIR AI Document Intelligence — Hybrid Render Planner.
"""
from app.composition.schemas import DocumentComposition
from app.rendering.schemas import RenderPlan, RenderPlanItem
from app.rendering.registry import RenderTargetRegistry

class HybridRenderPlanner:
    """Creates a deterministic plan for rendering composition blocks to their designated targets."""
    
    def create_plan(self, composition: DocumentComposition) -> RenderPlan:
        plan = RenderPlan(composition_id=composition.composition_id)
        
        for page in composition.pages:
            for region in page.regions.values():
                for block in region.blocks:
                    target = RenderTargetRegistry.get_target(block.component_family)
                    
                    item = RenderPlanItem(
                        source_block_id=block.block_id,
                        component_family=block.component_family,
                        target=target,
                        page_number=page.page_number
                    )
                    plan.items.append(item)
                    
        return plan
