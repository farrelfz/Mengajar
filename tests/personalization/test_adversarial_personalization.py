"""
Adversarial personalization tests: Negative constraints and boundary verification.
"""

import pytest
from app.personalization.contracts import (
    AdaptationPolicyType,
    KnowledgeLevel,
    ScaffoldingStrategy,
)
from app.personalization.engine import PersonalizationEngine
from app.personalization.profiles import CanonicalProfiles


def test_novice_profile_never_assigns_zero_scaffolding():
    engine = PersonalizationEngine()
    novice = CanonicalProfiles.novice_high_support()

    report = engine.personalize(blueprint=None, learner_profile=novice, policy=AdaptationPolicyType.BALANCED)

    assert report.adaptation_plan.scaffolding_strategy != ScaffoldingStrategy.NONE
    assert report.adaptation_plan.scaffolding_strategy == ScaffoldingStrategy.FULL_SUPPORT


def test_advanced_profile_never_forced_into_full_scaffolding():
    engine = PersonalizationEngine()
    advanced = CanonicalProfiles.advanced_challenge()

    report = engine.personalize(blueprint=None, learner_profile=advanced, policy=AdaptationPolicyType.MASTERY_FIRST)

    assert report.adaptation_plan.scaffolding_strategy != ScaffoldingStrategy.FULL_SUPPORT
    assert report.adaptation_plan.scaffolding_strategy == ScaffoldingStrategy.MINIMAL
