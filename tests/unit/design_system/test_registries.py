"""Unit tests for AssetRegistry, ComponentRegistry, and ProfileRegistry."""

import pytest
from app.design_system.registry.asset_registry import AssetRegistry
from app.design_system.registry.component_registry import ComponentRegistry
from app.design_system.registry.profile_registry import ProfileRegistry
from app.design_system.contracts.assets import AssetSpec, AssetType, AssetFormat
from app.design_system.contracts.components import ComponentCategory
from app.design_system.profiles import get_standard_profile_registry


def test_asset_registry_resolution_and_fallback():
    """Verifies asset resolution, artifact constraints, and placeholder fallback."""
    reg = AssetRegistry()

    # Existing asset valid for Worksheet
    spec, fallback, err = reg.resolve_asset("icon_inquiry", "WORKSHEET")
    assert spec is not None
    assert fallback is False
    assert err is None

    # Asset forbidden for Presentation
    spec_pres, fallback_pres, err_pres = reg.resolve_asset("icon_inquiry", "PRESENTATION")
    assert spec_pres is None
    assert "is forbidden for artifact type 'PRESENTATION'" in err_pres

    # Missing asset uses placeholder
    missing_spec, missing_fallback, _ = reg.resolve_asset("unknown_diagram_123", "HANDOUT")
    assert missing_spec is not None
    assert missing_fallback is True
    assert missing_spec.asset_id == "placeholder_diagram"


def test_component_registry_artifact_compatibility_enforcement():
    """Verifies INV-DESIGN-010: component whitelist per artifact type."""
    reg = ComponentRegistry()

    # Response workspace allowed on Worksheet
    valid_ws, err_ws = reg.validate_component_usage("worksheet_response_workspace", "WORKSHEET")
    assert valid_ws is True
    assert err_ws is None

    # Response workspace forbidden on Presentation!
    valid_pres, err_pres = reg.validate_component_usage("worksheet_response_workspace", "PRESENTATION")
    assert valid_pres is False
    assert "is not allowed in artifact type 'PRESENTATION'" in err_pres

    # Evidence card allowed on Scientific Document
    valid_sci, _ = reg.validate_component_usage("scientific_evidence_card", "SCIENTIFIC_DOCUMENT")
    assert valid_sci is True


def test_profile_registry_all_four_formats():
    """Verifies that ProfileRegistry contains all four formats."""
    reg = get_standard_profile_registry()
    formats = ["PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"]

    for fmt in formats:
        prof = reg.get_profile_for_artifact(fmt)
        assert prof is not None
        assert prof.artifact_type == fmt
        assert prof.canvas_spec.printable_area_pt > 0
