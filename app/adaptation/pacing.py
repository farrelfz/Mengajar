"""
Instructional Duration & Pacing Policy.

Governs pedagogical pacing, stage allocation, and depth scaling across time envelopes.
"""

from __future__ import annotations

from app.adaptation.contracts import InstructionalTimeBudget
from app.director.contracts import LearningJourney, LearningStage, LearningStageType


class PacingPolicy:
    """Adapts a LearningJourney according to the explicit InstructionalTimeBudget."""

    @staticmethod
    def pace_journey(
        journey: LearningJourney,
        budget: InstructionalTimeBudget,
    ) -> tuple[LearningJourney, list[dict[str, str]]]:
        """Pace and adapt stages to fit the duration constraint without losing pedagogical coherence."""
        duration = budget.duration_minutes
        stages = list(journey.stages)
        adjustments: list[dict[str, str]] = []

        if duration <= 15:
            # 15 MIN: Rapid briefing (Keep Hook, Formalization/Concept, Worked Example, Summary)
            essential_types = {
                LearningStageType.HOOK,
                LearningStageType.CONCEPT_FORMALIZATION,
                LearningStageType.WORKED_EXAMPLE,
                LearningStageType.SUMMARY,
                LearningStageType.PROBLEM_STATEMENT,
                LearningStageType.SYNTHESIS,
            }
            paced_stages = [s for s in stages if s.stage_type in essential_types][:4]
            adjustments.append({
                "action": "condensed_for_rapid_briefing",
                "duration": f"{duration}m",
                "remaining_stages": str(len(paced_stages)),
            })
        elif duration <= 45:
            # 45 MIN: Standard lesson (6-8 stages)
            paced_stages = stages[:8]
            adjustments.append({
                "action": "standard_lesson_pacing",
                "duration": f"{duration}m",
                "remaining_stages": str(len(paced_stages)),
            })
        else:
            # 90 MIN+: Deep mastery (Expand with additional practice/challenge stages if missing)
            paced_stages = list(stages)
            existing_types = {s.stage_type for s in paced_stages}

            if LearningStageType.CHALLENGE not in existing_types:
                paced_stages.append(
                    LearningStage(
                        stage_type=LearningStageType.CHALLENGE,
                        title=f"Advanced Challenge & Synthesis: {journey.strategy.value}",
                        purpose="90-Minute Extension: Multi-variable synthesis challenge",
                    )
                )
            if LearningStageType.REFLECTION not in existing_types:
                paced_stages.append(
                    LearningStage(
                        stage_type=LearningStageType.REFLECTION,
                        title="Self-Assessment & Reflection Rubric",
                        purpose="Metacognitive synthesis and mastery evaluation",
                    )
                )

            adjustments.append({
                "action": "expanded_for_deep_mastery",
                "duration": f"{duration}m",
                "total_stages": str(len(paced_stages)),
            })

        journey.stages = paced_stages
        journey.total_stages = len(paced_stages)
        return journey, adjustments
