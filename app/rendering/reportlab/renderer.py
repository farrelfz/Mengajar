"""
KIR AI Document Intelligence — ReportLab Vector Asset Engine.
"""
from pathlib import Path
from app.rendering.schemas import AssetMetadata, RenderTarget
from app.design.schemas import ComponentFamily
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group
from reportlab.graphics import renderSVG
from reportlab.lib import colors

class ReportLabRenderer:
    def __init__(self, asset_manager):
        self.asset_manager = asset_manager
        
    def render_component(self, block_id: str, component_family: ComponentFamily, context: dict) -> AssetMetadata:
        d = Drawing(600, 200)
        
        if component_family == ComponentFamily.TIMELINE_ITEM:
            d.add(Line(50, 100, 550, 100, strokeColor=colors.HexColor("#34495e"), strokeWidth=2))
            d.add(Rect(100, 90, 20, 20, fillColor=colors.HexColor("#3498db"), strokeColor=None))
            d.add(String(100, 120, "Phase 1", fontSize=12, fillColor=colors.HexColor("#2c3e50")))
            d.add(Rect(300, 90, 20, 20, fillColor=colors.HexColor("#e74c3c"), strokeColor=None))
            d.add(String(300, 120, "Phase 2", fontSize=12, fillColor=colors.HexColor("#2c3e50")))
            d.add(Rect(500, 90, 20, 20, fillColor=colors.HexColor("#2ecc71"), strokeColor=None))
            d.add(String(500, 120, "Phase 3", fontSize=12, fillColor=colors.HexColor("#2c3e50")))
        else:
            d.add(Rect(50, 50, 300, 100, fillColor=colors.HexColor("#ecf0f1"), strokeColor=colors.HexColor("#bdc3c7")))
            d.add(String(150, 100, f"Vector: {component_family.value}", fontSize=14, fillColor=colors.HexColor("#34495e")))
        
        asset_path = self.asset_manager.generate_asset_path(block_id, "svg")
        renderSVG.drawToFile(d, str(asset_path))
        
        asset = AssetMetadata(
            asset_id=block_id,
            asset_type="vector_diagram",
            source_component_id=block_id,
            render_engine=RenderTarget.REPORTLAB,
            format="svg",
            path=str(asset_path),
            width=600,
            height=200
        )
        self.asset_manager.registry.register(asset)
        return asset
