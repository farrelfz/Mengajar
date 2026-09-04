"""
Critique Prioritizer: Ranks findings into an explainable priority queue.
"""

from __future__ import annotations

from app.critic.contracts import (
    CritiqueAgreement,
    CritiqueFinding,
    CritiquePriority,
    CritiqueSeverity,
)


class CritiquePrioritizer:
    """Computes actionable priority rankings considering severity, confidence, and agreement."""

    @classmethod
    def prioritize(
        cls,
        findings: list[CritiqueFinding],
        agreements: list[CritiqueAgreement],
    ) -> list[str]:
        """Returns finding IDs ordered from highest priority to lowest priority."""
        if not findings:
            return []

        # Map agreement boosts
        boosted_ids = set()
        for agr in agreements:
            boosted_ids.update(agr.finding_ids)

        def score_finding(f: CritiqueFinding) -> tuple[int, int, str]:
            # Severity numeric rank (higher is more urgent)
            sev_map = {
                CritiqueSeverity.CRITICAL: 40,
                CritiqueSeverity.HIGH: 30,
                CritiqueSeverity.MEDIUM: 20,
                CritiqueSeverity.LOW: 10,
            }
            base = sev_map.get(f.severity, 20)

            # Consensus boost
            if f.id in boosted_ids:
                base += 5

            # Scope count
            scope_weight = min(len(f.affected_locations), 5)

            # Return tuple for sorting: (-score, -scope, id) for deterministic ordering
            return (-base, -scope_weight, f.id)

        sorted_findings = sorted(findings, key=score_finding)
        return [f.id for f in sorted_findings]

    @classmethod
    def derive_priority_level(cls, finding: CritiqueFinding, is_boosted: bool = False) -> CritiquePriority:
        if finding.severity == CritiqueSeverity.CRITICAL:
            return CritiquePriority.BLOCKER
        elif finding.severity == CritiqueSeverity.HIGH:
            return CritiquePriority.CRITICAL if is_boosted else CritiquePriority.HIGH
        elif finding.severity == CritiqueSeverity.MEDIUM:
            return CritiquePriority.HIGH if is_boosted else CritiquePriority.MEDIUM
        return CritiquePriority.LOW
