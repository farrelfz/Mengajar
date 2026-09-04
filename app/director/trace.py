"""
Explainable Director Trace recorder.
"""

from __future__ import annotations

from app.director.contracts import DirectorTrace, LearningJourney, MaterialStrategyType


class DirectorTraceBuilder:
    """Builds machine-readable explainability traces detailing why decisions were made."""

    def build_trace(
        self,
        strategy: MaterialStrategyType,
        strategy_reasons: list[str],
        journey: LearningJourney,
        domain_policy: str,
        density_reason: str,
    ) -> DirectorTrace:
        stage_reasons = []
        for s in journey.stages:
            stage_reasons.append({
                "stage": s.stage_type.value,
                "purpose": s.purpose,
                "cognitive_level": s.cognitive_level.value,
            })

        return DirectorTrace(
            strategy=strategy.value,
            strategy_reasons=strategy_reasons,
            stage_reasons=stage_reasons,
            policy_applied=domain_policy,
            density_reason=density_reason,
        )
