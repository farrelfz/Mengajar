"""
Stage Transition Grammar & Journey Validation Policies.

Enforces pedagogical sequencing rules, flags incoherent transitions,
and checks strategy-specific ordering constraints.
"""

from __future__ import annotations

from app.director.contracts import LearningStageType, MaterialStrategyType
from app.director.strategies import get_strategy_definition

# Canonical forbidden adjacent transitions
DISCOURAGED_TRANSITIONS: set[tuple[LearningStageType, LearningStageType]] = {
    (LearningStageType.SUMMARY, LearningStageType.HOOK),
    (LearningStageType.SUMMARY, LearningStageType.ACTIVATE_PRIOR_KNOWLEDGE),
    (LearningStageType.INDEPENDENT_PRACTICE, LearningStageType.CONCEPT_FORMALIZATION),
    (LearningStageType.CALL_TO_ACTION, LearningStageType.HOOK),
    (LearningStageType.CALL_TO_ACTION, LearningStageType.CONTEXT),
}


class StageTransitionPolicy:
    """Validator ensuring a pedagogical learning journey follows sound instructional grammar."""

    @staticmethod
    def validate_journey(
        stages: list[LearningStageType],
        strategy: MaterialStrategyType | None = None,
    ) -> tuple[bool, list[str]]:
        """
        Validate a sequence of learning stages against universal grammar and strategy rules.
        Returns (is_valid, list_of_warnings_or_errors).
        """
        issues: list[str] = []

        if not stages:
            return False, ["Learning journey contains 0 stages."]

        # 1. Check for adjacent duplicates
        for i in range(len(stages) - 1):
            if stages[i] == stages[i + 1]:
                issues.append(f"Redundant adjacent duplicate stage: '{stages[i].value}' at index {i} and {i+1}.")

        # 2. Check universal discouraged transitions
        for i in range(len(stages) - 1):
            pair = (stages[i], stages[i + 1])
            if pair in DISCOURAGED_TRANSITIONS:
                issues.append(
                    f"Incoherent stage transition detected: '{stages[i].value}' -> '{stages[i+1].value}' at step {i}."
                )

        # 3. Check strategy-specific forbidden ordering
        if strategy is not None:
            strat_def = get_strategy_definition(strategy)
            stage_indices = {stage: idx for idx, stage in enumerate(stages)}

            for early_stage, late_stage in strat_def.forbidden_orderings:
                if early_stage in stage_indices and late_stage in stage_indices:
                    if stage_indices[early_stage] > stage_indices[late_stage]:
                        issues.append(
                            f"Strategy '{strategy.value}' violation: '{early_stage.value}' (index {stage_indices[early_stage]}) "
                            f"appears AFTER '{late_stage.value}' (index {stage_indices[late_stage]})."
                        )

        # 4. Check for practice before explanation warning
        if (
            LearningStageType.INDEPENDENT_PRACTICE in stages
            and LearningStageType.WORKED_EXAMPLE in stages
            and stages.index(LearningStageType.INDEPENDENT_PRACTICE) < stages.index(LearningStageType.WORKED_EXAMPLE)
        ):
            issues.append("Pedagogical warning: Independent practice appears before worked example.")

        is_valid = len([msg for msg in issues if not msg.startswith("Pedagogical warning")]) == 0
        return is_valid, issues
