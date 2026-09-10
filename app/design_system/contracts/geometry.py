"""
Universal Design System — Geometry & Physical Units.

Phase 3B.0: Deterministic unit conversions and canonical canvas specifications
for Presentation (16:9) and Documents (A4 Portrait/Landscape).
"""

from __future__ import annotations

from typing import Tuple
from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# 1. PHYSICAL UNIT CONVERSION UTILITIES
# =============================================================================

PT_PER_INCH = 72.0
MM_PER_INCH = 25.4
PT_PER_MM = PT_PER_INCH / MM_PER_INCH  # ~2.83464566929


def px_to_pt(px: float, dpi: float = 96.0) -> float:
    """Converts CSS/screen pixels to physical typographic points (72 pt = 1 inch)."""
    return round((px / dpi) * PT_PER_INCH, 4)


def pt_to_px(pt: float, dpi: float = 96.0) -> float:
    """Converts typographic points to pixels at specified DPI (default 96 DPI)."""
    return round((pt / PT_PER_INCH) * dpi, 4)


def mm_to_pt(mm: float) -> float:
    """Converts millimeters to typographic points."""
    return round(mm * PT_PER_MM, 4)


def pt_to_mm(pt: float) -> float:
    """Converts typographic points to millimeters."""
    return round(pt / PT_PER_MM, 4)


def inch_to_pt(inch: float) -> float:
    """Converts inches to typographic points."""
    return round(inch * PT_PER_INCH, 4)


def pt_to_inch(pt: float) -> float:
    """Converts typographic points to inches."""
    return round(pt / PT_PER_INCH, 4)


# =============================================================================
# 2. CANVAS SPECIFICATION
# =============================================================================

class CanvasSpec(BaseModel):
    """Physical dimensions, safe margins, and coordinate boundaries for an artifact page."""
    model_config = ConfigDict(frozen=True)

    name: str
    width_pt: float
    height_pt: float
    orientation: str = "portrait"  # "portrait" or "landscape"
    aspect_ratio: str = "1:1.414"  # "16:9" or "1:1.414" (A4)
    safe_margin_top_pt: float
    safe_margin_bottom_pt: float
    safe_margin_left_pt: float
    safe_margin_right_pt: float
    bleed_margin_pt: float = 0.0

    @property
    def printable_width_pt(self) -> float:
        return self.width_pt - (self.safe_margin_left_pt + self.safe_margin_right_pt)

    @property
    def printable_height_pt(self) -> float:
        return self.height_pt - (self.safe_margin_top_pt + self.safe_margin_bottom_pt)

    @property
    def total_area_pt(self) -> float:
        return self.width_pt * self.height_pt

    @property
    def printable_area_pt(self) -> float:
        return max(0.0, self.printable_width_pt * self.printable_height_pt)


# =============================================================================
# 3. CANONICAL PREDEFINED CANVASES
# =============================================================================

# Presentation 16:9 (960pt x 540pt = 13.333in x 7.5in; 1280px x 720px at 96 DPI)
PRESENTATION_16_9_CANVAS = CanvasSpec(
    name="Presentation 16:9",
    width_pt=960.0,
    height_pt=540.0,
    orientation="landscape",
    aspect_ratio="16:9",
    safe_margin_top_pt=28.8,    # 0.4 in
    safe_margin_bottom_pt=28.8, # 0.4 in
    safe_margin_left_pt=50.4,   # 0.7 in
    safe_margin_right_pt=50.4,  # 0.7 in
)

# A4 Portrait (210mm x 297mm = 595.28pt x 841.89pt)
A4_PORTRAIT_CANVAS = CanvasSpec(
    name="A4 Portrait",
    width_pt=mm_to_pt(210.0),   # 595.2756 pt
    height_pt=mm_to_pt(297.0),  # 841.8898 pt
    orientation="portrait",
    aspect_ratio="1:1.414",
    safe_margin_top_pt=mm_to_pt(16.0),    # 45.3543 pt
    safe_margin_bottom_pt=mm_to_pt(16.0), # 45.3543 pt
    safe_margin_left_pt=mm_to_pt(18.0),   # 51.0236 pt
    safe_margin_right_pt=mm_to_pt(18.0),  # 51.0236 pt
)

# A4 Landscape (297mm x 210mm = 841.89pt x 595.28pt)
A4_LANDSCAPE_CANVAS = CanvasSpec(
    name="A4 Landscape",
    width_pt=mm_to_pt(297.0),
    height_pt=mm_to_pt(210.0),
    orientation="landscape",
    aspect_ratio="1.414:1",
    safe_margin_top_pt=mm_to_pt(12.0),
    safe_margin_bottom_pt=mm_to_pt(12.0),
    safe_margin_left_pt=mm_to_pt(18.0),
    safe_margin_right_pt=mm_to_pt(18.0),
)
