"""Unit tests for Universal Design System Color values and WCAG Contrast calculations."""

import pytest
from app.design_system.contracts.colors import (
    ColorValue,
    ContrastLevel,
    contrast_ratio,
    evaluate_contrast,
    relative_luminance,
)


def test_color_value_normalization_and_conversions():
    """Verifies hex string validation, 3-char expansion, and RGB conversions."""
    # 3-char expansion
    c1 = ColorValue(hex="#fff")
    assert c1.hex == "#ffffff"
    assert c1.to_rgb_tuple() == (255, 255, 255)
    assert c1.to_rgb_float_tuple() == (1.0, 1.0, 1.0)
    assert c1.to_rgba_css(0.5) == "rgba(255, 255, 255, 0.5)"

    # Slate 900
    c2 = ColorValue(hex="0f172a")  # without #
    assert c2.hex == "#0f172a"
    assert c2.to_rgb_tuple() == (15, 23, 42)


def test_invalid_hex_raises_value_error():
    """Verifies that malformed colors raise clear ValueError."""
    with pytest.raises(ValueError):
        ColorValue(hex="#invalid")
    with pytest.raises(ValueError):
        ColorValue(hex="#12345")


def test_wcag_relative_luminance_and_contrast_ratio():
    """Verifies pure black on white contrast equals 21.0."""
    white = ColorValue(hex="#ffffff")
    black = ColorValue(hex="#000000")

    assert relative_luminance(white) == 1.0
    assert relative_luminance(black) == 0.0

    ratio, level = evaluate_contrast(black, white)
    assert ratio == 21.0
    assert level == ContrastLevel.PASS_HIGH_CONTRAST


def test_low_contrast_detection():
    """Verifies that poor contrast is flagged as WARNING or FAIL."""
    light_gray = ColorValue(hex="#cbd5e1")
    white = ColorValue(hex="#ffffff")

    ratio, level = evaluate_contrast(light_gray, white)
    assert ratio < 3.0
    assert level == ContrastLevel.FAIL_CRITICAL_CONTRAST
