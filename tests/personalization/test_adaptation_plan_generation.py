"""
Unit tests for AdaptationPlan generation from profiles and policies.
"""

import pytest
from app.personalization.contracts import (
    AdaptationPolicyType,
    KnowledgeLevel,
    ScaffoldingStrategy,
)
from app.personalization.engine import PersonalizationEngine
from app.personalization.profiles import CanonicalProfiles


def test_personalization_engine_plans_novice_adaptation():
    engine = PersonalizationEngine()
    novice = CanonicalProfiles.novice_high_support()

    report = engine.personalize(
        blueprint=None,
        learner_profile=novice,
        policy=AdaptationPolicyType.BALANCED,
    )

    plan = report.adaptation_plan
    assert plan.target_complexity_level == "introductory_intuitive"
    assert plan.sequence_strategy == "concrete_to_abstract"
    assert plan.scaffolding_strategy == ScaffoldingStrategy.FULL_SUPPORT
    assert plan.density_modifier <= 0.85
    assert "pedagogy.analogy" in plan.preferred_capability_families


def test_personalization_engine_plans_advanced_adaptation():
    engine = PersonalizationEngine()
    advanced = CanonicalProfiles.advanced_challenge()

    report = engine.personalize(
        blueprint=None,
        learner_profile=advanced,
        policy=AdaptationPolicyType.BALANCED,
    )

    plan = report.adaptation_plan
    assert plan.target_complexity_level == "formal_rigorous"
    assert plan.sequence_strategy == "worked_example_progressive"
    assert plan.scaffolding_strategy == ScaffoldingStrategy.MINIMAL
    assert plan.density_modifier >= 1.15
    assert "quantitative.derivation" in plan.preferred_capability_families
