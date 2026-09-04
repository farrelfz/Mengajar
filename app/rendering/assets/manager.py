"""
KIR AI Document Intelligence — Asset Manager.
"""
import hashlib
from pathlib import Path
from app.rendering.assets.registry import AssetRegistry

class AssetManager:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.registry = AssetRegistry()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_asset_path(self, asset_id: str, format_ext: str) -> Path:
        return self.output_dir / f"{asset_id}.{format_ext}"
        
    def compute_checksum(self, file_path: Path) -> str:
        if not file_path.exists():
            return ""
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
