"""
Tests for Concept Prerequisite Graph and Duration Pacing Policy.
"""

import pytest

from app.blueprints.content import AudienceLevel
from app.adaptation import (
    ConceptPrerequisiteGraph,
    InstructionalTimeBudget,
    PacingPolicy,
    get_default_learner_profile,
)
from app.director import (
    IntelligentMaterialDirector,
    LearningGoal,
    LearningJourney,
    LearningStage,
    LearningStageType,
    MaterialStrategyType,
)


def test_prerequisite_graph_detects_missing_knowledge():
    learner = get_default_learner_profile(AudienceLevel.MIDDLE_SCHOOL)
    # Middle school learner lacks vector_components and rotational_pivot
    missing = ConceptPrerequisiteGraph.check_missing_prerequisites("torque", learner)
    assert len(missing) > 0
    assert "vector_components" in missing


def test_pacing_policy_adapts_journey_across_durations():
    director = IntelligentMaterialDirector()
    goal = LearningGoal(concept="Torque", expected_understanding="Rotational force", domain="physics")
    direction = director.direct(goal=goal)

    journey = direction.journey

    # 15 min budget
    b15 = InstructionalTimeBudget(duration_minutes=15)
    j15, adj15 = PacingPolicy.pace_journey(journey, b15)
    assert j15.total_stages <= 4
    assert any(a["action"] == "condensed_for_rapid_briefing" for a in adj15)

    # 90 min budget
    b90 = InstructionalTimeBudget(duration_minutes=90)
    j90, adj90 = PacingPolicy.pace_journey(journey, b90)
    assert j90.total_stages >= 6
    assert any(a["action"] == "expanded_for_deep_mastery" for a in adj90)
