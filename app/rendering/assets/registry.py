"""
KIR AI Document Intelligence — Asset Registry.
"""
from typing import Optional
from app.rendering.schemas import AssetMetadata

class AssetRegistry:
    def __init__(self):
        self._assets: dict[str, AssetMetadata] = {}

    def register(self, asset: AssetMetadata) -> None:
        self._assets[asset.asset_id] = asset

    def get_asset(self, asset_id: str) -> Optional[AssetMetadata]:
        return self._assets.get(asset_id)

    def get_all(self) -> list[AssetMetadata]:
        return list(self._assets.values())
        
    def has_asset(self, asset_id: str) -> bool:
        return asset_id in self._assets
