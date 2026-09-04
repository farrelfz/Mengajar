"""
Unit tests for Intelligent Director integration with Personalization.
"""

import pytest
from app.director import (
    AudienceProfile,
    InstructionalIntent,
    IntelligentMaterialDirector,
    KnowledgeState,
    LearningGoal,
    MaterialStrategyType,
)
from app.personalization.contracts import AdaptationPolicyType
from app.personalization.engine import PersonalizationEngine
from app.personalization.profiles import CanonicalProfiles


def test_director_choreographs_novice_journey():
    engine = PersonalizationEngine()
    director = IntelligentMaterialDirector()

    novice = CanonicalProfiles.novice_high_support()
    report = engine.personalize(blueprint=None, learner_profile=novice)

    goal = LearningGoal(concept="Torque", expected_understanding="Understand torque intuitively", domain="physics")
    aud_prof = AudienceProfile(education_level="middle_school", prior_knowledge=KnowledgeState.NOVICE)

    # Pass adapted sequence strategy to director
    direction = director.direct(
        goal=goal,
        audience=aud_prof,
        intent=InstructionalIntent.TEACH,
        format_id="a4_portrait",
        preferred_strategy=MaterialStrategyType(report.adaptation_plan.sequence_strategy),
    )

    stage_types = [s.stage_type.value for s in direction.journey.stages]
    # Invariant: Novice journey must have concrete experience/intuition early
    assert "hook" in stage_types or "surface_intuition" in stage_types or "concrete_experience" in stage_types
