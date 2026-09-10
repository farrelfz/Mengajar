"""Unit tests for Cross-Renderer Physical Parity Validator."""

import pytest
from app.design_system.validation.parity_validator import CrossRendererParityValidator


def test_cross_renderer_parity_standard_suite():
    """Verifies that canonical tokens maintain physical parity across HTML, ReportLab, and Pillow."""
    validator = CrossRendererParityValidator()
    report = validator.validate_standard_suite("PRESENTATION")

    assert report.total_checked > 0
    assert report.total_passed == report.total_checked
    assert report.has_discrepancies is False


def test_individual_color_and_size_parity():
    """Checks individual color conversion and point-to-pixel raster parity."""
    validator = CrossRendererParityValidator()

    # Color text primary
    item_color = validator.validate_token("color.text.primary", "PRESENTATION")
    assert item_color.is_parity_preserved is True
    assert item_color.html_value == "#0f172a"
    assert isinstance(item_color.reportlab_value, tuple)
    assert isinstance(item_color.pillow_value, tuple)

    # Spacing 16pt (16pt * 96/72 = 21.33px ≈ 21px)
    item_space = validator.validate_token("spacing.16", "PRESENTATION")
    assert item_space.is_parity_preserved is True
