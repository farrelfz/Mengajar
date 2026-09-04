"""
Source Authority & Freshness Evaluators.
"""

from __future__ import annotations

from app.grounding.contracts import FreshnessStatus, KnowledgeSource, SourceAuthority


class SourceAuthorityEvaluator:
    @classmethod
    def score_authority(cls, authority: SourceAuthority) -> float:
        mapping = {
            SourceAuthority.PRIMARY: 1.0,
            SourceAuthority.HIGH: 0.85,
            SourceAuthority.MEDIUM: 0.60,
            SourceAuthority.LOW: 0.30,
            SourceAuthority.UNKNOWN: 0.10,
        }
        return mapping.get(authority, 0.5)


class DomainAwareFreshnessPolicy:
    """Evaluates whether knowledge age impacts grounding validity based on domain characteristics."""

    TIME_INSENSITIVE_DOMAINS = {"physics", "mathematics", "classical_mechanics"}
    TIME_SENSITIVE_DOMAINS = {"computer_science", "medicine", "education_policy"}

    @classmethod
    def evaluate_freshness(cls, domain: str, publication_year: int | None = None) -> FreshnessStatus:
        dom = domain.lower()
        if dom in cls.TIME_INSENSITIVE_DOMAINS:
            return FreshnessStatus.TIME_INSENSITIVE

        if publication_year is None:
            return FreshnessStatus.UNKNOWN

        current_year = 2026
        age = current_year - publication_year
        if age <= 5:
            return FreshnessStatus.CURRENT
        else:
            return FreshnessStatus.STALE
