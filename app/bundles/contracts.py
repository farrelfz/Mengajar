"""
Multi-Artifact Curriculum Bundle — Contracts.

Defines artifact roles, bundle requests, coverage matrices, and result models.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from app.blueprints.content import AudienceLevel
from app.adaptation.contracts import SharedLearningObjective


class ArtifactRole(str, Enum):
    """Pedagogical function fulfilled by each artifact within a coordinated bundle."""
    PRESENTATION = "presentation"       # Narrative hook, visual anchor, core intuition (16:9)
    HANDOUT = "handout"                 # Comprehensive reference, deep explanation, derivations (A4 Portrait)
    WORKSHEET = "worksheet"             # Active problem-solving, guided & independent practice (A4 Portrait)
    ASSESSMENT = "assessment"           # Formative/summative evidence collection & rubrics (A4 Portrait)
    TEACHER_GUIDE = "teacher_guide"     # Pedagogical orchestration, timing, misconception notes (A4 Landscape)


class ArtifactBundleRequest(BaseModel):
    """Master request specifying concept and desired coordinated artifact bundle."""
    concept: str
    audience: AudienceLevel = AudienceLevel.HIGH_SCHOOL
    duration_minutes: int = 45
    artifacts: list[ArtifactRole] = Field(
        default_factory=lambda: [
            ArtifactRole.PRESENTATION,
            ArtifactRole.HANDOUT,
            ArtifactRole.WORKSHEET,
            ArtifactRole.ASSESSMENT,
        ]
    )
    domain: str = "physics"
    raw_input: str = ""
    source_hint: str = "bundle_request.md"


class BundleItemResult(BaseModel):
    """Result of generating an individual artifact within a bundle."""
    role: ArtifactRole
    format_id: str
    pdf_path: str
    page_count: int
    objectives_covered: list[str] = Field(default_factory=list)
    journey_stages: list[str] = Field(default_factory=list)


class BundleResult(BaseModel):
    """Complete multi-artifact curriculum bundle result."""
    bundle_id: str
    concept: str
    audience: str
    duration_minutes: int
    items: list[BundleItemResult] = Field(default_factory=list)
    shared_objectives: list[SharedLearningObjective] = Field(default_factory=list)
    coverage_matrix: dict[str, dict[str, bool]] = Field(default_factory=dict)
    redundancy_score: float = 0.0
    complementarity_score: float = 1.0
    coherence_valid: bool = True
    trace: dict[str, Any] = Field(default_factory=dict)
