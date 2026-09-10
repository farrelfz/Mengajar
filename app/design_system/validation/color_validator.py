"""
Universal Design System — Color Contrast Validator.

Phase 3B.0: Enforces WCAG 2.1 AA accessibility contrast thresholds (INV-DESIGN-003).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.design_system.contracts.colors import (
    ColorValue,
    ContrastLevel,
    contrast_ratio,
    evaluate_contrast,
)


class ColorContrastFinding:
    """Design-level finding for color contrast non-conformance."""
    def __init__(
        self,
        element_id: str,
        foreground_hex: str,
        background_hex: str,
        contrast_ratio: float,
        level: ContrastLevel,
        min_required_ratio: float,
        is_large_text: bool,
        message: str,
    ) -> None:
        self.element_id = element_id
        self.foreground_hex = foreground_hex
        self.background_hex = background_hex
        self.contrast_ratio = contrast_ratio
        self.level = level
        self.min_required_ratio = min_required_ratio
        self.is_large_text = is_large_text
        self.message = message


class ColorValidator:
    """Validates color combinations and accessible contrast ratios."""

    def validate_pair(
        self,
        element_id: str,
        foreground_hex: str,
        background_hex: str,
        is_large_text: bool = False,
    ) -> Optional[ColorContrastFinding]:
        """
        Validates whether the contrast ratio meets WCAG AA standards:
        - Normal text (< 18pt or < 14pt bold): minimum 4.5:1
        - Large text (>= 18pt or >= 14pt bold): minimum 3.0:1
        """
        fg = ColorValue(hex=foreground_hex)
        bg = ColorValue(hex=background_hex)
        ratio, level = evaluate_contrast(fg, bg)

        min_required = 3.0 if is_large_text else 4.5

        if ratio < min_required:
            msg = (
                f"Element '{element_id}' has contrast ratio of {ratio:.2f}:1 "
                f"(foreground: {foreground_hex}, background: {background_hex}), "
                f"failing WCAG AA threshold of {min_required:.1f}:1."
            )
            return ColorContrastFinding(
                element_id=element_id,
                foreground_hex=foreground_hex,
                background_hex=background_hex,
                contrast_ratio=ratio,
                level=level,
                min_required_ratio=min_required,
                is_large_text=is_large_text,
                message=msg,
            )
        return None
