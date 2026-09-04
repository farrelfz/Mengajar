"""
Refinement Planner: Converts diagnostic findings into prioritized, localized RefinementPlans.
"""

from __future__ import annotations

from app.critic.contracts import CritiquePriority, CritiqueReport, CritiqueSeverity
from app.quality.contracts import QualityFinding, QualityReport, QualitySeverity
from app.refinement.contracts import (
    RefinedArtifactBundle,
    RefinementAction,
    RefinementPlan,
    RefinementRisk,
)
from app.refinement.ownership import RefinementOwnershipResolver


class RefinementPlanner:
    """Plans ordered, localized refinement actions from quality and critic findings."""

    @classmethod
    def create_plan(
        cls,
        artifact_bundle: RefinedArtifactBundle,
        quality_report: QualityReport | None,
        critique_report: CritiqueReport | None,
        iteration: int = 1,
    ) -> RefinementPlan:
        actions: list[RefinementAction] = []
        action_idx = 1
        handled_finding_keys = set()

        # 1. Process Quality Findings
        if quality_report and quality_report.findings:
            for qf in quality_report.findings:
                key = f"{qf.dimension.value}_{qf.finding[:30]}"
                if key in handled_finding_keys:
                    continue
                handled_finding_keys.add(key)

                layer, intent, scope = RefinementOwnershipResolver.resolve_quality_finding(qf)
                risk = RefinementRisk.HIGH if qf.severity == QualitySeverity.CRITICAL else RefinementRisk.LOW

                action = RefinementAction(
                    action_id=f"act_qual_{action_idx:02d}",
                    source_finding_ids=[f"qf_{qf.dimension.value}"],
                    target_layer=layer,
                    target_scope=scope,
                    target_identifier=qf.affected_section or "global",
                    intent=intent,
                    rationale=qf.recommendation or qf.finding,
                    expected_benefit=f"Resolves quality finding in {qf.dimension.value}.",
                    estimated_risk=risk,
                    constraints=["preserve_learning_objectives", "preserve_format_geometry"],
                    preservation_requirements=["core_concepts", "learning_objectives"],
                )
                actions.append(action)
                action_idx += 1

        # 2. Process Critic Findings (Prioritized)
        if critique_report and critique_report.findings:
            for cf in critique_report.findings:
                key = f"{cf.perspective.value}_{cf.title}"
                if key in handled_finding_keys:
                    continue
                handled_finding_keys.add(key)

                layer, intent, scope = RefinementOwnershipResolver.resolve_critic_finding(cf)
                risk = RefinementRisk.HIGH if cf.severity == CritiqueSeverity.CRITICAL else RefinementRisk.LOW

                action = RefinementAction(
                    action_id=f"act_crit_{action_idx:02d}",
                    source_finding_ids=[cf.id],
                    target_layer=layer,
                    target_scope=scope,
                    target_identifier=cf.affected_locations[0] if cf.affected_locations else "global",
                    intent=intent,
                    rationale=cf.improvement_direction or cf.diagnosis,
                    expected_benefit=cf.why_it_matters,
                    estimated_risk=risk,
                    constraints=["preserve_learning_objectives", "preserve_format_geometry"],
                    preservation_requirements=["core_concepts", "learning_objectives"],
                )
                actions.append(action)
                action_idx += 1

        # Sort actions deterministically by risk (LOW risk first, then MEDIUM, HIGH)
        risk_rank = {RefinementRisk.LOW: 0, RefinementRisk.MEDIUM: 1, RefinementRisk.HIGH: 2, RefinementRisk.CRITICAL: 3}
        sorted_actions = sorted(actions, key=lambda a: (risk_rank.get(a.estimated_risk, 4), a.action_id))

        return RefinementPlan(
            plan_id=f"plan_{artifact_bundle.artifact_id}_iter{iteration}",
            source_artifact_id=artifact_bundle.artifact_id,
            iteration=iteration,
            actions=sorted_actions,
            invariants=["learning_objectives_preserved", "core_concepts_preserved", "target_format_invariant"],
            expected_improvement=f"Resolves {len(sorted_actions)} identified weaknesses across layers.",
            risk_summary="LOW" if all(a.estimated_risk == RefinementRisk.LOW for a in sorted_actions) else "MEDIUM",
            trace=[f"Planned {len(sorted_actions)} actions for iteration {iteration}."],
        )
