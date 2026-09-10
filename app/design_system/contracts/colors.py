"""
Universal Design System — Color System & Accessibility.

Phase 3B.0: Hex/RGB/ReportLab color representations, relative luminance,
and WCAG contrast ratio calculations with artifact-aware grading.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Tuple
from pydantic import BaseModel, ConfigDict, field_validator


class ContrastLevel(str, Enum):
    """Accessibility contrast classification based on WCAG 2.1 thresholds."""
    PASS_HIGH_CONTRAST = "PASS_HIGH_CONTRAST"      # >= 7.0 (AAA)
    PASS_ACCEPTABLE = "PASS_ACCEPTABLE"            # >= 4.5 (AA body)
    WARNING_LOW_CONTRAST = "WARNING_LOW_CONTRAST"  # >= 3.0 (AA large text / UI)
    FAIL_CRITICAL_CONTRAST = "FAIL_CRITICAL_CONTRAST" # < 3.0 (Unreadable)


class ColorRole(str, Enum):
    """Semantic functional roles for document colors."""
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    TEXT_PRIMARY = "TEXT_PRIMARY"
    TEXT_SECONDARY = "TEXT_SECONDARY"
    TEXT_MUTED = "TEXT_MUTED"
    BACKGROUND_PRIMARY = "BACKGROUND_PRIMARY"
    BACKGROUND_SECONDARY = "BACKGROUND_SECONDARY"
    SURFACE_PRIMARY = "SURFACE_PRIMARY"
    SURFACE_ELEVATED = "SURFACE_ELEVATED"
    BORDER_SUBTLE = "BORDER_SUBTLE"
    BORDER_STRONG = "BORDER_STRONG"
    ACCENT_PRIMARY = "ACCENT_PRIMARY"
    ACCENT_SECONDARY = "ACCENT_SECONDARY"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    DANGER = "DANGER"


class ColorValue(BaseModel):
    """Immutable color representation with cross-renderer conversions."""
    model_config = ConfigDict(frozen=True)

    hex: str  # e.g. "#2563eb" or "#ffffff"

    @field_validator("hex")
    @classmethod
    def validate_hex(cls, v: str) -> str:
        s = v.strip().lower()
        if not s.startswith("#"):
            s = f"#{s}"
        if len(s) == 4:  # #rgb -> #rrggbb
            s = f"#{s[1]*2}{s[2]*2}{s[3]*2}"
        if len(s) != 7 or any(c not in "0123456789abcdef" for c in s[1:]):
            raise ValueError(f"Invalid hexadecimal color: '{v}'")
        return s

    def to_rgb_tuple(self) -> Tuple[int, int, int]:
        """Returns (R, G, B) integer tuple in 0..255 range (for Pillow)."""
        r = int(self.hex[1:3], 16)
        g = int(self.hex[3:5], 16)
        b = int(self.hex[5:7], 16)
        return (r, g, b)

    def to_rgb_float_tuple(self) -> Tuple[float, float, float]:
        """Returns (R, G, B) float tuple in 0.0..1.0 range (for ReportLab)."""
        r, g, b = self.to_rgb_tuple()
        return (round(r / 255.0, 4), round(g / 255.0, 4), round(b / 255.0, 4))

    def to_rgba_css(self, alpha: float = 1.0) -> str:
        """Returns standard CSS rgba(r, g, b, a) string."""
        r, g, b = self.to_rgb_tuple()
        return f"rgba({r}, {g}, {b}, {alpha})"


def relative_luminance(color: ColorValue) -> float:
    """Calculates relative luminance according to WCAG 2.1 definition."""
    rgb_floats = color.to_rgb_float_tuple()
    s_rgb = []
    for c in rgb_floats:
        if c <= 0.04045:
            s_rgb.append(c / 12.92)
        else:
            s_rgb.append(math.pow((c + 0.055) / 1.055, 2.4))
    return round((0.2126 * s_rgb[0]) + (0.7152 * s_rgb[1]) + (0.0722 * s_rgb[2]), 5)


def contrast_ratio(foreground: ColorValue, background: ColorValue) -> float:
    """Computes WCAG contrast ratio (1.0 to 21.0)."""
    l1 = relative_luminance(foreground)
    l2 = relative_luminance(background)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def evaluate_contrast(foreground: ColorValue, background: ColorValue) -> Tuple[float, ContrastLevel]:
    """Evaluates contrast ratio and maps to canonical ContrastLevel."""
    ratio = contrast_ratio(foreground, background)
    if ratio >= 7.0:
        level = ContrastLevel.PASS_HIGH_CONTRAST
    elif ratio >= 4.5:
        level = ContrastLevel.PASS_ACCEPTABLE
    elif ratio >= 3.0:
        level = ContrastLevel.WARNING_LOW_CONTRAST
    else:
        level = ContrastLevel.FAIL_CRITICAL_CONTRAST
    return ratio, level
