"""
Universal Design System — Spacing Contracts.

Phase 3B.0: Canonical spacing scale and unit conversions.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict
from app.design_system.contracts.geometry import pt_to_mm, pt_to_px


class SpacingScale(str, Enum):
    """Canonical spacing steps."""
    NONE = "NONE"      # 0 pt
    XXS = "XXS"        # 2 pt
    XS = "XS"          # 4 pt
    SM = "SM"          # 8 pt
    MD = "MD"          # 16 pt
    LG = "LG"          # 24 pt
    XL = "XL"          # 32 pt
    XXL = "XXL"        # 48 pt
    XXXL = "XXXL"      # 64 pt


SPACING_PT_MAP = {
    SpacingScale.NONE: 0.0,
    SpacingScale.XXS: 2.0,
    SpacingScale.XS: 4.0,
    SpacingScale.SM: 8.0,
    SpacingScale.MD: 16.0,
    SpacingScale.LG: 24.0,
    SpacingScale.XL: 32.0,
    SpacingScale.XXL: 48.0,
    SpacingScale.XXXL: 64.0,
}


class SpacingToken(BaseModel):
    """Unit-aware spacing token."""
    model_config = ConfigDict(frozen=True)

    scale: SpacingScale
    size_pt: float

    @classmethod
    def from_scale(cls, scale: SpacingScale) -> SpacingToken:
        return cls(scale=scale, size_pt=SPACING_PT_MAP[scale])

    def to_px(self, dpi: float = 96.0) -> float:
        return pt_to_px(self.size_pt, dpi)

    def to_mm(self) -> float:
        return pt_to_mm(self.size_pt)
