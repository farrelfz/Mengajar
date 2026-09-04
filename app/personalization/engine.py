"""
Personalization Engine: Master orchestrator producing AdaptationPlan and PersonalizationReport.
"""

from __future__ import annotations

from app.blueprints.contracts import SemanticMaterialBlueprint
from app.personalization.adaptation import AdaptationPlanner
from app.personalization.contracts import (
    AdaptationPlan,
    AdaptationPolicyType,
    LearnerProfile,
    PersonalizationReport,
    PersonalizationTrace,
)


class PersonalizationEngine:
    """Master engine computing explainable pedagogical adaptation plans from learner profiles."""

    def __init__(self) -> None:
        self.planner = AdaptationPlanner()

    def personalize(
        self,
        blueprint: SemanticMaterialBlueprint | None,
        learner_profile: LearnerProfile,
        policy: AdaptationPolicyType = AdaptationPolicyType.BALANCED,
        target_format: str = "a4_portrait",
    ) -> PersonalizationReport:
        # Generate inspectable AdaptationPlan
        plan = self.planner.plan_adaptation(
            blueprint=blueprint,
            profile=learner_profile,
            policy_type=policy,
        )

        trace = PersonalizationTrace(
            profile_id=learner_profile.profile_id,
            policy_applied=policy,
            decisions=plan.decisions,
            constraints_enforced=[
                "semantic_truth_invariance",
                "format_geometry_compliance",
                f"density_modifier_{plan.density_modifier}",
            ],
        )

        return PersonalizationReport(
            learner_profile=learner_profile,
            adaptation_policy=policy,
            adaptation_plan=plan,
            trace=trace,
        )
