"""
Universal Document Intelligence System V5 — Canonical Review Case Contract.

Phase 6: Immutable case representation anchoring all review lifecycles,
evidence, priority scoring, reviewer assignments, and decisions.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.review.contracts.directives import ReviewDirective
from app.review.contracts.enums import (
    ReviewState,
    ReviewTrigger,
    ReviewabilityStatus,
    ReviewerCapability,
)
from app.review.contracts.review_decision import ReviewDecision


class CaseIdentity(BaseModel):
    """Cryptographically anchored identity of an artifact under review."""
    model_config = ConfigDict(frozen=True)

    case_id: str = Field(default_factory=lambda: f"rc_{uuid.uuid4().hex[:8]}")
    artifact_id: str
    job_id: str
    artifact_type: str
    artifact_digest: str  # SHA-256


class ReviewCase(BaseModel):
    """Complete, self-contained review case managed within the review studio."""
    model_config = ConfigDict(frozen=True)

    case_id: str = Field(default_factory=lambda: f"rc_{uuid.uuid4().hex[:8]}")
    artifact_id: str
    job_id: str = ""
    artifact_type: str
    artifact_digest: str
    trigger: ReviewTrigger
    current_state: ReviewState = ReviewState.OPEN
    priority_score: float = 0.5
    reviewability: ReviewabilityStatus = ReviewabilityStatus.EXPERT_REVIEW_REQUIRED
    required_capabilities: Tuple[ReviewerCapability, ...] = Field(default_factory=tuple)
    assigned_reviewer_id: Optional[str] = None
    lease_expires_at: Optional[float] = None
    evidence_package_id: Optional[str] = None
    decisions: Tuple[ReviewDecision, ...] = Field(default_factory=tuple)
    validated_directives: Tuple[ReviewDirective, ...] = Field(default_factory=tuple)
    provenance_record_ids: Tuple[str, ...] = Field(default_factory=tuple)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
