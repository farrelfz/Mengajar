"""
Universal Document Intelligence System V5 — Structured Human Decision Model.

Phase 6: Strongly typed models enforcing epistemic separation:
OBSERVATION -> INTERPRETATION -> DECISION -> DIRECTIVE.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.review.contracts.directives import ReviewDirective
from app.review.contracts.enums import (
    EpistemicStatus,
    ExpertDecisionType,
    ReviewConfidence,
)


class ReviewObservation(BaseModel):
    """Empirical statement of what is visually, semantically, or structurally observed."""
    model_config = ConfigDict(frozen=True)

    observation_id: str = Field(default_factory=lambda: f"obs_{uuid.uuid4().hex[:8]}")
    statement: str = Field(min_length=5)
    target_element: Optional[str] = None
    page_or_slide: Optional[int] = None
    epistemic_status: EpistemicStatus = EpistemicStatus.VERIFIED
    referenced_evidence_ids: Tuple[str, ...] = Field(default_factory=tuple)


class ReviewInterpretation(BaseModel):
    """Diagnostic or causal hypothesis explaining why a defect occurred."""
    model_config = ConfigDict(frozen=True)

    interpretation_id: str = Field(default_factory=lambda: f"int_{uuid.uuid4().hex[:8]}")
    hypothesis: str = Field(min_length=5)
    affected_layer: Optional[str] = None  # e.g., LEVEL_R0 to LEVEL_R5
    epistemic_status: EpistemicStatus = EpistemicStatus.LIKELY


class ReviewDecision(BaseModel):
    """Authoritative, structured judgment submitted by an expert reviewer."""
    model_config = ConfigDict(frozen=True)

    decision_id: str = Field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:8]}")
    case_id: str
    reviewer_id: str
    decision_type: ExpertDecisionType
    confidence: ReviewConfidence = ReviewConfidence.HIGH
    epistemic_status: EpistemicStatus = EpistemicStatus.VERIFIED
    rationale: str = Field(min_length=20)
    observations: Tuple[ReviewObservation, ...] = Field(default_factory=tuple)
    interpretations: Tuple[ReviewInterpretation, ...] = Field(default_factory=tuple)
    root_cause_assessment: Optional[str] = None
    directives: Tuple[ReviewDirective, ...] = Field(default_factory=tuple)
    unresolved_uncertainties: Tuple[str, ...] = Field(default_factory=tuple)
    counterfactual_reasoning: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
