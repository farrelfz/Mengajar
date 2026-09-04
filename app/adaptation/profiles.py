"""
Standard Learner Profiles & Complexity Policies.
"""

from app.blueprints.content import AudienceLevel
from app.adaptation.contracts import (
    ComplexityLevel,
    ContentComplexityProfile,
    LearnerProfile,
)
from app.director.contracts import CognitiveLevel, KnowledgeState


def get_default_learner_profile(
    audience: AudienceLevel = AudienceLevel.HIGH_SCHOOL,
    knowledge_state: KnowledgeState = KnowledgeState.NOVICE,
) -> LearnerProfile:
    """Construct a canonical LearnerProfile based on education level and knowledge state."""
    if audience == AudienceLevel.MIDDLE_SCHOOL:
        return LearnerProfile(
            educational_level=AudienceLevel.MIDDLE_SCHOOL,
            age_band="12-15",
            knowledge_state=knowledge_state,
            prerequisite_mastery={"basic_arithmetic": True, "basic_forces": True, "vectors": False},
            mathematical_readiness=ComplexityLevel.FOUNDATIONAL,
            scientific_reasoning_level=ComplexityLevel.FOUNDATIONAL,
            vocabulary_level=ComplexityLevel.FOUNDATIONAL,
            cognitive_readiness=CognitiveLevel.RECOGNIZE,
        )
    elif audience == AudienceLevel.UNDERGRADUATE:
        return LearnerProfile(
            educational_level=AudienceLevel.UNDERGRADUATE,
            age_band="18-22",
            knowledge_state=knowledge_state,
            prerequisite_mastery={"calculus": True, "vector_algebra": True, "newtonian_mechanics": True},
            mathematical_readiness=ComplexityLevel.ADVANCED,
            scientific_reasoning_level=ComplexityLevel.ADVANCED,
            vocabulary_level=ComplexityLevel.ADVANCED,
            cognitive_readiness=CognitiveLevel.ANALYZE,
        )
    elif audience == AudienceLevel.RESEARCHER:
        return LearnerProfile(
            educational_level=audience,
            age_band="22+",
            knowledge_state=knowledge_state,
            prerequisite_mastery={"advanced_mathematics": True, "research_methodology": True},
            mathematical_readiness=ComplexityLevel.EXPERT,
            scientific_reasoning_level=ComplexityLevel.EXPERT,
            vocabulary_level=ComplexityLevel.EXPERT,
            cognitive_readiness=CognitiveLevel.EVALUATE,
        )
    else:  # High School Default
        return LearnerProfile(
            educational_level=AudienceLevel.HIGH_SCHOOL,
            age_band="15-18",
            knowledge_state=knowledge_state,
            prerequisite_mastery={"trigonometry": True, "scalar_forces": True, "vector_components": True},
            mathematical_readiness=ComplexityLevel.INTERMEDIATE,
            scientific_reasoning_level=ComplexityLevel.INTERMEDIATE,
            vocabulary_level=ComplexityLevel.INTERMEDIATE,
            cognitive_readiness=CognitiveLevel.UNDERSTAND,
        )


class ComplexityPolicy:
    """Derives a 10-dimensional ContentComplexityProfile from a LearnerProfile."""

    @staticmethod
    def derive_complexity_profile(learner: LearnerProfile) -> ContentComplexityProfile:
        level = learner.educational_level

        if level == AudienceLevel.MIDDLE_SCHOOL:
            return ContentComplexityProfile(
                abstraction_level=ComplexityLevel.FOUNDATIONAL,
                conceptual_depth=ComplexityLevel.FOUNDATIONAL,
                vocabulary_complexity=ComplexityLevel.FOUNDATIONAL,
                mathematical_formalism=ComplexityLevel.FOUNDATIONAL,
                reasoning_complexity=ComplexityLevel.FOUNDATIONAL,
                example_complexity=ComplexityLevel.FOUNDATIONAL,
                evidence_requirement=ComplexityLevel.FOUNDATIONAL,
                task_open_endedness=ComplexityLevel.FOUNDATIONAL,
                prerequisite_dependency=ComplexityLevel.FOUNDATIONAL,
                misconception_depth=ComplexityLevel.FOUNDATIONAL,
            )
        elif level == AudienceLevel.UNDERGRADUATE:
            return ContentComplexityProfile(
                abstraction_level=ComplexityLevel.ADVANCED,
                conceptual_depth=ComplexityLevel.ADVANCED,
                vocabulary_complexity=ComplexityLevel.ADVANCED,
                mathematical_formalism=ComplexityLevel.ADVANCED,
                reasoning_complexity=ComplexityLevel.ADVANCED,
                example_complexity=ComplexityLevel.ADVANCED,
                evidence_requirement=ComplexityLevel.ADVANCED,
                task_open_endedness=ComplexityLevel.ADVANCED,
                prerequisite_dependency=ComplexityLevel.ADVANCED,
                misconception_depth=ComplexityLevel.ADVANCED,
            )
        elif level == AudienceLevel.RESEARCHER:
            return ContentComplexityProfile(
                abstraction_level=ComplexityLevel.EXPERT,
                conceptual_depth=ComplexityLevel.EXPERT,
                vocabulary_complexity=ComplexityLevel.EXPERT,
                mathematical_formalism=ComplexityLevel.EXPERT,
                reasoning_complexity=ComplexityLevel.EXPERT,
                example_complexity=ComplexityLevel.EXPERT,
                evidence_requirement=ComplexityLevel.EXPERT,
                task_open_endedness=ComplexityLevel.EXPERT,
                prerequisite_dependency=ComplexityLevel.EXPERT,
                misconception_depth=ComplexityLevel.EXPERT,
            )
        else:  # High School
            return ContentComplexityProfile(
                abstraction_level=ComplexityLevel.INTERMEDIATE,
                conceptual_depth=ComplexityLevel.INTERMEDIATE,
                vocabulary_complexity=ComplexityLevel.INTERMEDIATE,
                mathematical_formalism=ComplexityLevel.INTERMEDIATE,
                reasoning_complexity=ComplexityLevel.INTERMEDIATE,
                example_complexity=ComplexityLevel.INTERMEDIATE,
                evidence_requirement=ComplexityLevel.INTERMEDIATE,
                task_open_endedness=ComplexityLevel.INTERMEDIATE,
                prerequisite_dependency=ComplexityLevel.INTERMEDIATE,
                misconception_depth=ComplexityLevel.INTERMEDIATE,
            )
