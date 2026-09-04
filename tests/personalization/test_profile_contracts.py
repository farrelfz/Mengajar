"""
Unit tests for LearnerProfile contracts, enums, and serialization.
"""

import pytest
from app.personalization.contracts import (
    AbstractionPreference,
    AdaptationPolicyType,
    AssessmentReadiness,
    CognitiveSupportNeed,
    DensityTolerance,
    KnowledgeLevel,
    LearnerProfile,
    LearningGoalType,
    PacingPreference,
    PreferredRepresentation,
    PriorKnowledgeState,
    ScaffoldingStrategy,
)
from app.personalization.profiles import CanonicalProfiles


def test_learner_enums_and_constants():
    assert KnowledgeLevel.NOVICE == "novice"
    assert PriorKnowledgeState.NONE == "none"
    assert CognitiveSupportNeed.HIGH_SUPPORT == "high_support"
    assert AbstractionPreference.CONCRETE_FIRST == "concrete_first"
    assert DensityTolerance.LOW == "low"
    assert PacingPreference.SLOW == "slow"
    assert AssessmentReadiness.FOUNDATIONAL == "foundational"
    assert PreferredRepresentation.VISUAL == "visual"
    assert LearningGoalType.UNDERSTAND == "understand"
    assert AdaptationPolicyType.BALANCED == "balanced"
    assert ScaffoldingStrategy.FULL_SUPPORT == "full_support"


def test_canonical_profiles_instantiation():
    novice = CanonicalProfiles.novice_high_support()
    assert novice.knowledge_level == KnowledgeLevel.NOVICE
    assert novice.cognitive_support == CognitiveSupportNeed.HIGH_SUPPORT

    advanced = CanonicalProfiles.advanced_challenge()
    assert advanced.knowledge_level == KnowledgeLevel.ADVANCED
    assert advanced.cognitive_support == CognitiveSupportNeed.CHALLENGE_ORIENTED
