"""
KIR AI Document Intelligence — Render Target Registry.
"""
from app.design.schemas import ComponentFamily
from app.rendering.schemas import RenderTarget

class RenderTargetRegistry:
    _registry: dict[ComponentFamily, RenderTarget] = {
        ComponentFamily.TITLE_BLOCK: RenderTarget.HTML,
        ComponentFamily.SECTION_LABEL: RenderTarget.HTML,
        ComponentFamily.TEXT_BLOCK: RenderTarget.HTML,
        ComponentFamily.KEY_STATEMENT: RenderTarget.HTML,
        ComponentFamily.KEY_NUMBER: RenderTarget.HTML,
        ComponentFamily.INSIGHT_BLOCK: RenderTarget.HTML,
        ComponentFamily.CALLOUT: RenderTarget.HTML,
        ComponentFamily.WARNING_BLOCK: RenderTarget.HTML,
        ComponentFamily.COMPARISON_BLOCK: RenderTarget.HTML,
        ComponentFamily.STEP_BLOCK: RenderTarget.HTML,
        ComponentFamily.TIMELINE_ITEM: RenderTarget.REPORTLAB,
        ComponentFamily.DATA_BLOCK: RenderTarget.PYTHON_VISUAL,
        ComponentFamily.REFERENCE_BLOCK: RenderTarget.HTML,
        ComponentFamily.IMAGE_PLACEHOLDER: RenderTarget.HTML,
        ComponentFamily.DIAGRAM_PLACEHOLDER: RenderTarget.REPORTLAB,
        ComponentFamily.QUOTE_BLOCK: RenderTarget.HTML,
        ComponentFamily.SUMMARY_BLOCK: RenderTarget.HTML,
    }

    @classmethod
    def register(cls, component_family: ComponentFamily, target: RenderTarget) -> None:
        cls._registry[component_family] = target

    @classmethod
    def get_target(cls, component_family: ComponentFamily) -> RenderTarget:
        return cls._registry.get(component_family, RenderTarget.HTML)
