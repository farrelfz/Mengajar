"""Unit tests for Universal Design System Typography and Font Registry."""

import pytest
from app.design_system.contracts.typography import (
    FontFace,
    TypographyScale,
    TypographySpec,
)
from app.design_system.registry.font_registry import FontRegistry


def test_font_registry_defaults_and_aliases():
    """Verifies default cross-renderer font faces and alias mappings."""
    registry = FontRegistry()

    # Inter sans-serif default
    inter, fallback = registry.resolve_font("Inter", weight=400, style="normal")
    assert not fallback
    assert inter.family == "Inter"
    assert inter.reportlab_name == "Helvetica"
    assert "Inter" in inter.html_family

    # Alias 'sans' resolves to Inter
    sans, fallback = registry.resolve_font("sans", weight=700, style="normal")
    assert not fallback
    assert sans.family == "Inter"
    assert sans.reportlab_name == "Helvetica-Bold"

    # Alias 'serif' resolves to Merriweather
    serif, fallback = registry.resolve_font("serif", weight=400, style="normal")
    assert not fallback
    assert serif.family == "Merriweather"
    assert serif.reportlab_name == "Times-Roman"


def test_font_registry_deterministic_fallback():
    """Verifies graceful fallback when requesting an uninstalled font family."""
    registry = FontRegistry()

    unknown_font, fallback = registry.resolve_font("FantasyComicSans", weight=400, style="normal")
    assert fallback is True
    assert unknown_font.family == "Inter"  # Safe base fallback
    assert unknown_font.reportlab_name == "Helvetica"


def test_typography_spec_computed_line_height():
    """Verifies line-height calculation from nominal size and multiplier."""
    face = FontFace(family="Inter", weight=400, style="normal")
    spec = TypographySpec(
        font_face=face,
        nominal_size_pt=10.0,
        min_size_pt=8.0,
        max_size_pt=14.0,
        line_height_multiplier=1.4,
    )
    assert spec.computed_line_height_pt == 14.0
