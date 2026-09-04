"""
Unit tests for Partial Profiles and safe fallback default resolution.
"""

import pytest
from app.personalization.contracts import (
    AbstractionPreference,
    CognitiveSupportNeed,
    KnowledgeLevel,
    LearnerProfile,
    LearningGoalType,
    PriorKnowledgeState,
)
from app.personalization.inference import ProfileInferenceEngine
from app.personalization.profiles import LearnerProfileBuilder


def test_builder_resolves_safe_defaults_for_partial_novice():
    # Only knowledge_level specified
    profile = LearnerProfileBuilder("part_novice").with_knowledge_level(KnowledgeLevel.NOVICE).build()

    assert profile.knowledge_level == KnowledgeLevel.NOVICE
    assert profile.prior_knowledge == PriorKnowledgeState.NONE
    assert profile.cognitive_support == CognitiveSupportNeed.HIGH_SUPPORT
    assert profile.abstraction_preference == AbstractionPreference.CONCRETE_FIRST


def test_inference_engine_infers_from_context():
    profile = ProfileInferenceEngine.infer_from_context(
        audience_level="high_school",
        context_prompt="Latihan soal persiapan ujian fisika SMA",
    )

    assert profile.knowledge_level == KnowledgeLevel.INTERMEDIATE
    assert profile.learning_goal == LearningGoalType.PREPARE_FOR_EXAM
