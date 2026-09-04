"""
Grounding Score: Explainable composite scoring across coverage, support strength, authority, freshness, and consistency.
"""

from __future__ import annotations

from app.grounding.contracts import (
    Claim,
    ClaimEvidenceLink,
    Evidence,
    GroundingScore,
    GroundingStatus,
    SupportRelation,
)


class GroundingScoreCalculator:
    """Computes transparent, explainable grounding metrics."""

    @classmethod
    def calculate_score(
        cls,
        claims: list[Claim],
        evidence: list[Evidence],
        links: list[ClaimEvidenceLink],
    ) -> GroundingScore:
        req_claims = [c for c in claims if c.requires_grounding]
        if not req_claims:
            return GroundingScore(
                coverage=1.0,
                support_strength=1.0,
                authority=1.0,
                freshness=1.0,
                consistency=1.0,
                overall_score=1.0,
            )

        # 1. Coverage
        grounded_or_partial = [c for c in req_claims if c.grounding_status in [GroundingStatus.GROUNDED, GroundingStatus.PARTIALLY_GROUNDED]]
        coverage = round(len(grounded_or_partial) / len(req_claims), 3)

        # 2. Support Strength
        supporting_links = [l for l in links if l.relation in [SupportRelation.SUPPORTS, SupportRelation.PARTIALLY_SUPPORTS]]
        support_strength = round(
            sum(l.support_score for l in supporting_links) / (len(supporting_links) + 1e-6), 3
        ) if supporting_links else 0.0

        # 3. Authority
        auth_scores = [1.0 if ev.authority.value == "primary" else 0.85 if ev.authority.value == "high" else 0.6 for ev in evidence]
        authority = round(sum(auth_scores) / (len(auth_scores) + 1e-6), 3) if auth_scores else 0.5

        # 4. Freshness
        freshness = 1.0

        # 5. Consistency
        contradicted_count = sum(1 for c in req_claims if c.grounding_status == GroundingStatus.CONTRADICTED)
        consistency = 1.0 if contradicted_count == 0 else max(0.0, 1.0 - (contradicted_count * 0.5))

        # Overall composite (weighted mean)
        overall = round(
            0.30 * coverage
            + 0.25 * support_strength
            + 0.20 * authority
            + 0.10 * freshness
            + 0.15 * consistency,
            3,
        )

        return GroundingScore(
            coverage=coverage,
            support_strength=min(1.0, support_strength),
            authority=min(1.0, authority),
            freshness=freshness,
            consistency=consistency,
            overall_score=min(1.0, max(0.0, overall)),
        )
