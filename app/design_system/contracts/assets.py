"""
Universal Design System — Asset Contracts.

Phase 3B.0: Typed specifications for document visual assets, icons, diagrams,
and figures with cross-artifact compatibility, criticality flags, and fallbacks.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field


class AssetType(str, Enum):
    """Canonical visual asset classifications."""
    ICON = "ICON"
    DIAGRAM = "DIAGRAM"
    ILLUSTRATION = "ILLUSTRATION"
    IMAGE = "IMAGE"
    FORMULA = "FORMULA"
    LOGO = "LOGO"
    SIGNATURE_BLOCK = "SIGNATURE_BLOCK"
    CHART = "CHART"


class AssetFormat(str, Enum):
    """Supported asset physical file formats."""
    SVG = "SVG"
    PNG = "PNG"
    WEBP = "WEBP"
    JPEG = "JPEG"
    PDF = "PDF"


class AssetSpec(BaseModel):
    """Specification of an asset asset entry in the design system."""
    model_config = ConfigDict(frozen=True)

    asset_id: str
    asset_type: AssetType
    file_path: str
    format: AssetFormat
    width_pt: float
    height_pt: float
    allowed_artifacts: Tuple[str, ...] = (
        "PRESENTATION",
        "HANDOUT",
        "WORKSHEET",
        "SCIENTIFIC_DOCUMENT",
    )
    is_critical: bool = False
    fallback_asset_id: Optional[str] = None
    license: str = "proprietary/internal"
    alt_text: str = ""
    caption_template: Optional[str] = None

    def is_allowed_for(self, artifact_type: str) -> bool:
        """Checks if the asset is permitted for use in the specified artifact type."""
        return artifact_type.upper() in [a.upper() for a in self.allowed_artifacts]

    @property
    def aspect_ratio(self) -> float:
        """Returns width / height aspect ratio."""
        if self.height_pt <= 0:
            return 1.0
        return round(self.width_pt / self.height_pt, 4)
