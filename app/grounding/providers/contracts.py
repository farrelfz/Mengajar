"""
Knowledge Provider contracts and query models.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from app.grounding.contracts import ClaimType, KnowledgeSourceType, SourceAuthority


class KnowledgeQuery(BaseModel):
    """Search query specification passed to knowledge providers."""
    query: str
    domain: str = "general"
    claim_type: ClaimType | None = None
    top_k: int = 5
    source_types: list[KnowledgeSourceType] | None = None
    minimum_authority: SourceAuthority | None = None
    metadata_filters: dict[str, Any] = Field(default_factory=dict)
