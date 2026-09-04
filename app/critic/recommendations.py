"""
Recommendation Generator: Produces structured, non-destructive improvement directions.
"""

from __future__ import annotations

from app.critic.contracts import (
    CritiqueAgreement,
    CritiqueFinding,
    CritiquePriority,
    CritiqueRecommendation,
    ImplementationScope,
)
from app.critic.prioritization import CritiquePrioritizer


class RecommendationGenerator:
    """Transforms prioritized critique findings into actionable, non-destructive recommendations."""

    @classmethod
    def generate_recommendations(
        cls,
        findings: list[CritiqueFinding],
        agreements: list[CritiqueAgreement],
    ) -> list[CritiqueRecommendation]:
        recommendations: list[CritiqueRecommendation] = []
        boosted_ids = {f_id for agr in agreements for f_id in agr.finding_ids}

        for idx, finding in enumerate(findings, start=1):
            is_boosted = finding.id in boosted_ids
            prio = CritiquePrioritizer.derive_priority_level(finding, is_boosted=is_boosted)

            # Determine implementation scope based on affected locations
            if "global" in finding.affected_locations:
                scope = ImplementationScope.GLOBAL_PATTERN
            elif len(finding.affected_locations) > 1:
                scope = ImplementationScope.SECTION
            elif finding.affected_locations and "Page" in finding.affected_locations[0]:
                scope = ImplementationScope.PAGE
            else:
                scope = ImplementationScope.BLOCK

            rec = CritiqueRecommendation(
                id=f"rec_{finding.perspective.value}_{idx:02d}",
                finding_ids=[finding.id],
                recommendation=finding.improvement_direction,
                rationale=finding.why_it_matters,
                expected_impact=f"Resolves {finding.severity.value}-severity weakness: {finding.title}.",
                implementation_scope=scope,
                priority=prio,
            )
            recommendations.append(rec)

        # Sort recommendations deterministically by priority
        prio_rank = {
            CritiquePriority.BLOCKER: 0,
            CritiquePriority.CRITICAL: 1,
            CritiquePriority.HIGH: 2,
            CritiquePriority.MEDIUM: 3,
            CritiquePriority.LOW: 4,
        }
        return sorted(recommendations, key=lambda r: (prio_rank.get(r.priority, 5), r.id))
