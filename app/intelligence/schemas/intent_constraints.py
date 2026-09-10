"""
Universal Knowledge Core — Typed Intent Constraints & Generation Request Schemas.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class EducationLevel(str, Enum):
    PRIMARY = "primary"            # SD
    JUNIOR_HIGH = "junior_high"    # SMP
    SENIOR_HIGH = "senior_high"    # SMA/SMK
    UNDERGRADUATE = "undergraduate"# S1
    POSTGRADUATE = "postgraduate"  # S2/S3
    GENERAL = "general"


class ExpertiseLevel(str, Enum):
    NOVICE = "novice"
    DEVELOPING = "developing"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AudienceProfile(BaseModel):
    education_level: EducationLevel = EducationLevel.SENIOR_HIGH
    expertise_level: ExpertiseLevel = ExpertiseLevel.NOVICE
    language: str = "id"
    age_band: Optional[str] = None


class LengthConstraint(BaseModel):
    target_pages_or_slides: Optional[int] = None
    max_words_per_section: Optional[int] = None


class DepthConstraint(BaseModel):
    detail_level: str = "standard"  # summary, standard, exhaustive
    include_worked_examples: bool = True
    include_math_derivations: bool = False


class CitationConstraint(BaseModel):
    style: str = "indonesian_kti"   # indonesian_kti, apa7, ieee
    require_doi: bool = False


class FormatIntentConstraint(BaseModel):
    allow_two_column: bool = False
    include_answer_key_appendix: bool = True
    custom_accent_color: Optional[str] = None


class IntentConstraints(BaseModel):
    length: LengthConstraint = Field(default_factory=LengthConstraint)
    depth: DepthConstraint = Field(default_factory=DepthConstraint)
    citation: CitationConstraint = Field(default_factory=CitationConstraint)
    format_specific: FormatIntentConstraint = Field(default_factory=FormatIntentConstraint)


class GenerationRequest(BaseModel):
    request_id: str
    raw_source_text: str
    source_filename: str = "input.md"
    target_format_id: str
    audience: AudienceProfile = Field(default_factory=AudienceProfile)
    constraints: IntentConstraints = Field(default_factory=IntentConstraints)


class ResolvedArtifactIntent(BaseModel):
    intent_id: str
    target_format_id: str
    strategy_mode: str
    primary_goal: str
    audience: AudienceProfile
    ordered_intent_functions: List[str] = Field(default_factory=list)
    constraints: IntentConstraints
