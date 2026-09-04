"""
KIR AI Document Intelligence — Artifact Format Contracts.

Authoritative Single Source of Truth for physical output formats, geometry,
orientation, and rendering constraints.
"""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field
from app.intelligence.schemas import DocumentMode


class ArtifactFormat(BaseModel):
    """Authoritative representation of a physical document canvas/page format."""
    id: str
    display_name: str
    width_mm: float
    height_mm: float
    orientation: Literal["portrait", "landscape", "square", "custom"]
    category: Literal["document", "presentation", "poster", "custom"] = "document"
    paginated: bool = True
    
    # CSS & Styling
    css_page_size: str
    page_class: str
    
    # Playwright PDF export parameters
    playwright_format: str | None = None
    playwright_landscape: bool = False
    playwright_width: str | None = None
    playwright_height: str | None = None
    
    # Backward compatibility mode mapping
    legacy_document_mode: DocumentMode = DocumentMode.A4_PORTRAIT

    @property
    def width_pt(self) -> float:
        """Width in PDF typographic points (72 pt = 1 inch = 25.4 mm)."""
        return self.width_mm * 72.0 / 25.4

    @property
    def height_pt(self) -> float:
        """Height in PDF typographic points."""
        return self.height_mm * 72.0 / 25.4

    @property
    def aspect_ratio(self) -> float:
        """Width divided by height."""
        return self.width_mm / self.height_mm if self.height_mm > 0 else 1.0

    def to_css_page_rule(self) -> str:
        """Produce the canonical CSS @page rule for this format."""
        return f"@page {{ size: {self.css_page_size}; margin: 0; }}"

    def matches_dimensions(self, width_pt: float, height_pt: float, tolerance_pt: float = 3.0) -> bool:
        """Verify if given dimensions in points match this format within tolerance."""
        return (
            abs(self.width_pt - width_pt) <= tolerance_pt
            and abs(self.height_pt - height_pt) <= tolerance_pt
        )
