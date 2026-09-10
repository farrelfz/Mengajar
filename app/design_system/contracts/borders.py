"""
Universal Design System — Border & Corner Radius Contracts.

Phase 3B.0: Canonical border widths, styles, and corner radii.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict
from app.design_system.contracts.colors import ColorValue


class RadiusScale(str, Enum):
    """Canonical border radius scale."""
    NONE = "NONE"  # 0 pt
    SM = "SM"      # 4 pt
    MD = "MD"      # 8 pt
    LG = "LG"      # 12 pt
    FULL = "FULL"  # 9999 pt (pill badge)


RADIUS_PT_MAP = {
    RadiusScale.NONE: 0.0,
    RadiusScale.SM: 4.0,
    RadiusScale.MD: 8.0,
    RadiusScale.LG: 12.0,
    RadiusScale.FULL: 9999.0,
}


class BorderStyle(str, Enum):
    """Canonical border line styles."""
    SOLID = "SOLID"
    DASHED = "DASHED"
    DOTTED = "DOTTED"
    NONE = "NONE"


class BorderSpec(BaseModel):
    """Complete border and radius specification."""
    model_config = ConfigDict(frozen=True)

    width_pt: float = 1.0
    style: BorderStyle = BorderStyle.SOLID
    color: ColorValue = ColorValue(hex="#e2e8f0")
    radius: RadiusScale = RadiusScale.NONE

    @property
    def radius_pt(self) -> float:
        return RADIUS_PT_MAP[self.radius]
