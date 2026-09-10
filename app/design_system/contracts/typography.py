"""
Universal Design System — Typography Contracts.

Phase 3B.0: FontFace specifications, cross-renderer font mapping,
typographic scales, and typography specifications with strict minimum boundaries.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TypographyScale(str, Enum):
    """Canonical typographic scale steps."""
    DISPLAY_XL = "DISPLAY_XL"
    DISPLAY_L = "DISPLAY_L"
    DISPLAY_M = "DISPLAY_M"
    HEADING_XL = "HEADING_XL"
    HEADING_L = "HEADING_L"
    HEADING_M = "HEADING_M"
    HEADING_S = "HEADING_S"
    BODY_L = "BODY_L"
    BODY_M = "BODY_M"
    BODY_S = "BODY_S"
    CAPTION = "CAPTION"
    MICRO = "MICRO"


class FontFace(BaseModel):
    """Cross-renderer font face definition."""
    model_config = ConfigDict(frozen=True)

    family: str
    weight: int = 400
    style: str = "normal"
    path: Optional[str] = None
    html_family: str = "sans-serif"
    reportlab_name: str = "Helvetica"
    is_embeddable: bool = True
    unicode_capable: bool = True


class TypographySpec(BaseModel):
    """Complete specification for a typographic style step."""
    model_config = ConfigDict(frozen=True)

    font_face: FontFace
    nominal_size_pt: float
    min_size_pt: float
    max_size_pt: float
    line_height_multiplier: float = 1.3
    letter_spacing_pt: float = 0.0
    paragraph_spacing_pt: float = 8.0
    font_weight: int = 400
    is_bold: bool = False
    is_italic: bool = False

    @property
    def computed_line_height_pt(self) -> float:
        return round(self.nominal_size_pt * self.line_height_multiplier, 2)
