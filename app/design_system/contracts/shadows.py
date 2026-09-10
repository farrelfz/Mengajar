"""
Universal Design System — Elevation & Shadows.

Phase 3B.0: Canonical elevation scale with HTML CSS shadow and ReportLab border fallbacks.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict


class ElevationScale(str, Enum):
    """Canonical surface elevation steps."""
    FLAT = "FLAT"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ShadowSpec(BaseModel):
    """Elevation shadow specification with cross-renderer fallback."""
    model_config = ConfigDict(frozen=True)

    elevation: ElevationScale
    css_box_shadow: str
    reportlab_fallback_border_width_pt: float = 0.0
    reportlab_fallback_border_color_hex: str = "#e2e8f0"


SHADOW_MAP = {
    ElevationScale.FLAT: ShadowSpec(
        elevation=ElevationScale.FLAT,
        css_box_shadow="none",
        reportlab_fallback_border_width_pt=0.0,
    ),
    ElevationScale.LOW: ShadowSpec(
        elevation=ElevationScale.LOW,
        css_box_shadow="0 1px 3px 0 rgba(0, 0, 0, 0.05)",
        reportlab_fallback_border_width_pt=0.5,
        reportlab_fallback_border_color_hex="#e2e8f0",
    ),
    ElevationScale.MEDIUM: ShadowSpec(
        elevation=ElevationScale.MEDIUM,
        css_box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.07)",
        reportlab_fallback_border_width_pt=1.0,
        reportlab_fallback_border_color_hex="#cbd5e1",
    ),
    ElevationScale.HIGH: ShadowSpec(
        elevation=ElevationScale.HIGH,
        css_box_shadow="0 10px 15px -3px rgba(0, 0, 0, 0.1)",
        reportlab_fallback_border_width_pt=1.5,
        reportlab_fallback_border_color_hex="#94a3b8",
    ),
}
