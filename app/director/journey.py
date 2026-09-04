"""
Learning Journey Model & Synthesis Builder.

Constructs ordered, pedagogically scaffolded LearningJourneys based on strategy,
audience cognitive profile, and format constraints.
"""

from __future__ import annotations

import uuid
from app.director.contracts import (
    AudienceProfile,
    CognitiveLevel,
    DensityBudget,
    LearningGoal,
    LearningJourney,
    LearningStage,
    LearningStageType,
    MaterialStrategyType,
)
from app.director.strategies import get_strategy_definition


class LearningJourneyBuilder:
    """Builds a customized, format-adapted LearningJourney."""

    def build_journey(
        self,
        strategy: MaterialStrategyType,
        goal: LearningGoal,
        audience: AudienceProfile,
        density_budget: DensityBudget,
        format_id: str = "a4_portrait",
    ) -> LearningJourney:
        """Synthesize a complete LearningJourney."""
        strat_def = get_strategy_definition(strategy)
        preferred_stages = list(strat_def.preferred_stages)

        # 1. Format Adaptation: Condense for presentation_16_9 if list is long (>6 stages)
        if format_id == "presentation_16_9" and len(preferred_stages) > 6:
            # Preserve critical stages: Hook, Core, Representation, Summary
            essential = {
                LearningStageType.HOOK,
                LearningStageType.SURFACE_INTUITION,
                LearningStageType.MISCONCEPTION,
                LearningStageType.CONCRETE_EXPERIENCE,
                LearningStageType.CONCEPT_FORMALIZATION,
                LearningStageType.WORKED_EXAMPLE,
                LearningStageType.SUMMARY,
                LearningStageType.CALL_TO_ACTION,
                LearningStageType.PROBLEM_STATEMENT,
                LearningStageType.SYNTHESIS,
            }
            preferred_stages = [s for s in preferred_stages if s in essential][:5]

        # 2. Build individual stages
        stages: list[LearningStage] = []
        for idx, stage_type in enumerate(preferred_stages):
            cog_level = (
                strat_def.cognitive_trajectory[min(idx, len(strat_def.cognitive_trajectory) - 1)]
                if strat_def.cognitive_trajectory
                else CognitiveLevel.UNDERSTAND
            )

            stage = LearningStage(
                stage_type=stage_type,
                title=f"{stage_type.value.replace('_', ' ').title()}: {goal.concept}",
                purpose=f"Stage {idx+1}: {strat_def.display_name} — {stage_type.value}",
                cognitive_level=cog_level,
                target_concepts=[goal.concept],
                key_takeaways=[goal.expected_understanding],
            )
            stages.append(stage)

        journey = LearningJourney(
            journey_id=f"journey_{uuid.uuid4().hex[:8]}",
            strategy=strategy,
            stages=stages,
            total_stages=len(stages),
            estimated_cognitive_load="low" if format_id == "presentation_16_9" else "moderate",
        )
        return journey
