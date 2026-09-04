"""
Tests for Strategy Selection, Learning Journey Construction, and Stage Transition Grammar.
"""

import pytest

from app.director import (
    AudienceProfile,
    InstructionalIntent,
    IntelligentMaterialDirector,
    KnowledgeState,
    LearningGoal,
    LearningStageType,
    MaterialStrategyType,
    StageTransitionPolicy,
)


@pytest.fixture
def director() -> IntelligentMaterialDirector:
    return IntelligentMaterialDirector()


def test_strategy_selection_novice_physics_selects_concrete_to_abstract(director: IntelligentMaterialDirector):
    goal = LearningGoal(concept="Rotational Torque", expected_understanding="Understand lever arm and torque", domain="physics")
    aud = AudienceProfile(prior_knowledge=KnowledgeState.NOVICE)
    direction = director.direct(goal=goal, audience=aud, intent=InstructionalIntent.TEACH)

    assert direction.strategy in [
        MaterialStrategyType.CONCRETE_TO_ABSTRACT,
        MaterialStrategyType.MISCONCEPTION_CORRECTION,
    ]
    assert len(direction.journey.stages) >= 4
    assert direction.journey.stages[0].stage_type == LearningStageType.HOOK


def test_distinguish_explain_vs_teach(director: IntelligentMaterialDirector):
    goal = LearningGoal(concept="Newton's Third Law", expected_understanding="Action and reaction forces", domain="physics")

    # Intent = EXPLAIN -> Quick Explanation or Conceptual Discovery
    dir_explain = director.direct(goal=goal, intent=InstructionalIntent.EXPLAIN)
    assert dir_explain.strategy in [
        MaterialStrategyType.QUICK_EXPLANATION,
        MaterialStrategyType.CONCEPTUAL_DISCOVERY,
        MaterialStrategyType.CONCRETE_TO_ABSTRACT,
    ]

    # Intent = TEACH -> Scaffolded journey
    dir_teach = director.direct(goal=goal, intent=InstructionalIntent.TEACH)
    assert dir_teach.strategy in [
        MaterialStrategyType.CONCRETE_TO_ABSTRACT,
        MaterialStrategyType.MISCONCEPTION_CORRECTION,
        MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
    ]


def test_stage_transition_grammar_detects_forbidden_ordering():
    # Incoherent sequence: SUMMARY before HOOK
    bad_stages = [
        LearningStageType.SUMMARY,
        LearningStageType.HOOK,
        LearningStageType.CONCEPT_FORMALIZATION,
    ]
    is_valid, warnings = StageTransitionPolicy.validate_journey(bad_stages)
    assert is_valid is False
    assert any("Incoherent stage transition" in w for w in warnings)


def test_stage_transition_grammar_detects_adjacent_duplicates():
    duplicate_stages = [
        LearningStageType.HOOK,
        LearningStageType.HOOK,
        LearningStageType.CONCEPT_FORMALIZATION,
    ]
    is_valid, warnings = StageTransitionPolicy.validate_journey(duplicate_stages)
    assert any("Redundant adjacent duplicate" in w for w in warnings)
