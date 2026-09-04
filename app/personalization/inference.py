"""
Safe Non-Invasive Contextual Profile Inference.
"""

from __future__ import annotations

import re
from typing import Any
from pydantic import BaseModel, Field

from app.blueprints.content import AudienceLevel
from app.personalization.contracts import (
    AbstractionPreference,
    CognitiveSupportNeed,
    DensityTolerance,
    KnowledgeLevel,
    LearnerProfile,
    LearningGoalType,
    PreferredRepresentation,
    PriorKnowledgeState,
)
from app.personalization.profiles import CanonicalProfiles, LearnerProfileBuilder


class ProfileEvidence(BaseModel):
    field: str
    value: str
    source: str = "explicit"  # explicit, inferred, default
    confidence: float = 1.0


class ProfileInferenceEngine:
    """Infers baseline learner profile safely from explicit instructional hints without sensitive demographic profiling."""

    @classmethod
    def infer_from_context(
        cls,
        audience_level: AudienceLevel | str | None = None,
        context_prompt: str | None = None,
    ) -> LearnerProfile:
        builder = LearnerProfileBuilder(profile_id="inferred_profile")
        prompt_lower = (context_prompt or "").lower()

        # 1. Infer from AudienceLevel enum
        aud_str = str(audience_level or "").lower()
        if "middle_school" in aud_str or "beginner" in aud_str or "smp" in prompt_lower or "dasar" in prompt_lower:
            builder.with_knowledge_level(KnowledgeLevel.BEGINNER)
            builder.with_cognitive_support(CognitiveSupportNeed.HIGH_SUPPORT)
        elif "high_school" in aud_str or "sma" in prompt_lower or "kelas xi" in prompt_lower:
            builder.with_knowledge_level(KnowledgeLevel.INTERMEDIATE)
            builder.with_cognitive_support(CognitiveSupportNeed.MODERATE)
        elif "researcher" in aud_str or "peneliti" in prompt_lower or "advanced" in aud_str:
            builder.with_knowledge_level(KnowledgeLevel.ADVANCED)
            builder.with_cognitive_support(CognitiveSupportNeed.CHALLENGE_ORIENTED)

        # 2. Infer Learning Goal from prompt keywords
        if "ujian" in prompt_lower or "exam" in prompt_lower or "latihan soal" in prompt_lower:
            builder.with_learning_goal(LearningGoalType.PREPARE_FOR_EXAM)
        elif "penelitian" in prompt_lower or "skripsi" in prompt_lower or "research" in prompt_lower:
            builder.with_learning_goal(LearningGoalType.CONDUCT_RESEARCH)
        elif "mengajar" in prompt_lower or "teach" in prompt_lower:
            builder.with_learning_goal(LearningGoalType.TEACH_OTHERS)

        return builder.build()
