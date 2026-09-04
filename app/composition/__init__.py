"""
KIR AI Document Intelligence — Composition Module.
"""
from app.composition.engine import DocumentComposer
from app.composition.schemas import DocumentComposition, PageComposition, RegionRole, ContentBlock

__all__ = [
    "DocumentComposer",
    "DocumentComposition",
    "PageComposition",
    "RegionRole",
    "ContentBlock"
]
