"""Unit tests for Universal Design System Geometry and Physical Unit conversions."""

import pytest
from app.design_system.contracts.geometry import (
    px_to_pt,
    pt_to_px,
    mm_to_pt,
    pt_to_mm,
    inch_to_pt,
    pt_to_inch,
    PRESENTATION_16_9_CANVAS,
    A4_PORTRAIT_CANVAS,
    A4_LANDSCAPE_CANVAS,
)


def test_unit_conversions_bidirectional_consistency():
    """Verifies that unit conversions invert faithfully without drift."""
    # 72 points = 1 inch
    assert inch_to_pt(1.0) == 72.0
    assert pt_to_inch(72.0) == 1.0

    # 96 px = 72 pt at 96 DPI
    assert px_to_pt(96.0, dpi=96.0) == 72.0
    assert pt_to_px(72.0, dpi=96.0) == 96.0

    # Millimeters round-trip
    mm_val = 210.0
    pt_val = mm_to_pt(mm_val)
    assert abs(pt_to_mm(pt_val) - mm_val) < 0.01


def test_presentation_canvas_spec():
    """Verifies 16:9 Presentation canvas specifications."""
    c = PRESENTATION_16_9_CANVAS
    assert c.width_pt == 960.0
    assert c.height_pt == 540.0
    assert c.aspect_ratio == "16:9"
    assert c.printable_width_pt == 960.0 - (50.4 * 2)
    assert c.printable_height_pt == 540.0 - (28.8 * 2)
    assert c.printable_area_pt > 0


def test_a4_canvas_spec():
    """Verifies standard A4 dimensions (210mm x 297mm)."""
    portrait = A4_PORTRAIT_CANVAS
    assert round(pt_to_mm(portrait.width_pt), 1) == 210.0
    assert round(pt_to_mm(portrait.height_pt), 1) == 297.0
    assert portrait.orientation == "portrait"

    landscape = A4_LANDSCAPE_CANVAS
    assert round(pt_to_mm(landscape.width_pt), 1) == 297.0
    assert round(pt_to_mm(landscape.height_pt), 1) == 210.0
    assert landscape.orientation == "landscape"
