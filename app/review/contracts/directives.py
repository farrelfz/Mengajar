"""
Universal Document Intelligence System V5 — Review Directive Contracts.

Phase 6: Strongly typed declarative directives emitted by expert reviewers.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.review.contracts.enums import DirectiveCategory, DirectiveType


class ReviewDirective(BaseModel):
    """Declarative, constrained repair or governance directive from a reviewer."""
    model_config = ConfigDict(frozen=True)

    directive_id: str = Field(default_factory=lambda: f"dir_{uuid.uuid4().hex[:8]}")
    directive_type: DirectiveType
    category: DirectiveCategory
    target_element_id: Optional[str] = None
    target_page_or_slide: Optional[int] = None
    target_section: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    rationale: str = Field(min_length=10)
    reviewer_id: str
    is_validated: bool = False
    validation_signature: Optional[str] = None
    created_at: float = Field(default_factory=time.time)


class DirectiveValidationResult(BaseModel):
    """Outcome of checking a candidate directive against safety rules and invariants."""
    model_config = ConfigDict(frozen=True)

    is_valid: bool
    directive_id: str
    violations: Tuple[str, ...] = Field(default_factory=tuple)
    responsible_subsystem: Optional[str] = None
    safe_alternative: Optional[str] = None
    signature: Optional[str] = None
    validated_at: float = Field(default_factory=time.time)
