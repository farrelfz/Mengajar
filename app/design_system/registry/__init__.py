"""Universal Design System Registries Export."""

from app.design_system.registry.token_registry import TokenRegistry
from app.design_system.registry.font_registry import FontRegistry
from app.design_system.registry.asset_registry import AssetRegistry
from app.design_system.registry.component_registry import ComponentRegistry
from app.design_system.registry.profile_registry import ProfileRegistry

__all__ = [
    "TokenRegistry",
    "FontRegistry",
    "AssetRegistry",
    "ComponentRegistry",
    "ProfileRegistry",
]
