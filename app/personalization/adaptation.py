"""
Adaptation Planner: Translates (Blueprint, LearnerProfile, Policy) into an inspectable AdaptationPlan.
"""

from __future__ import annotations

from typing import Any
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.personalization.contracts import (
    AbstractionPreference,
    AdaptationDecision,
    AdaptationPlan,
    AdaptationPolicyType,
    KnowledgeLevel,
    LearnerProfile,
    LearningGoalType,
    PreferredRepresentation,
)
from app.personalization.policies import AdaptationPolicyRegistry


class AdaptationPlanner:
    """Computes first-class AdaptationPlan constraints."""

    @classmethod
    def plan_adaptation(
        cls,
        blueprint: SemanticMaterialBlueprint | None,
        profile: LearnerProfile,
        policy_type: AdaptationPolicyType = AdaptationPolicyType.BALANCED,
    ) -> AdaptationPlan:
        policy = AdaptationPolicyRegistry.get_policy(policy_type)
        decisions: list[AdaptationDecision] = []

        # 1. Complexity & Sequence Strategy Mapping
        if profile.knowledge_level == KnowledgeLevel.NOVICE:
            seq_strat = "concrete_to_abstract"
            complexity = "introductory_intuitive"
            decisions.append(
                AdaptationDecision(
                    dimension="sequence",
                    decision="concrete_to_abstract",
                    rationale="Novice learner requires intuitive grounding and analogies before formalization.",
                )
            )
        elif profile.knowledge_level == KnowledgeLevel.ADVANCED:
            seq_strat = "worked_example_progressive"
            complexity = "formal_rigorous"
            decisions.append(
                AdaptationDecision(
                    dimension="sequence",
                    decision="worked_example_progressive",
                    rationale="Advanced learner benefits from rapid formal models, derivations, and challenge problems.",
                )
            )
        else:
            seq_strat = "conceptual_discovery"
            complexity = "balanced_standard"
            decisions.append(
                AdaptationDecision(
                    dimension="sequence",
                    decision="conceptual_discovery",
                    rationale="Intermediate learner balances guided inquiry with formal models.",
                )
            )

        # 2. Learning Goal Adjustments
        if profile.learning_goal == LearningGoalType.PREPARE_FOR_EXAM:
            seq_strat = "exam_preparation"
            decisions.append(
                AdaptationDecision(
                    dimension="learning_goal",
                    decision="exam_preparation_scaffolding",
                    rationale="Targeting exam preparation: prioritizing worked solutions and diagnostic practice.",
                )
            )
        elif profile.learning_goal == LearningGoalType.CONDUCT_RESEARCH:
            seq_strat = "research_method_tutorial"
            decisions.append(
                AdaptationDecision(
                    dimension="learning_goal",
                    decision="research_methodology_focus",
                    rationale="Targeting research: prioritizing methodological rigor, gap analysis, and variables.",
                )
            )

        # 3. Density & Scaffolding resolution via Policy
        density_mod = policy.resolve_density_modifier(profile)
        scaffolding_strat = policy.resolve_scaffolding(profile)

        # 4. Preferred Capability Families based on Representation
        pref_fams: list[str] = []
        for rep in profile.preferred_representations:
            if rep == PreferredRepresentation.VISUAL:
                pref_fams.extend(["universal.concept_hierarchy", "relationship.two_concept_comparison"])
            elif rep == PreferredRepresentation.QUANTITATIVE:
                pref_fams.extend(["quantitative.derivation", "quantitative.formula_breakdown"])
            elif rep == PreferredRepresentation.DIAGRAMMATIC:
                pref_fams.extend(["relationship.network", "process.timeline"])

        if profile.knowledge_level == KnowledgeLevel.NOVICE:
            pref_fams.insert(0, "pedagogy.analogy")
            pref_fams.insert(1, "pedagogy.concept_checkpoint")

        return AdaptationPlan(
            plan_id=f"plan_adapt_{profile.profile_id}",
            target_complexity_level=complexity,
            sequence_strategy=seq_strat,
            scaffolding_strategy=scaffolding_strat,
            density_modifier=density_mod,
            preferred_capability_families=pref_fams,
            preferred_representations=profile.preferred_representations,
            example_strategy="concrete_first" if profile.abstraction_preference in [AbstractionPreference.CONCRETE_FIRST, AbstractionPreference.CONCRETE_TO_ABSTRACT] else "formal_first",
            assessment_strategy="practice" if profile.learning_goal == LearningGoalType.PRACTICE else "conceptual_checkpoint",
            insert_misconception_checkpoints=len(profile.misconception_risks) > 0,
            decisions=decisions,
        )
