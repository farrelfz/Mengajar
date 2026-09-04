"""
Cognitive Complexity Progression Policy.

Validates and models Bloom's taxonomy progression across learning stages.
"""

from __future__ import annotations

from app.director.contracts import AudienceProfile, CognitiveLevel, KnowledgeState, LearningStage


COGNITIVE_RANKS: dict[CognitiveLevel, int] = {
    CognitiveLevel.RECOGNIZE: 1,
    CognitiveLevel.UNDERSTAND: 2,
    CognitiveLevel.APPLY: 3,
    CognitiveLevel.ANALYZE: 4,
    CognitiveLevel.EVALUATE: 5,
    CognitiveLevel.CREATE: 6,
}


class CognitiveProgressionPolicy:
    """Enforces smooth cognitive development across stages."""

    @staticmethod
    def validate_progression(
        stages: list[LearningStage],
        audience: AudienceProfile,
    ) -> tuple[bool, list[str]]:
        """
        Validates cognitive development.
        Flags premature high-order complexity for novice audiences.
        """
        warnings: list[str] = []

        if not stages:
            return True, []

        ranks = [COGNITIVE_RANKS.get(s.cognitive_level, 2) for s in stages]

        # 1. Novice protection: Check if stage 1 or 2 jumps to EVALUATE/CREATE without scaffolding
        if audience.prior_knowledge in [KnowledgeState.NOVICE, KnowledgeState.UNKNOWN]:
            if ranks[0] >= 5:  # EVALUATE or CREATE
                warnings.append(
                    f"Cognitive hazard: Novice learner introduced immediately to high-order cognitive level '{stages[0].cognitive_level.value}'."
                )

        # 2. Check for abrupt regression or leap (>2 cognitive level jump between adjacent stages)
        for i in range(len(ranks) - 1):
            jump = ranks[i + 1] - ranks[i]
            if jump > 3:
                warnings.append(
                    f"Abrupt cognitive leap (+{jump} levels) from '{stages[i].cognitive_level.value}' to '{stages[i+1].cognitive_level.value}' at stage {i+1}."
                )

        is_valid = len(warnings) == 0
        return is_valid, warnings
