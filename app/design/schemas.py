"""
KIR AI Document Intelligence — Design Domain Schemas.

Defines schemas for the design layer: tokens, hierarchy, constraints,
and the final VisualBlueprint.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.intelligence.schemas import DocumentMode, KtiBab


# ══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ══════════════════════════════════════════════════════════════════════════════


class ColorRole(str, Enum):
    BACKGROUND = "background"
    SURFACE = "surface"
    SURFACE_SUBTLE = "surface_subtle"
    SURFACE_EMPHASIS = "surface_emphasis"
    TEXT_PRIMARY = "text_primary"
    TEXT_SECONDARY = "text_secondary"
    TEXT_MUTED = "text_muted"
    BORDER_SUBTLE = "border_subtle"
    BORDER_STRONG = "border_strong"
    ACCENT_PRIMARY = "accent_primary"
    ACCENT_SECONDARY = "accent_secondary"
    ACCENT_SOFT = "accent_soft"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    DATA_1 = "data_1"
    DATA_2 = "data_2"
    DATA_3 = "data_3"
    DATA_4 = "data_4"
    DATA_5 = "data_5"


class TypographyScale(str, Enum):
    DISPLAY = "display"
    HERO = "hero"
    HEADLINE = "headline"
    TITLE = "title"
    SECTION = "section"
    SUBSECTION = "subsection"
    BODY_LARGE = "body_large"
    BODY = "body"
    BODY_SMALL = "body_small"
    SUPPORTING = "supporting"
    CAPTION = "caption"
    LABEL = "label"
    MICRO = "micro"


class SpacingScale(str, Enum):
    NONE = "none"
    XXS = "xxs"
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "2xl"
    XXXL = "3xl"
    XXXXL = "4xl"


class RadiusScale(str, Enum):
    NONE = "none"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    FULL = "full"


class BorderScale(str, Enum):
    NONE = "none"
    SUBTLE = "subtle"
    STANDARD = "standard"
    STRONG = "strong"


class ElevationScale(str, Enum):
    FLAT = "flat"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class VisualHierarchyLevel(int, Enum):
    LEVEL_1 = 1  # Primary message
    LEVEL_2 = 2  # Supporting idea
    LEVEL_3 = 3  # Explanation
    LEVEL_4 = 4  # Metadata/Citation


class CompositionPattern(str, Enum):
    SEQUENTIAL = "sequential"
    COMPARISON = "comparison"
    DATA_DOMINANT = "data_dominant"
    LAYERED = "layered"
    DIRECTIONAL = "directional"
    DISTILLED = "distilled"
    CONCEPT_FOCUSED = "concept_focused"
    EMPHASIS = "emphasis"
    CLOSURE = "closure"
    CONSTRAINT = "constraint"
    ACTION = "action"
    FORWARD_LOOKING = "forward_looking"
    EXPLANATORY = "explanatory"
    SYNTHESIS = "synthesis"
    GRID = "grid"
    SINGLE_FOCUS = "single_focus"


class DesignWarningCode(str, Enum):
    OVERFLOW_RISK = "OVERFLOW_RISK"
    LOW_CONTRAST_RISK = "LOW_CONTRAST_RISK"
    EXCESSIVE_DENSITY = "EXCESSIVE_DENSITY"
    WEAK_HIERARCHY = "WEAK_HIERARCHY"
    VISUAL_MONOTONY = "VISUAL_MONOTONY"
    UNBALANCED_COMPOSITION = "UNBALANCED_COMPOSITION"
    UNSUPPORTED_PAGE_TYPE = "UNSUPPORTED_PAGE_TYPE"
    MISSING_PRIMARY_FOCUS = "MISSING_PRIMARY_FOCUS"
    CONTENT_SPLIT_REQUIRED = "CONTENT_SPLIT_REQUIRED"


class BalanceStatus(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class VisualWeight(str, Enum):
    LIGHT = "light"
    NORMAL = "normal"
    STRONG = "strong"
    DOMINANT = "dominant"


class ComponentFamily(str, Enum):
    TITLE_BLOCK = "title_block"
    SECTION_LABEL = "section_label"
    TEXT_BLOCK = "text_block"
    KEY_STATEMENT = "key_statement"
    KEY_NUMBER = "key_number"
    INSIGHT_BLOCK = "insight_block"
    CALLOUT = "callout"
    WARNING_BLOCK = "warning_block"
    COMPARISON_BLOCK = "comparison_block"
    STEP_BLOCK = "step_block"
    TIMELINE_ITEM = "timeline_item"
    DATA_BLOCK = "data_block"
    REFERENCE_BLOCK = "reference_block"
    IMAGE_PLACEHOLDER = "image_placeholder"
    DIAGRAM_PLACEHOLDER = "diagram_placeholder"
    QUOTE_BLOCK = "quote_block"
    SUMMARY_BLOCK = "summary_block"


# ══════════════════════════════════════════════════════════════════════════════
# DOMAIN MODELS
# ══════════════════════════════════════════════════════════════════════════════


class DesignToken(BaseModel):
    """Abstract representation of a design token."""

    name: str
    value: str
    description: str | None = None


class Theme(BaseModel):
    """Semantic Theme configuration."""

    name: str
    colors: dict[ColorRole, str]
    typography_fonts: dict[str, str]
    is_dark_mode: bool = False


class DesignWarning(BaseModel):
    """Warning produced during design evaluation."""

    code: DesignWarningCode
    severity: str  # "warning" or "error"
    reason: str
    affected_unit_ids: list[str] = Field(default_factory=list)
    suggested_strategy: str | None = None


class BalanceReport(BaseModel):
    """Report produced by the Balance Evaluator."""

    status: BalanceStatus = BalanceStatus.PASS
    warnings: list[DesignWarning] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    suggested_strategies: list[str] = Field(default_factory=list)


class ComponentAssignment(BaseModel):
    """Maps a component family to its source data and styling constraints."""

    component_family: ComponentFamily
    source_unit_ids: list[str] = Field(default_factory=list)
    typography: TypographyScale | None = None
    color_role: ColorRole | None = None
    visual_weight: VisualWeight = VisualWeight.NORMAL
    spacing_bottom: SpacingScale | None = None


class PageComposition(BaseModel):
    """A single page composed of semantic content mapped to visual components."""

    page_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    page_type: str
    composition_pattern: CompositionPattern
    source_group_id: str | None = None
    source_unit_ids: list[str] = Field(default_factory=list)
    components: list[ComponentAssignment] = Field(default_factory=list)
    grid_specification: str | None = None
    balance_report: BalanceReport | None = None
    notes: str | None = None


class VisualBlueprint(BaseModel):
    """The final output of the Design Layer.

    Contains no HTML/CSS, only abstract visual composition assignments.
    """

    blueprint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_proposal_id: str
    document_mode: DocumentMode
    theme_name: str
    pages: list[PageComposition] = Field(default_factory=list)
    global_warnings: list[DesignWarning] = Field(default_factory=list)
    color_tokens: dict[str, str] = Field(default_factory=dict)
