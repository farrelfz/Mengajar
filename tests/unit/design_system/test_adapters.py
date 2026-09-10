"""Unit tests for HTML, ReportLab, PyMuPDF, and Pillow design adapters."""

import pytest
from app.design_system.adapters.html_adapter import HtmlDesignAdapter
from app.design_system.adapters.reportlab_adapter import ReportLabDesignAdapter
from app.design_system.adapters.pymupdf_adapter import PyMuPdfDesignAdapter
from app.design_system.adapters.pillow_adapter import PillowDesignAdapter


def test_html_adapter_css_generation():
    """Verifies CSS custom property and canvas stylesheet generation."""
    adapter = HtmlDesignAdapter()
    css_vars = adapter.generate_css_variables()
    assert "--ds-color-text-primary:" in css_vars
    assert "--ds-color-slate-900:" in css_vars

    pres_css = adapter.generate_canvas_css("PRESENTATION")
    assert "960.0pt" in pres_css
    assert "540.0pt" in pres_css
    assert "aspect-ratio: 16 / 9;" in pres_css

    handout_css = adapter.generate_canvas_css("HANDOUT")
    assert "210.00mm" in handout_css
    assert "297.00mm" in handout_css


def test_reportlab_adapter_geometry_and_styles():
    """Verifies ReportLab geometry, color, and ParagraphStyle bindings."""
    adapter = ReportLabDesignAdapter()

    # Geometry for Presentation 16:9
    geo_pres = adapter.get_page_geometry("PRESENTATION")
    assert geo_pres["pagesize"] == (960.0, 540.0)

    # Geometry for Handout A4
    geo_handout = adapter.get_page_geometry("HANDOUT")
    assert round(geo_handout["pagesize"][0], 1) == 595.3

    # Paragraph style enforces minimum font size
    style = adapter.get_paragraph_style(
        style_name="TestBody",
        artifact_type="PRESENTATION",
        role="body",
    )
    assert style.fontSize >= 11.0  # Presentation body floor
    assert style.fontName == "Helvetica"


def test_pymupdf_adapter_geometry_and_floors():
    """Verifies PyMuPDF page bounds and dynamic minimum font floors."""
    adapter = PyMuPdfDesignAdapter()

    rect_pres = adapter.get_expected_page_rect("PRESENTATION")
    assert rect_pres == (0.0, 0.0, 960.0, 540.0)

    floors_pres = adapter.get_minimum_font_thresholds("PRESENTATION")
    assert floors_pres["body"] == 11.0

    floors_sci = adapter.get_minimum_font_thresholds("SCIENTIFIC_DOCUMENT")
    assert floors_sci["body"] == 8.0


def test_pillow_adapter_pixel_conversions():
    """Verifies pixel dimensions at specified DPI."""
    adapter = PillowDesignAdapter()

    dims_96 = adapter.get_pixel_dimensions("PRESENTATION", dpi=96.0)
    assert dims_96 == (1280, 720)

    rgb = adapter.get_rgb_tuple("#2563eb")
    assert rgb == (37, 99, 235)
