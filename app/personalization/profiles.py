"""
Canonical Learner Profiles and Profile Builder with safe partial default resolution.
"""

from __future__ import annotations

from typing import Any
from app.personalization.contracts import (
    AbstractionPreference,
    AssessmentReadiness,
    CognitiveSupportNeed,
    DensityTolerance,
    KnowledgeLevel,
    LearnerProfile,
    LearningGoalType,
    PacingPreference,
    PreferredRepresentation,
    PriorKnowledgeState,
)


class CanonicalProfiles:
    """Standard predefined pedagogical learner profiles."""

    @classmethod
    def novice_high_support(cls, profile_id: str = "novice_high_support") -> LearnerProfile:
        return LearnerProfile(
            profile_id=profile_id,
            knowledge_level=KnowledgeLevel.NOVICE,
            prior_knowledge=PriorKnowledgeState.NONE,
            cognitive_support=CognitiveSupportNeed.HIGH_SUPPORT,
            abstraction_preference=AbstractionPreference.CONCRETE_FIRST,
            density_tolerance=DensityTolerance.LOW,
            pacing=PacingPreference.SLOW,
            assessment_readiness=AssessmentReadiness.FOUNDATIONAL,
            preferred_representations=[PreferredRepresentation.VISUAL, PreferredRepresentation.TEXTUAL],
            learning_goal=LearningGoalType.UNDERSTAND,
        )

    @classmethod
    def intermediate_balanced(cls, profile_id: str = "intermediate_balanced") -> LearnerProfile:
        return LearnerProfile(
            profile_id=profile_id,
            knowledge_level=KnowledgeLevel.INTERMEDIATE,
            prior_knowledge=PriorKnowledgeState.BASIC,
            cognitive_support=CognitiveSupportNeed.MODERATE,
            abstraction_preference=AbstractionPreference.CONCRETE_TO_ABSTRACT,
            density_tolerance=DensityTolerance.MEDIUM,
            pacing=PacingPreference.MODERATE,
            assessment_readiness=AssessmentReadiness.PRACTICE_READY,
            preferred_representations=[PreferredRepresentation.VISUAL, PreferredRepresentation.SYMBOLIC, PreferredRepresentation.TEXTUAL],
            learning_goal=LearningGoalType.PRACTICE,
        )

    @classmethod
    def advanced_challenge(cls, profile_id: str = "advanced_challenge") -> LearnerProfile:
        return LearnerProfile(
            profile_id=profile_id,
            knowledge_level=KnowledgeLevel.ADVANCED,
            prior_knowledge=PriorKnowledgeState.STRONG,
            cognitive_support=CognitiveSupportNeed.CHALLENGE_ORIENTED,
            abstraction_preference=AbstractionPreference.FORMAL_FIRST,
            density_tolerance=DensityTolerance.HIGH,
            pacing=PacingPreference.ACCELERATED,
            assessment_readiness=AssessmentReadiness.MASTERY_READY,
            preferred_representations=[PreferredRepresentation.QUANTITATIVE, PreferredRepresentation.SYMBOLIC, PreferredRepresentation.DIAGRAMMATIC],
            learning_goal=LearningGoalType.ANALYZE,
        )

    @classmethod
    def exam_preparation(cls, profile_id: str = "exam_preparation") -> LearnerProfile:
        return LearnerProfile(
            profile_id=profile_id,
            knowledge_level=KnowledgeLevel.INTERMEDIATE,
            prior_knowledge=PriorKnowledgeState.SOLID,
            cognitive_support=CognitiveSupportNeed.GUIDED,
            abstraction_preference=AbstractionPreference.BALANCED,
            density_tolerance=DensityTolerance.MEDIUM_HIGH,
            pacing=PacingPreference.FAST,
            assessment_readiness=AssessmentReadiness.TRANSFER_READY,
            preferred_representations=[PreferredRepresentation.SYMBOLIC, PreferredRepresentation.TEXTUAL, PreferredRepresentation.QUANTITATIVE],
            learning_goal=LearningGoalType.PREPARE_FOR_EXAM,
        )

    @classmethod
    def researcher_novice(cls, profile_id: str = "researcher_novice") -> LearnerProfile:
        return LearnerProfile(
            profile_id=profile_id,
            knowledge_level=KnowledgeLevel.BEGINNER,
            prior_knowledge=PriorKnowledgeState.BASIC,
            cognitive_support=CognitiveSupportNeed.GUIDED,
            abstraction_preference=AbstractionPreference.CONCRETE_TO_ABSTRACT,
            density_tolerance=DensityTolerance.MEDIUM,
            pacing=PacingPreference.MODERATE,
            assessment_readiness=AssessmentReadiness.APPLICATION_READY,
            preferred_representations=[PreferredRepresentation.TEXTUAL, PreferredRepresentation.DIAGRAMMATIC],
            learning_goal=LearningGoalType.CONDUCT_RESEARCH,
        )


class LearnerProfileBuilder:
    """Constructs learner profiles with safe fallback resolution for omitted fields."""

    def __init__(self, profile_id: str = "custom_profile") -> None:
        self.profile_id = profile_id
        self.knowledge_level: KnowledgeLevel | None = None
        self.prior_knowledge: PriorKnowledgeState | None = None
        self.cognitive_support: CognitiveSupportNeed | None = None
        self.abstraction_preference: AbstractionPreference | None = None
        self.density_tolerance: DensityTolerance | None = None
        self.pacing: PacingPreference | None = None
        self.assessment_readiness: AssessmentReadiness | None = None
        self.preferred_representations: list[PreferredRepresentation] | None = None
        self.learning_goal: LearningGoalType | None = None

    def with_knowledge_level(self, level: KnowledgeLevel) -> LearnerProfileBuilder:
        self.knowledge_level = level
        return self

    def with_cognitive_support(self, support: CognitiveSupportNeed) -> LearnerProfileBuilder:
        self.cognitive_support = support
        return self

    def with_learning_goal(self, goal: LearningGoalType) -> LearnerProfileBuilder:
        self.learning_goal = goal
        return self

    def build(self) -> LearnerProfile:
        # Safe default fallback resolution
        k_lvl = self.knowledge_level or KnowledgeLevel.INTERMEDIATE
        prior = self.prior_knowledge or (
            PriorKnowledgeState.NONE if k_lvl == KnowledgeLevel.NOVICE else PriorKnowledgeState.BASIC
        )
        support = self.cognitive_support or (
            CognitiveSupportNeed.HIGH_SUPPORT if k_lvl == KnowledgeLevel.NOVICE else CognitiveSupportNeed.MODERATE
        )
        abstract = self.abstraction_preference or (
            AbstractionPreference.CONCRETE_FIRST if k_lvl == KnowledgeLevel.NOVICE else AbstractionPreference.CONCRETE_TO_ABSTRACT
        )
        density = self.density_tolerance or DensityTolerance.MEDIUM
        pace = self.pacing or PacingPreference.MODERATE
        readiness = self.assessment_readiness or AssessmentReadiness.PRACTICE_READY
        reps = self.preferred_representations or [PreferredRepresentation.VISUAL, PreferredRepresentation.TEXTUAL]
        goal = self.learning_goal or LearningGoalType.UNDERSTAND

        return LearnerProfile(
            profile_id=self.profile_id,
            knowledge_level=k_lvl,
            prior_knowledge=prior,
            cognitive_support=support,
            abstraction_preference=abstract,
            density_tolerance=density,
            pacing=pace,
            assessment_readiness=readiness,
            preferred_representations=reps,
            learning_goal=goal,
        )
