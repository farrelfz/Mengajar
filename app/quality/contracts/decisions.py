"""
Universal Document Intelligence System V5 — Canonical Decision Contracts.

Phase 3A.1: Authoritative export and repair decisions issued exclusively
by the UnifiedQualityAuthority.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Tuple
from pydantic import BaseModel, ConfigDict, Field


class ExportDecision(str, Enum):
    """The 7 authoritative decision states governing artifact export."""
    EXPORT_APPROVED = "EXPORT_APPROVED"
    EXPORT_APPROVED_WITH_WARNINGS = "EXPORT_APPROVED_WITH_WARNINGS"
    REPAIR_REQUIRED = "REPAIR_REQUIRED"
    RENDER_REPAIR_REQUIRED = "RENDER_REPAIR_REQUIRED"
    SEMANTIC_REPAIR_REQUIRED = "SEMANTIC_REPAIR_REQUIRED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


class UnifiedQualityDecision(BaseModel):
    """Authoritative decision object issued by UnifiedQualityAuthority."""
    model_config = ConfigDict(frozen=True)

    decision: ExportDecision
    can_export: bool
    repair_required: bool
    manual_review_required: bool = False
    hard_blockers: Tuple[str, ...] = Field(default_factory=tuple)
    warnings: Tuple[str, ...] = Field(default_factory=tuple)
    rationale: str
