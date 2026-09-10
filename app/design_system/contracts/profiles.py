"""
Universal Design System — Profile Contracts.

Phase 3B.0: Canonical base contract for format-specific design profiles
(Presentation, Handout, Worksheet, Scientific Document).
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field
from app.design_system.contracts.geometry import CanvasSpec
from app.design_system.contracts.components import ComponentCategory


class DesignProfile(BaseModel):
    """Specification of a format-specific design profile."""
    model_config = ConfigDict(frozen=True)

    profile_id: str
    artifact_type: str  # "PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"
    canvas_spec: CanvasSpec
    default_theme_id: str = "base"
    min_heading_size_pt: float = 14.0
    min_body_size_pt: float = 9.0
    min_caption_size_pt: float = 7.0
    max_density_weight_per_page: float = 10.0
    default_font_family: str = "Inter"
    allowed_component_categories: Tuple[ComponentCategory, ...] = tuple(ComponentCategory)
    token_overrides: Dict[str, Any] = Field(default_factory=dict)
    anti_spoiling_required: bool = False
    citation_required: bool = False
    description: str = ""

    def validate_font_size(self, role: str, size_pt: float) -> Tuple[bool, float, str]:
        """
        Validates whether a font size meets the profile's minimum requirements (INV-DESIGN-006).
        Returns (is_valid, minimum_required, violation_message).
        """
        role_upper = role.upper()
        if "HEADING" in role_upper or "TITLE" in role_upper or "DISPLAY" in role_upper:
            min_size = self.min_heading_size_pt
        elif "CAPTION" in role_upper or "MICRO" in role_upper:
            min_size = self.min_caption_size_pt
        else:
            min_size = self.min_body_size_pt

        if size_pt < min_size:
            return False, min_size, (
                f"Font size {size_pt:.2f}pt for role '{role}' in {self.artifact_type} "
                f"violates minimum required size of {min_size:.2f}pt."
            )
        return True, min_size, ""
