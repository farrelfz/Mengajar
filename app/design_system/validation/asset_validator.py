"""
Universal Design System — Asset & Component Validator.

Phase 3B.0: Enforces font existence (INV-DESIGN-004), critical asset resolution
(INV-DESIGN-005), and component-artifact compatibility (INV-DESIGN-010).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.design_system.registry.font_registry import FontRegistry
from app.design_system.registry.asset_registry import AssetRegistry
from app.design_system.registry.component_registry import ComponentRegistry


class AssetValidationFinding:
    """Design-level finding for asset or component issues."""
    def __init__(
        self,
        target_id: str,
        violation_type: str,  # "FONT_MISSING", "CRITICAL_ASSET_MISSING", "COMPONENT_INCOMPATIBLE"
        artifact_type: str,
        is_critical: bool,
        message: str,
    ) -> None:
        self.target_id = target_id
        self.violation_type = violation_type
        self.artifact_type = artifact_type
        self.is_critical = is_critical
        self.message = message


class AssetAndComponentValidator:
    """Validates assets, fonts, and component usage."""

    def __init__(
        self,
        font_registry: Optional[FontRegistry] = None,
        asset_registry: Optional[AssetRegistry] = None,
        component_registry: Optional[ComponentRegistry] = None,
    ) -> None:
        self.font_registry = font_registry or FontRegistry()
        self.asset_registry = asset_registry or AssetRegistry()
        self.component_registry = component_registry or ComponentRegistry()

    def validate_font(
        self, family: str, weight: int, style: str, artifact_type: str
    ) -> Optional[AssetValidationFinding]:
        """Validates that a font family exists in the FontRegistry."""
        face = self.font_registry.get_face(family, weight, style)
        if not face:
            # Fallback was needed
            return AssetValidationFinding(
                target_id=f"{family}:{weight}:{style}",
                violation_type="FONT_ASSET_UNREGISTERED",
                artifact_type=artifact_type,
                is_critical=False,
                message=f"Font '{family}' (weight {weight}, style {style}) not registered; fallback will be required.",
            )
        return None

    def validate_asset_usage(
        self, asset_id: str, artifact_type: str
    ) -> Optional[AssetValidationFinding]:
        """Validates asset existence, criticality, and artifact compatibility."""
        spec, fallback_applied, err = self.asset_registry.resolve_asset(asset_id, artifact_type)
        if err and not fallback_applied:
            # Fatal: asset forbidden or completely unavailable
            return AssetValidationFinding(
                target_id=asset_id,
                violation_type="CRITICAL_ASSET_MISSING",
                artifact_type=artifact_type,
                is_critical=True,
                message=err,
            )
        elif fallback_applied:
            return AssetValidationFinding(
                target_id=asset_id,
                violation_type="ASSET_FALLBACK_APPLIED",
                artifact_type=artifact_type,
                is_critical=False,
                message=err or f"Asset '{asset_id}' required fallback.",
            )
        return None

    def validate_component_usage(
        self, component_id: str, artifact_type: str
    ) -> Optional[AssetValidationFinding]:
        """Enforces INV-DESIGN-010 component whitelist per artifact."""
        is_valid, err = self.component_registry.validate_component_usage(component_id, artifact_type)
        if not is_valid:
            return AssetValidationFinding(
                target_id=component_id,
                violation_type="COMPONENT_ARTIFACT_INCOMPATIBLE",
                artifact_type=artifact_type,
                is_critical=True,
                message=err or f"Component '{component_id}' incompatible with '{artifact_type}'.",
            )
        return None
