"""
Tests for Choreography, Explainable Trace, Diagnostics, Manual Overrides, and Determinism.
"""

import pytest

from app.capabilities.taxonomy import CapabilityFamily, SemanticIntent
from app.director import (
    AudienceProfile,
    InstructionalIntent,
    IntelligentMaterialDirector,
    LearningGoal,
    MaterialStrategyType,
)


@pytest.fixture
def director() -> IntelligentMaterialDirector:
    return IntelligentMaterialDirector()


def test_choreography_generates_typed_requirements_without_hardcoded_ids(director: IntelligentMaterialDirector):
    goal = LearningGoal(concept="Paragraph Anatomy", expected_understanding="Topic sentence to analysis", domain="academic_writing")
    direction = director.direct(goal=goal)

    assert len(direction.choreography) == len(direction.journey.stages)
    for req in direction.choreography:
        assert isinstance(req.primary_intent, SemanticIntent)
        assert req.pedagogical_role is not None
        assert req.density is not None
        # Verify NO hardcoded capability ID is stored on the requirement (pure taxonomy requirement!)
        assert not hasattr(req, "capability_id")


def test_director_trace_explainability(director: IntelligentMaterialDirector):
    goal = LearningGoal(concept="Research Gap Identification", expected_understanding="Formulating novelty", domain="research_education")
    direction = director.direct(goal=goal)

    trace = direction.trace
    assert trace.strategy is not None
    assert len(trace.strategy_reasons) > 0
    assert len(trace.stage_reasons) == len(direction.journey.stages)
    assert trace.policy_applied == "research_education"


def test_manual_strategy_override_with_diagnostics(director: IntelligentMaterialDirector):
    goal = LearningGoal(concept="Thermodynamics First Law", expected_understanding="Energy conservation", domain="physics")

    # Manually force RESEARCH_METHOD_TUTORIAL on a physics topic
    direction = director.direct(
        goal=goal,
        preferred_strategy=MaterialStrategyType.RESEARCH_METHOD_TUTORIAL,
    )
    assert direction.strategy == MaterialStrategyType.RESEARCH_METHOD_TUTORIAL
    assert any("Manual override" in r for r in direction.trace.strategy_reasons)


def test_director_determinism_across_three_runs(director: IntelligentMaterialDirector):
    goal = LearningGoal(concept="Graph Interpretation", expected_understanding="Axis and trend reading", domain="data_literacy")

    run1 = director.direct(goal=goal, format_id="a4_landscape")
    run2 = director.direct(goal=goal, format_id="a4_landscape")
    run3 = director.direct(goal=goal, format_id="a4_landscape")

    assert run1.strategy == run2.strategy == run3.strategy
    assert len(run1.journey.stages) == len(run2.journey.stages) == len(run3.journey.stages)
    for s1, s2, s3 in zip(run1.journey.stages, run2.journey.stages, run3.journey.stages):
        assert s1.stage_type == s2.stage_type == s3.stage_type
