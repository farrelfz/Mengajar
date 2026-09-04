"""
Evidence Ranker: Multi-factor deterministic ranking based on relevance, authority, freshness, specificity, and domain compatibility.
"""

from __future__ import annotations

from app.grounding.contracts import Claim, Evidence, FreshnessStatus, SourceAuthority


class EvidenceRanker:
    """Computes weighted multi-dimensional score for retrieved evidence candidates."""

    WEIGHT_RELEVANCE: float = 0.40
    WEIGHT_AUTHORITY: float = 0.25
    WEIGHT_SPECIFICITY: float = 0.15
    WEIGHT_DOMAIN: float = 0.10
    WEIGHT_FRESHNESS: float = 0.10

    AUTHORITY_SCORES: dict[SourceAuthority, float] = {
        SourceAuthority.PRIMARY: 1.0,
        SourceAuthority.HIGH: 0.85,
        SourceAuthority.MEDIUM: 0.60,
        SourceAuthority.LOW: 0.30,
        SourceAuthority.UNKNOWN: 0.10,
    }

    @classmethod
    def rank_evidence(cls, claim: Claim, candidates: list[Evidence]) -> list[tuple[float, Evidence]]:
        scored: list[tuple[float, Evidence]] = []

        for ev in candidates:
            # 1. Relevance score (0.0 - 1.0)
            rel_score = ev.relevance_score

            # 2. Authority score
            auth_score = cls.AUTHORITY_SCORES.get(ev.authority, 0.5)

            # 3. Domain compatibility
            dom_score = 1.0 if (ev.domain == claim.domain or ev.domain == "general" or claim.domain == "general") else 0.4

            # 4. Freshness score
            fresh_score = 1.0 if ev.freshness in [FreshnessStatus.CURRENT, FreshnessStatus.TIME_INSENSITIVE] else 0.5

            # 5. Specificity score
            spec_score = min(1.0, len(ev.content.split()) / 25.0)

            total = (
                cls.WEIGHT_RELEVANCE * rel_score
                + cls.WEIGHT_AUTHORITY * auth_score
                + cls.WEIGHT_SPECIFICITY * spec_score
                + cls.WEIGHT_DOMAIN * dom_score
                + cls.WEIGHT_FRESHNESS * fresh_score
            )
            scored.append((round(total, 3), ev))

        # Deterministic sorting
        scored.sort(key=lambda x: (x[0], x[1].evidence_id), reverse=True)
        return scored
