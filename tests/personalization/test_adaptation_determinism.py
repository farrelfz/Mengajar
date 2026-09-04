"""
Unit tests for Personalization determinism across 10 consecutive executions.
"""

import pytest
from app.personalization.contracts import AdaptationPolicyType
from app.personalization.engine import PersonalizationEngine
from app.personalization.profiles import CanonicalProfiles


def test_personalization_determinism_across_10_runs():
    engine = PersonalizationEngine()
    profile = CanonicalProfiles.intermediate_balanced()

    reports = [
        engine.personalize(
            blueprint=None,
            learner_profile=profile,
            policy=AdaptationPolicyType.BALANCED,
        )
        for _ in range(10)
    ]

    first = reports[0]
    for idx, rep in enumerate(reports[1:], start=2):
        assert rep.adaptation_plan.target_complexity_level == first.adaptation_plan.target_complexity_level, f"Complexity mismatch on run {idx}"
        assert rep.adaptation_plan.sequence_strategy == first.adaptation_plan.sequence_strategy, f"Strategy mismatch on run {idx}"
        assert rep.adaptation_plan.density_modifier == first.adaptation_plan.density_modifier, f"Density mismatch on run {idx}"
        assert rep.adaptation_plan.scaffolding_strategy == first.adaptation_plan.scaffolding_strategy, f"Scaffolding mismatch on run {idx}"
        assert len(rep.trace.decisions) == len(first.trace.decisions), f"Decisions count mismatch on run {idx}"
