"""
Universal Document Intelligence System V5 — Blueprint Validation Contracts.

Phase 4.1: Machine-readable contracts for blueprint structural validation.
Operates UPSTREAM of rendering — diagnostic signals only, NOT export authority.
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class BlueprintFailureType(str, Enum):
    """Taxonomy of blueprint structural failure modes."""
    BLUEPRINT_INCOMPLETE = "BLUEPRINT_INCOMPLETE"
    ARTIFACT_COLLAPSE_RISK = "ARTIFACT_COLLAPSE_RISK"
    PRESENTATION_HANDOUT_COLLAPSE = "PRESENTATION_HANDOUT_COLLAPSE"
    HANDOUT_SLIDE_FRAGMENTATION = "HANDOUT_SLIDE_FRAGMENTATION"
    WORKSHEET_QUIZ_COLLAPSE = "WORKSHEET_QUIZ_COLLAPSE"
    WORKSHEET_ANSWER_LEAK = "WORKSHEET_ANSWER_LEAK"
    SCIENTIFIC_ARGUMENT_WEAKNESS = "SCIENTIFIC_ARGUMENT_WEAKNESS"
    UNSUPPORTED_SCIENTIFIC_CLAIM = "UNSUPPORTED_SCIENTIFIC_CLAIM"
    MISSING_TRACEABILITY = "MISSING_TRACEABILITY"
    UNCERTAINTY_POLICY_VIOLATION = "UNCERTAINTY_POLICY_VIOLATION"
    NARRATIVE_DISCONTINUITY = "NARRATIVE_DISCONTINUITY"
    INQUIRY_ARC_BROKEN = "INQUIRY_ARC_BROKEN"
    SEMANTIC_FIELD_CONTRADICTION = "SEMANTIC_FIELD_CONTRADICTION"


class BlueprintValidationReport(BaseModel):
    """
    Structural diagnostic report for a generated Markdown blueprint.

    This is a SIGNAL layer only. It does NOT approve or deny production export.
    That authority belongs exclusively to UnifiedQualityAuthority.
    """
    model_config = ConfigDict(frozen=True)

    report_id: str = Field(default_factory=lambda: f"bvr_{uuid.uuid4().hex[:8]}")
    artifact_type: str
    is_valid: bool
    completeness_score: float = Field(ge=0.0, le=1.0)
    artifact_specificity_score: float = Field(ge=0.0, le=1.0)
    semantic_coherence_score: float = Field(ge=0.0, le=1.0)
    traceability_score: float = Field(ge=0.0, le=1.0)
    anti_pattern_findings: List[str] = Field(default_factory=list)
    hard_invariant_violations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    missing_required_fields: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)
