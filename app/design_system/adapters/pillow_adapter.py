"""
Universal Design System — Pillow Raster Adapter.

Phase 3B.0: Raster pixel canvas sizing, margin offsets, and integer RGB colors
for screenshot rendering and image export.
"""

from __future__ import annotations

from typing import Optional, Tuple
from app.design_system.contracts.geometry import pt_to_px
from app.design_system.contracts.colors import ColorValue
from app.design_system.registry.profile_registry import ProfileRegistry
from app.design_system.profiles import get_standard_profile_registry


class PillowDesignAdapter:
    """Binds design system geometry and colors to Pillow pixel coordinates."""

    def __init__(self, profile_registry: Optional[ProfileRegistry] = None) -> None:
        self.profile_registry = profile_registry or get_standard_profile_registry()

    def get_pixel_dimensions(
        self, artifact_type: str, dpi: float = 96.0
    ) -> Tuple[int, int]:
        """Returns (width_px, height_px) rounded to nearest integer."""
        profile = self.profile_registry.get_profile_for_artifact(artifact_type)
        if not profile:
            return (round(pt_to_px(595.28, dpi)), round(pt_to_px(841.89, dpi)))

        width_px = round(pt_to_px(profile.canvas_spec.width_pt, dpi))
        height_px = round(pt_to_px(profile.canvas_spec.height_pt, dpi))
        return (width_px, height_px)

    def get_pixel_margins(
        self, artifact_type: str, dpi: float = 96.0
    ) -> Tuple[int, int, int, int]:
        """Returns (top, right, bottom, left) margins in pixels."""
        profile = self.profile_registry.get_profile_for_artifact(artifact_type)
        if not profile:
            return (45, 51, 45, 51)

        c = profile.canvas_spec
        return (
            round(pt_to_px(c.safe_margin_top_pt, dpi)),
            round(pt_to_px(c.safe_margin_right_pt, dpi)),
            round(pt_to_px(c.safe_margin_bottom_pt, dpi)),
            round(pt_to_px(c.safe_margin_left_pt, dpi)),
        )

    def get_rgb_tuple(self, hex_or_color: str | ColorValue) -> Tuple[int, int, int]:
        """Converts hex string or ColorValue to Pillow (R, G, B) tuple."""
        if isinstance(hex_or_color, ColorValue):
            return hex_or_color.to_rgb_tuple()
        return ColorValue(hex=hex_or_color).to_rgb_tuple()
