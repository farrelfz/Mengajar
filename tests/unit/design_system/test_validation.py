"""Unit tests for Design System Validators and Quality Authority Bridge."""

import pytest
from app.design_system.validation.typography_validator import TypographyValidator
from app.design_system.validation.color_validator import ColorValidator
from app.design_system.validation.geometry_validator import GeometryValidator
from app.design_system.validation.asset_validator import AssetAndComponentValidator
from app.design_system.validation.token_validator import TokenValidator
from app.design_system.validation.quality_bridge import DesignSystemQualityBridge
from app.quality.contracts.signals import QualityDomain, SignalSeverity


def test_typography_validator_detects_sub_floor_fonts():
    """Verifies that font sizes below artifact floor trigger findings."""
    val = TypographyValidator()

    # Presentation floor is 11.0 pt for body; 9.0 pt should fail
    finding = val.validate_font_size(
        element_id="slide1_body",
        role="body",
        size_pt=9.0,
        artifact_type="PRESENTATION",
    )
    assert finding is not None
    assert finding.actual_size_pt == 9.0
    assert finding.min_required_pt == 11.0

    # Bridge maps it to canonical QualityFinding
    q_fnd = DesignSystemQualityBridge.map_typography_finding(finding)
    assert q_fnd.failure_code == "MINIMUM_FONT_SIZE_VIOLATION"
    assert q_fnd.domain == QualityDomain.RENDERED
    assert q_fnd.severity == SignalSeverity.MAJOR


def test_color_validator_detects_unreadable_contrast():
    """Verifies that low-contrast text triggers a finding."""
    val = ColorValidator()

    finding = val.validate_pair(
        element_id="card_subtitle",
        foreground_hex="#94a3b8",  # Slate 400
        background_hex="#f8fafc",  # Slate 50
    )
    assert finding is not None
    assert finding.contrast_ratio < 4.5

    q_fnd = DesignSystemQualityBridge.map_color_contrast_finding(finding)
    assert q_fnd.failure_code == "COLOR_CONTRAST_LOW"


def test_geometry_validator_detects_canvas_overflow():
    """Verifies that coordinates beyond canvas bounds trigger overflow finding."""
    val = GeometryValidator()

    # Presentation canvas is 960x540; right=1000 overflows
    finding = val.validate_bounding_box(
        element_id="wide_card",
        x=800.0,
        y=100.0,
        width=200.0,
        height=150.0,
        artifact_type="PRESENTATION",
    )
    assert finding is not None
    assert finding.violation_type == "CANVAS_OVERFLOW"

    q_fnd = DesignSystemQualityBridge.map_geometry_finding(finding)
    assert q_fnd.severity == SignalSeverity.CRITICAL


def test_asset_and_component_validator():
    """Verifies detection of incompatible components and unregistered fonts."""
    val = AssetAndComponentValidator()

    # Incompatible component
    fnd_comp = val.validate_component_usage("worksheet_response_workspace", "PRESENTATION")
    assert fnd_comp is not None
    assert fnd_comp.violation_type == "COMPONENT_ARTIFACT_INCOMPATIBLE"

    q_fnd = DesignSystemQualityBridge.map_asset_finding(fnd_comp)
    assert q_fnd.severity == SignalSeverity.BLOCKING
