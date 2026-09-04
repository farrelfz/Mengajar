"""
KIR AI Document Intelligence — Python Visualization Engine.
"""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from app.rendering.schemas import AssetMetadata, RenderTarget
from app.design.schemas import ComponentFamily

class MatplotlibRenderer:
    def __init__(self, asset_manager):
        self.asset_manager = asset_manager
        
    def render_component(self, block_id: str, component_family: ComponentFamily, context: dict) -> AssetMetadata:
        asset_path = self.asset_manager.generate_asset_path(block_id, "svg")
        
        plt.figure(figsize=(6, 4))
        
        if component_family == ComponentFamily.DATA_BLOCK:
            categories = ['A', 'B', 'C', 'D']
            values = [4, 7, 1, 8]
            plt.bar(categories, values, color='#3498db')
            plt.title("Sample Data Bar Chart")
            plt.ylabel("Value")
        else:
            x = np.linspace(0, 10, 100)
            y = np.sin(x)
            plt.plot(x, y, color='#e74c3c')
            plt.title(f"Sample Visual: {component_family.value}")
            
        plt.tight_layout()
        plt.savefig(str(asset_path), format='svg', bbox_inches='tight')
        plt.close()
        
        asset = AssetMetadata(
            asset_id=block_id,
            asset_type="data_chart",
            source_component_id=block_id,
            render_engine=RenderTarget.PYTHON_VISUAL,
            format="svg",
            path=str(asset_path),
            width=600,
            height=400
        )
        self.asset_manager.registry.register(asset)
        return asset
