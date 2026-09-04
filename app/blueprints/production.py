"""
KIR AI Document Intelligence — Production Blueprint (Level C).

Answers: WHAT REUSABLE PRODUCTION CAPABILITIES are required?
Defines semantic visual intents and required capability contracts without layout coordinates.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class TargetArtifactType(str, Enum):
    TEACHING_PRESENTATION = "teaching_presentation"
    RESEARCH_PRESENTATION = "research_presentation"
    DETAILED_HANDOUT = "detailed_handout"
    STUDENT_WORKSHEET = "student_worksheet"
    SCIENTIFIC_POSTER = "scientific_poster"
    ONE_PAGE_SUMMARY = "one_page_summary"
    KTI_DOCUMENT = "kti_document"


class SemanticIntentSpec(BaseModel):
    """Specification of what visual/structural effect is needed semantically."""
    intent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    semantic_intent: str  # e.g., "rotational_force_system", "misconception_card", "step_by_step_derivation"
    domain: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    preferred_format: str | None = None  # e.g., "svg", "html", "chart"


class ProductionRequirement(BaseModel):
    """Links a pedagogical step to required registered capabilities and intents."""
    step_id: str
    semantic_type: str
    required_capability_id: str | None = None  # Optional explicit capability ID
    semantic_intent: SemanticIntentSpec | None = None
    fallback_capability_ids: list[str] = Field(default_factory=list)
    is_mandatory: bool = True
    density_hint: str = "standard"  # compact, standard, expansive
    presentation_hint: str | None = None  # full_slide, hero_focus, split_column, card


class ProductionBlueprint(BaseModel):
    """Level C Production Blueprint: Mapping from narrative to capability requests."""
    blueprint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_artifact: TargetArtifactType = TargetArtifactType.TEACHING_PRESENTATION
    target_format: str | None = None  # Explicit physical format override (e.g. "a4_portrait", "a4_landscape", "presentation_16_9")
    requirements: list[ProductionRequirement] = Field(default_factory=list)
    global_constraints: dict[str, Any] = Field(default_factory=dict)
