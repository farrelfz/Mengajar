"""
KIR AI Document Intelligence — Rendering Contracts.
"""
from typing import Protocol
from pathlib import Path
from app.composition.schemas import DocumentComposition
from app.rendering.schemas import RenderResult, AssetMetadata

class HybridRenderEngine(Protocol):
    def render(self, composition: DocumentComposition, output_dir: Path) -> RenderResult:
        ...

class ComponentRenderer(Protocol):
    def render(self, block_id: str, context: dict, output_dir: Path) -> AssetMetadata | str:
        ...
