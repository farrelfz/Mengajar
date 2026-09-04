"""
KIR AI Document Intelligence — Page Type Registry Schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.intelligence.schemas import ContentDensity, DocumentMode, BlueprintCandidateType


class PageType(BaseModel):
    """Abstract definition of a page type."""

    name: str
    purpose: str
    supported_candidates: list[BlueprintCandidateType] = Field(default_factory=list)
    preferred_hierarchy: list[int] = Field(default_factory=list)
    supported_density: list[ContentDensity] = Field(default_factory=list)
    supported_modes: list[DocumentMode] = Field(default_factory=list)
    preferred_grids: list[str] = Field(default_factory=list)
    fallback_page_type: str | None = None
