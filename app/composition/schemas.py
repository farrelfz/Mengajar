"""
KIR AI Document Intelligence — Composition Schemas (Batch 4).

Defines the structure for DocumentComposition, PageComposition, and Regions.
These models represent the absolute layout semantics without any HTML/CSS coordinates.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.intelligence.schemas import DocumentMode
from app.design.schemas import TypographyScale, ColorRole, ComponentFamily


class RegionRole(str, Enum):
    """Semantic region within a page composition."""
    HEADER = "header"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUPPORTING = "supporting"
    VISUAL = "visual"
    SEQUENCE = "sequence"
    FOOTER = "footer"


class CompositionWarningCode(str, Enum):
    PAGE_OVERFLOW_RISK = "PAGE_OVERFLOW_RISK"
    UNSAFE_CONTENT_SPLIT = "UNSAFE_CONTENT_SPLIT"
    EXCESSIVE_PAGE_DENSITY = "EXCESSIVE_PAGE_DENSITY"
    ORPHANED_CONTENT = "ORPHANED_CONTENT"
    REPETITIVE_COMPOSITION = "REPETITIVE_COMPOSITION"
    WEAK_PAGE_FOCUS = "WEAK_PAGE_FOCUS"
    UNBALANCED_REGION_USAGE = "UNBALANCED_REGION_USAGE"
    SEMANTIC_SEQUENCE_BREAK = "SEMANTIC_SEQUENCE_BREAK"
    UNSUPPORTED_COMPOSITION = "UNSUPPORTED_COMPOSITION"
    CONTINUATION_REQUIRED = "CONTINUATION_REQUIRED"
    TRANSITION_RECOMMENDED = "TRANSITION_RECOMMENDED"
    MISSING_SOURCE_CONTENT = "MISSING_SOURCE_CONTENT"
    DUPLICATED_SOURCE_CONTENT = "DUPLICATED_SOURCE_CONTENT"


class CompositionWarning(BaseModel):
    code: CompositionWarningCode
    severity: str  # "warning", "error", "info"
    page_number: int | None = None
    source_unit_ids: list[str] = Field(default_factory=list)
    reason: str
    recommended_action: str | None = None


class ContentBlock(BaseModel):
    """Maps a collection of source units to a component family within a region."""
    block_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    component_family: ComponentFamily
    source_unit_ids: list[str]
    typography: TypographyScale | None = None
    color_role: ColorRole | None = None
    sequence_index: int | None = None
    rendered_html: str | None = None
    raw_content: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PageRegion(BaseModel):
    """An abstract area on a page populated with content blocks."""
    role: RegionRole
    blocks: list[ContentBlock] = Field(default_factory=list)


class ContinuationMetadata(BaseModel):
    """Metadata to maintain context across split pages."""
    source_group_id: str
    sequence_position: int
    continuation_index: int
    previous_page_id: str | None = None
    next_page_id: str | None = None


class PageComposition(BaseModel):
    """A concrete page with defined semantic regions."""
    page_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    page_number: int
    page_type: str
    composition_type: str
    hierarchy_level: int = 1
    regions: dict[RegionRole, PageRegion] = Field(default_factory=dict)
    source_unit_ids: list[str] = Field(default_factory=list)
    continuation: ContinuationMetadata | None = None
    density_estimate: float = 0.5
    warnings: list[CompositionWarning] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CompositionQualityReport(BaseModel):
    score: float = 1.0
    dimension_scores: dict[str, float] = Field(default_factory=dict)
    warnings: list[CompositionWarning] = Field(default_factory=list)
    critical_issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class DocumentComposition(BaseModel):
    """The final abstract document structure, ready for HTML/PDF realization."""
    composition_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: dict[str, Any] = Field(default_factory=dict)
    mode: DocumentMode
    format_id: str | None = None  # Canonical physical format ID (e.g. "a4_portrait", "presentation_16_9")
    theme_reference: str
    source_blueprint_id: str
    pages: list[PageComposition] = Field(default_factory=list)
    warnings: list[CompositionWarning] = Field(default_factory=list)
    composition_summary: CompositionQualityReport | None = None
