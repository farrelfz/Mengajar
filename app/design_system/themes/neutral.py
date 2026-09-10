"""
Universal Design System — Neutral Theme.

Phase 3B.0: Minimalist monochrome theme for general document presentation.
"""

from __future__ import annotations

from app.design_system.themes.base import ThemeDefinition, get_base_theme


def get_neutral_theme() -> ThemeDefinition:
    """Constructs the clean minimalist theme."""
    base = get_base_theme()
    return ThemeDefinition(
        theme_id="neutral",
        name="Neutral Theme",
        description="Distraction-free minimalist monochrome theme",
        raw_tokens=base.raw_tokens,
        semantic_tokens=base.semantic_tokens,
    )
