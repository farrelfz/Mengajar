"""
Integration tests for Cross-Format Parity and Profile Distinctness.

Phase 3B.0: Asserts that all four artifact types maintain distinct, non-collapsing
design identities, enforce their respective architectural invariants, and resolve
consistently across HTML, ReportLab, and raster targets.
"""

import pytest
from app.design_system.profiles import get_standard_profile_registry
from app.design_system.resolver import DesignTokenResolver
from app.design_system.registry.component_registry import ComponentRegistry
from app.design_system.contracts.components import ComponentCategory


def test_four_formats_profile_distinctness():
    """Verifies that all 4 formats have unique geometries and distinct constraints."""
    registry = get_standard_profile_registry()
    formats = ["PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"]

    profiles = {fmt: registry.get_profile_for_artifact(fmt) for fmt in formats}

    # 1. Geometries are non-identical
    assert profiles["PRESENTATION"].canvas_spec.aspect_ratio == "16:9"
    assert profiles["HANDOUT"].canvas_spec.aspect_ratio == "1:1.414"

    # 2. Minimum body font sizes are differentiated
    assert profiles["PRESENTATION"].min_body_size_pt == 11.0
    assert profiles["HANDOUT"].min_body_size_pt == 8.5
    assert profiles["WORKSHEET"].min_body_size_pt == 9.0
    assert profiles["SCIENTIFIC_DOCUMENT"].min_body_size_pt == 8.0

    # 3. Invariant flags are format-specific
    assert profiles["WORKSHEET"].anti_spoiling_required is True
    assert profiles["PRESENTATION"].anti_spoiling_required is False

    assert profiles["SCIENTIFIC_DOCUMENT"].citation_required is True
    assert profiles["PRESENTATION"].citation_required is False

    # 4. Font families
    assert profiles["SCIENTIFIC_DOCUMENT"].default_font_family == "Merriweather"
    assert profiles["PRESENTATION"].default_font_family == "Inter"


def test_cross_renderer_resolution_parity():
    """Verifies that token resolution produces coherent types across renderers."""
    resolver = DesignTokenResolver()

    # Color primary across HTML, ReportLab, and Pillow
    tok_html, _ = resolver.resolve("color.text.primary", "PRESENTATION", "HTML")
    tok_rl, _ = resolver.resolve("color.text.primary", "PRESENTATION", "REPORTLAB")
    tok_pil, _ = resolver.resolve("color.text.primary", "PRESENTATION", "PILLOW")

    assert tok_html.resolved_value == "#0f172a"
    assert tok_rl.resolved_value == (0.0588, 0.0902, 0.1647)
    assert tok_pil.resolved_value == (15, 23, 42)


def test_component_cross_artifact_whitelisting():
    """Verifies that component permissions remain strictly bounded across formats."""
    comp_reg = ComponentRegistry()

    # Worksheet Response Workspace: WORKSHEET only
    assert comp_reg.validate_component_usage("worksheet_response_workspace", "WORKSHEET")[0] is True
    assert comp_reg.validate_component_usage("worksheet_response_workspace", "PRESENTATION")[0] is False
    assert comp_reg.validate_component_usage("worksheet_response_workspace", "HANDOUT")[0] is False
    assert comp_reg.validate_component_usage("worksheet_response_workspace", "SCIENTIFIC_DOCUMENT")[0] is False

    # Presentation Card: PRESENTATION only
    assert comp_reg.validate_component_usage("presentation_card", "PRESENTATION")[0] is True
    assert comp_reg.validate_component_usage("presentation_card", "SCIENTIFIC_DOCUMENT")[0] is False

    # Scientific Evidence Card: SCIENTIFIC_DOCUMENT & HANDOUT only
    assert comp_reg.validate_component_usage("scientific_evidence_card", "SCIENTIFIC_DOCUMENT")[0] is True
    assert comp_reg.validate_component_usage("scientific_evidence_card", "HANDOUT")[0] is True
    assert comp_reg.validate_component_usage("scientific_evidence_card", "PRESENTATION")[0] is False
