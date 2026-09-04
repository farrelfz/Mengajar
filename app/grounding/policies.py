"""
Domain Grounding Policies: Domain-specific standards for required grounding thresholds and evidence requirements.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from app.grounding.contracts import ClaimType, SourceAuthority


class DomainGroundingPolicy(BaseModel):
    domain: str
    min_overall_score: float = 0.70
    min_coverage_score: float = 0.75
    min_authority: SourceAuthority = SourceAuthority.MEDIUM
    mandatory_grounded_claim_types: list[ClaimType] = Field(
        default_factory=lambda: [ClaimType.DEFINITIONAL, ClaimType.QUANTITATIVE]
    )
    allow_unsupported_rhetoric: bool = True


class DomainGroundingPolicyRegistry:
    """Registry of domain-specific grounding policies."""

    _POLICIES: dict[str, DomainGroundingPolicy] = {
        "physics": DomainGroundingPolicy(
            domain="physics",
            min_overall_score=0.85,
            min_coverage_score=0.85,
            min_authority=SourceAuthority.HIGH,
            mandatory_grounded_claim_types=[ClaimType.DEFINITIONAL, ClaimType.QUANTITATIVE, ClaimType.CAUSAL],
        ),
        "research_methodology": DomainGroundingPolicy(
            domain="research_methodology",
            min_overall_score=0.80,
            min_coverage_score=0.80,
            min_authority=SourceAuthority.HIGH,
            mandatory_grounded_claim_types=[ClaimType.DEFINITIONAL, ClaimType.PROCEDURAL, ClaimType.METHODOLOGY if hasattr(ClaimType, "METHODOLOGY") else ClaimType.FACTUAL],
        ),
        "education": DomainGroundingPolicy(
            domain="education",
            min_overall_score=0.75,
            min_coverage_score=0.75,
            min_authority=SourceAuthority.MEDIUM,
            mandatory_grounded_claim_types=[ClaimType.DEFINITIONAL, ClaimType.PEDAGOGICAL],
        ),
        "general": DomainGroundingPolicy(
            domain="general",
            min_overall_score=0.70,
            min_coverage_score=0.70,
            min_authority=SourceAuthority.MEDIUM,
            mandatory_grounded_claim_types=[ClaimType.DEFINITIONAL],
        ),
    }

    @classmethod
    def get_policy(cls, domain: str) -> DomainGroundingPolicy:
        return cls._POLICIES.get(domain.lower(), cls._POLICIES["general"])
