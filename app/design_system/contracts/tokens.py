"""
Universal Design System — Canonical Token Contracts.

Phase 3B.0: Hierarchical 4-tier token model:
Level 1: RawToken (physical primitives, hex, px, pt)
Level 2: SemanticToken (functional roles: text.primary, space.section)
Level 3: ArtifactToken (format-specific overrides: presentation.title, handout.body)
Level 4: RenderToken (renderer-bound: CSS variable, ReportLab Color/points)
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field


class TokenLevel(str, Enum):
    """The four canonical token derivation levels."""
    RAW = "RAW"
    SEMANTIC = "SEMANTIC"
    ARTIFACT = "ARTIFACT"
    RENDER = "RENDER"


class RawToken(BaseModel):
    """Level 1: Unopinionated physical constant."""
    model_config = ConfigDict(frozen=True)

    name: str
    value: Any
    category: str  # "color", "size", "font", "space", "radius"


class SemanticToken(BaseModel):
    """Level 2: Abstract functional role referencing a raw token."""
    model_config = ConfigDict(frozen=True)

    name: str
    raw_token_ref: str
    role: str
    description: str = ""


class ArtifactToken(BaseModel):
    """Level 3: Artifact-specific token binding or override."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str  # "PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"
    name: str
    semantic_token_ref: str
    override_value: Optional[Any] = None
    rationale: str = ""


class RenderToken(BaseModel):
    """Level 4: Renderer-executable value with degradation tracking."""
    model_config = ConfigDict(frozen=True)

    renderer: str  # "HTML", "CSS", "REPORTLAB", "PYMUPDF", "PILLOW"
    token_name: str
    resolved_value: Any
    unit: Optional[str] = None
    fallback_applied: bool = False
    degradation_note: Optional[str] = None


class DesignResolutionTrace(BaseModel):
    """Audit trail tracking complete token derivation path."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    renderer: str
    requested_token: str
    semantic_token: Optional[str] = None
    artifact_token: Optional[str] = None
    raw_token: Optional[str] = None
    resolved_value: Any
    fallback_applied: bool = False
    degradation_recorded: bool = False
