"""
Universal Design System — PyMuPDF Inspection Adapter.

Phase 3B.0: Supplies canonical bounding box geometry, printable rects,
and minimum font size thresholds to physical PDF quality inspectors.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple
from app.design_system.registry.profile_registry import ProfileRegistry
from app.design_system.profiles import get_standard_profile_registry


class PyMuPdfDesignAdapter:
    """Provides design system geometry expectations and thresholds for PDF inspectors."""

    def __init__(self, profile_registry: Optional[ProfileRegistry] = None) -> None:
        self.profile_registry = profile_registry or get_standard_profile_registry()

    def get_expected_page_rect(self, artifact_type: str) -> Tuple[float, float, float, float]:
        """
        Returns (x0, y0, x1, y1) expected page rectangle in points for PyMuPDF page.rect.
        """
        profile = self.profile_registry.get_profile_for_artifact(artifact_type)
        if not profile:
            return (0.0, 0.0, 595.28, 841.89)

        return (0.0, 0.0, profile.canvas_spec.width_pt, profile.canvas_spec.height_pt)

    def get_printable_safe_rect(self, artifact_type: str) -> Tuple[float, float, float, float]:
        """
        Returns (x0, y0, x1, y1) printable safe inner rectangle in points.
        """
        profile = self.profile_registry.get_profile_for_artifact(artifact_type)
        if not profile:
            return (51.0, 45.0, 544.0, 796.0)

        canvas = profile.canvas_spec
        return (
            canvas.safe_margin_left_pt,
            canvas.safe_margin_top_pt,
            canvas.width_pt - canvas.safe_margin_right_pt,
            canvas.height_pt - canvas.safe_margin_bottom_pt,
        )

    def get_minimum_font_thresholds(self, artifact_type: str) -> Dict[str, float]:
        """
        Returns font size floor thresholds for the artifact type.
        Used by pdf_inspector.py to replace hardcoded values.
        """
        profile = self.profile_registry.get_profile_for_artifact(artifact_type)
        if not profile:
            return {"heading": 12.0, "body": 9.0, "caption": 7.0}

        return {
            "heading": profile.min_heading_size_pt,
            "body": profile.min_body_size_pt,
            "caption": profile.min_caption_size_pt,
        }
