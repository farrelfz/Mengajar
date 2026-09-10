"""Unit tests for DesignAwareRepairResolver integration with repair mutations."""

import pytest
from app.design_system.contracts.spacing import SpacingScale
from app.quality.repair.design_resolver import DesignAwareRepairResolver


def test_design_aware_repair_resolver_clamps_to_floor():
    """Verifies that font downscaling mutations are clamped to profile floor."""
    resolver = DesignAwareRepairResolver()

    # Presentation body floor is 11.0 pt
    safe_size, clamped = resolver.resolve_safe_font_size(
        artifact_type="PRESENTATION",
        role="body",
        target_size_pt=8.5,
    )
    assert clamped is True
    assert safe_size == 11.0

    # Presentation title floor is 14.0 pt
    safe_title, clamped_title = resolver.resolve_safe_font_size(
        artifact_type="PRESENTATION",
        role="title",
        target_size_pt=10.0,
    )
    assert clamped_title is True
    assert safe_title == 14.0


def test_discrete_spacing_stepping():
    """Verifies that spacing changes step discretely along SpacingScale."""
    resolver = DesignAwareRepairResolver()

    step_down = resolver.step_spacing(SpacingScale.MD, direction="decrease")
    assert step_down.scale == SpacingScale.SM
    assert step_down.size_pt == 8.0

    step_up = resolver.step_spacing(SpacingScale.MD, direction="increase")
    assert step_up.scale == SpacingScale.LG
    assert step_up.size_pt == 24.0


def test_accessible_color_resolution():
    """Verifies that accessible foreground text color is chosen for light/dark backgrounds."""
    resolver = DesignAwareRepairResolver()

    # On dark navy background, should pick white text
    dark_bg = "#0f172a"
    fg_on_dark = resolver.resolve_accessible_text_color(dark_bg)
    assert fg_on_dark == "#ffffff"

    # On light background, should pick dark slate text
    light_bg = "#f8fafc"
    fg_on_light = resolver.resolve_accessible_text_color(light_bg)
    assert fg_on_light == "#0f172a"
