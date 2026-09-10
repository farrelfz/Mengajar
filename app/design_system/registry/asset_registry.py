"""
Universal Design System — Asset Registry.

Phase 3B.0: Deterministic asset resolution, artifact compatibility checks,
and fallback handling for missing/placeholder assets (INV-DESIGN-005).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from app.design_system.contracts.assets import (
    AssetSpec,
    AssetType,
    AssetFormat,
)


class AssetRegistry:
    """Central repository for static, generated, and placeholder assets."""

    def __init__(self) -> None:
        self._assets: Dict[str, AssetSpec] = {}
        self._initialize_standard_assets()

    def _initialize_standard_assets(self) -> None:
        """Pre-registers standard fallback and system icon/diagram assets."""
        standard_assets = [
            # Placeholders
            AssetSpec(
                asset_id="placeholder_diagram",
                asset_type=AssetType.DIAGRAM,
                file_path="assets/diagrams/placeholder.svg",
                format=AssetFormat.SVG,
                width_pt=240.0,
                height_pt=160.0,
                allowed_artifacts=("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"),
                is_critical=False,
                alt_text="Diagram Placeholder",
            ),
            AssetSpec(
                asset_id="placeholder_image",
                asset_type=AssetType.IMAGE,
                file_path="assets/images/placeholder.png",
                format=AssetFormat.PNG,
                width_pt=200.0,
                height_pt=150.0,
                allowed_artifacts=("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"),
                is_critical=False,
                alt_text="Image Placeholder",
            ),

            # Standard Icons
            AssetSpec(
                asset_id="icon_info",
                asset_type=AssetType.ICON,
                file_path="assets/icons/info.svg",
                format=AssetFormat.SVG,
                width_pt=16.0,
                height_pt=16.0,
                allowed_artifacts=("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"),
                is_critical=False,
                alt_text="Information",
            ),
            AssetSpec(
                asset_id="icon_warning",
                asset_type=AssetType.ICON,
                file_path="assets/icons/warning.svg",
                format=AssetFormat.SVG,
                width_pt=16.0,
                height_pt=16.0,
                allowed_artifacts=("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"),
                is_critical=False,
                alt_text="Warning",
            ),
            AssetSpec(
                asset_id="icon_inquiry",
                asset_type=AssetType.ICON,
                file_path="assets/icons/inquiry.svg",
                format=AssetFormat.SVG,
                width_pt=18.0,
                height_pt=18.0,
                allowed_artifacts=("WORKSHEET", "HANDOUT"),
                is_critical=False,
                alt_text="Inquiry Activity",
            ),
            AssetSpec(
                asset_id="icon_evidence",
                asset_type=AssetType.ICON,
                file_path="assets/icons/evidence.svg",
                format=AssetFormat.SVG,
                width_pt=16.0,
                height_pt=16.0,
                allowed_artifacts=("SCIENTIFIC_DOCUMENT", "HANDOUT"),
                is_critical=False,
                alt_text="Scientific Evidence",
            ),
        ]

        for asset in standard_assets:
            self.register_asset(asset)

    def register_asset(self, asset: AssetSpec) -> None:
        """Registers an asset specification."""
        self._assets[asset.asset_id] = asset

    def get_asset(self, asset_id: str) -> Optional[AssetSpec]:
        """Retrieves asset spec by ID."""
        return self._assets.get(asset_id)

    def resolve_asset(
        self, asset_id: str, artifact_type: str
    ) -> Tuple[Optional[AssetSpec], bool, Optional[str]]:
        """
        Deterministically resolves an asset for an artifact.
        Checks:
        1. Asset existence
        2. Artifact whitelist compatibility (INV-DESIGN-010)
        3. Fallback resolution if primary asset is missing or disallowed
        Returns (resolved_spec, fallback_applied, error_message).
        """
        asset = self.get_asset(asset_id)

        # Asset does not exist
        if not asset:
            fallback = self.get_asset("placeholder_diagram")
            return fallback, True, f"Asset '{asset_id}' not found in registry; used placeholder fallback."

        # Check artifact compatibility
        if not asset.is_allowed_for(artifact_type):
            if asset.fallback_asset_id:
                fallback = self.get_asset(asset.fallback_asset_id)
                if fallback and fallback.is_allowed_for(artifact_type):
                    return fallback, True, (
                        f"Asset '{asset_id}' not allowed for {artifact_type}; "
                        f"used fallback '{asset.fallback_asset_id}'."
                    )
            return None, False, f"Asset '{asset_id}' is forbidden for artifact type '{artifact_type}'."

        return asset, False, None

    def list_assets(self) -> List[AssetSpec]:
        """Returns all registered assets."""
        return list(self._assets.values())
