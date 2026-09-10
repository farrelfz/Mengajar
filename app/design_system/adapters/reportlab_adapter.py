"""
Universal Design System — ReportLab Vector Adapter.

Phase 3B.0: Adapts design tokens and canvas specifications into ReportLab
Color, PageSize, and ParagraphStyle objects.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.styles import ParagraphStyle

from app.design_system.contracts.geometry import CanvasSpec
from app.design_system.contracts.colors import ColorValue
from app.design_system.registry.profile_registry import ProfileRegistry
from app.design_system.registry.font_registry import FontRegistry
from app.design_system.profiles import get_standard_profile_registry


class ReportLabDesignAdapter:
    """Binds canonical design system tokens to ReportLab vector primitives."""

    def __init__(
        self,
        profile_registry: Optional[ProfileRegistry] = None,
        font_registry: Optional[FontRegistry] = None,
    ) -> None:
        self.profile_registry = profile_registry or get_standard_profile_registry()
        self.font_registry = font_registry or FontRegistry()

    def get_color(self, hex_or_color: str | ColorValue) -> Color:
        """Converts a hex string or ColorValue to ReportLab Color."""
        if isinstance(hex_or_color, ColorValue):
            r, g, b = hex_or_color.to_rgb_float_tuple()
            return Color(r, g, b)
        return HexColor(hex_or_color)

    def get_page_geometry(self, artifact_type: str) -> Dict[str, Any]:
        """Returns ReportLab SimpleDocTemplate geometry parameters."""
        profile = self.profile_registry.get_profile_for_artifact(artifact_type)
        if not profile:
            # Safe default
            return {
                "pagesize": (595.28, 841.89),
                "topMargin": 45.35,
                "bottomMargin": 45.35,
                "leftMargin": 51.02,
                "rightMargin": 51.02,
            }

        canvas = profile.canvas_spec
        return {
            "pagesize": (canvas.width_pt, canvas.height_pt),
            "topMargin": canvas.safe_margin_top_pt,
            "bottomMargin": canvas.safe_margin_bottom_pt,
            "leftMargin": canvas.safe_margin_left_pt,
            "rightMargin": canvas.safe_margin_right_pt,
        }

    def get_paragraph_style(
        self,
        style_name: str,
        artifact_type: str,
        role: str = "body",
        font_weight: int = 400,
        font_style: str = "normal",
        font_color: str = "#0f172a",
    ) -> ParagraphStyle:
        """
        Creates a ReportLab ParagraphStyle strictly conforming to design profile
        minimum sizes and font face mapping (INV-DESIGN-004, INV-DESIGN-006).
        """
        profile = self.profile_registry.get_profile_for_artifact(artifact_type)
        face, _ = self.font_registry.resolve_font(
            family=profile.default_font_family if profile else "Inter",
            weight=font_weight,
            style=font_style,
        )

        # Determine size from profile role
        if profile and role in profile.token_overrides:
            font_size = float(profile.token_overrides[role])
        elif "title" in role.lower() or "h1" in role.lower():
            font_size = profile.min_heading_size_pt * 1.4 if profile else 20.0
        elif "heading" in role.lower() or "h2" in role.lower():
            font_size = profile.min_heading_size_pt * 1.1 if profile else 14.0
        elif "caption" in role.lower() or "citation" in role.lower():
            font_size = profile.min_caption_size_pt if profile else 8.0
        else:
            font_size = profile.min_body_size_pt if profile else 10.0

        # Enforce profile minimum
        if profile:
            _, min_req, _ = profile.validate_font_size(role, font_size)
            font_size = max(font_size, min_req)

        leading = round(font_size * 1.3, 1)

        return ParagraphStyle(
            name=style_name,
            fontName=face.reportlab_name,
            fontSize=font_size,
            leading=leading,
            textColor=self.get_color(font_color),
        )
