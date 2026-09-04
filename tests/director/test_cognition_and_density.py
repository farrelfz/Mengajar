"""
Tests for Cognitive Progression, Density Budget, Format Awareness, and Misconception Detection.
"""

import pytest

from app.capabilities.taxonomy import DensityProfile
from app.director import (
    AudienceProfile,
    CognitiveLevel,
    CognitiveProgressionPolicy,
    InstructionalIntent,
    IntelligentMaterialDirector,
    KnowledgeState,
    LearningGoal,
    LearningStage,
    LearningStageType,
    MaterialStrategyType,
    MisconceptionDetector,
)


@pytest.fixture
def director() -> IntelligentMaterialDirector:
    return IntelligentMaterialDirector()


def test_cognitive_progression_novice_evaluation_warning():
    aud = AudienceProfile(prior_knowledge=KnowledgeState.NOVICE)
    abrupt_stages = [
        LearningStage(
            stage_type=LearningStageType.CHALLENGE,
            title="Complex Synthesis",
            purpose="Synthesize advanced models",
            cognitive_level=CognitiveLevel.CREATE,
        )
    ]
    is_valid, warnings = CognitiveProgressionPolicy.validate_progression(abrupt_stages, aud)
    assert is_valid is False
    assert any("Novice learner introduced immediately to high-order" in w for w in warnings)


def test_format_aware_density_adaptation(director: IntelligentMaterialDirector):
    goal = LearningGoal(concept="Cellular Respiration", expected_understanding="ATP synthesis pathways", domain="general")

    # 16:9 Presentation should have low density budget
    dir_16_9 = director.direct(goal=goal, format_id="presentation_16_9")
    assert dir_16_9.diagnostics.density_budget == "low"
    assert len(dir_16_9.journey.stages) <= 6

    # A4 Portrait can support higher density
    dir_a4 = director.direct(goal=goal, format_id="a4_portrait")
    assert dir_a4.diagnostics.density_budget == "medium"


def test_misconception_opportunity_detection(director: IntelligentMaterialDirector):
    misc = MisconceptionDetector.detect_for_topic("Understanding torque on a pivot")
    assert misc is not None
    assert "Greater applied force always produces greater rotational torque" in misc.misconception_statement

    # When strategy is MISCONCEPTION_CORRECTION, statement is populated into payload
    goal = LearningGoal(concept="Understanding torque on a pivot", expected_understanding="Force vs lever arm", domain="physics")
    direction = director.direct(
        goal=goal,
        preferred_strategy=MaterialStrategyType.MISCONCEPTION_CORRECTION,
    )
    misc_stage = next((s for s in direction.journey.stages if s.stage_type == LearningStageType.MISCONCEPTION), None)
    assert misc_stage is not None
    assert "misconception_statement" in misc_stage.content_payload
