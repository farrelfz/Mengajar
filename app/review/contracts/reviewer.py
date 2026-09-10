"""
Universal Document Intelligence System V5 — Reviewer Profile Contracts.

Phase 6: Strongly typed models for human reviewer capabilities, calibration,
and authorization privileges.
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.review.contracts.enums import ReviewerCapability


class ReviewerCapabilityProfile(BaseModel):
    """Detailed competency profile used by the queue expertise router."""
    model_config = ConfigDict(frozen=True)

    capabilities: Tuple[ReviewerCapability, ...] = Field(default_factory=tuple)
    specialized_artifacts: Tuple[str, ...] = Field(
        default=("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT")
    )
    conflict_of_interest_tags: Tuple[str, ...] = Field(default_factory=tuple)
    years_experience: float = 1.0


class ReviewerProfile(BaseModel):
    """Immutable identity and calibration standing of an expert reviewer."""
    model_config = ConfigDict(frozen=True)

    reviewer_id: str = Field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:8]}")
    name: str
    email: str = ""
    capabilities: Tuple[ReviewerCapability, ...] = Field(default_factory=tuple)
    calibration_score: float = Field(default=1.0, ge=0.0, le=1.0)
    is_active: bool = True
    is_senior_adjudicator: bool = False
    max_concurrent_leases: int = Field(default=3, ge=1, le=10)
    created_at: float = Field(default_factory=time.time)

    def has_capability(self, cap: ReviewerCapability) -> bool:
        return cap in self.capabilities

    def can_adjudicate(self) -> bool:
        return self.is_active and self.is_senior_adjudicator and self.calibration_score >= 0.85
