"""
Universal Design System & Asset Library.

Phase 3B.0: Single source of truth for visual and physical document primitives
across HTML/CSS, ReportLab vector, and raster renderers.
"""

from app.design_system.resolver import DesignTokenResolver
from app.design_system.validation.quality_bridge import DesignSystemQualityBridge

__all__ = [
    "DesignTokenResolver",
    "DesignSystemQualityBridge",
]
