"""
Adversarial Case D: Pedagogical sequence violations and inverted scaffolding.
"""

import pytest

from app.director.contracts import (
    LearningJourney,
    LearningStage,
    LearningStageType,
    MaterialStrategyType,
)
from app.quality.contracts import QualityDimension, QualitySeverity
from app.quality.pedagogical_evaluator import PedagogicalEvaluator


def test_practice_before_concept_triggers_pedagogical_error():
    # Practice placed BEFORE concept formalization
    journey = LearningJourney(
        journey_id="j_bad_practice",
        strategy=MaterialStrategyType.PROBLEM_BASED_LEARNING,
        stages=[
            LearningStage(
                stage_type=LearningStageType.INDEPENDENT_PRACTICE,
                title="Practice Problem 1",
                purpose="Solve complex problems",
            ),
            LearningStage(
                stage_type=LearningStageType.CONCEPT_FORMALIZATION,
                title="Theory & Formulas",
                purpose="Learn principles",
            ),
        ],
    )

    metrics, findings = PedagogicalEvaluator.evaluate(journey)

    assert len(findings) >= 1
    assert any(f.severity == QualitySeverity.ERROR for f in findings)
    assert any("practice stage appears before concept formalization" in f.finding.lower() for f in findings)
    assert metrics[0].score <= 0.65


def test_challenge_before_concept_triggers_warning():
    journey = LearningJourney(
        journey_id="j_bad_challenge",
        strategy=MaterialStrategyType.CONCEPTUAL_DISCOVERY,
        stages=[
            LearningStage(
                stage_type=LearningStageType.CHALLENGE,
                title="Olympiad Challenge Problem",
                purpose="Test advanced synthesis",
            ),
            LearningStage(
                stage_type=LearningStageType.CONCEPT_FORMALIZATION,
                title="Foundational Definition",
                purpose="Define core idea",
            ),
        ],
    )

    metrics, findings = PedagogicalEvaluator.evaluate(journey)

    assert len(findings) >= 1
    assert any("advanced challenge stage appears before" in f.finding.lower() for f in findings)
    assert metrics[0].score <= 0.70
