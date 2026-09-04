"""
Unit tests for PedagogicalEvaluator and FormatEvaluator.
"""

from pathlib import Path
import pytest

from app.director.contracts import (
    LearningJourney,
    LearningStage,
    LearningStageType,
    MaterialStrategyType,
)
from app.quality.contracts import QualityDimension, QualitySeverity
from app.quality.format_evaluator import FormatEvaluator
from app.quality.pedagogical_evaluator import PedagogicalEvaluator


def test_pedagogical_evaluator_flags_worked_example_before_formalization():
    # Intentionally malformed pedagogical sequence: Worked Example BEFORE Concept Formalization
    journey = LearningJourney(
        journey_id="j_bad_sequence",
        strategy=MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
        stages=[
            LearningStage(
                stage_type=LearningStageType.WORKED_EXAMPLE,
                title="Step-by-Step Calculation",
                purpose="Practice before concept",
            ),
            LearningStage(
                stage_type=LearningStageType.CONCEPT_FORMALIZATION,
                title="Torque Definition",
                purpose="Late definition",
            ),
        ],
    )

    metrics, findings = PedagogicalEvaluator.evaluate(journey)

    assert len(findings) >= 1
    assert any(f.dimension == QualityDimension.PEDAGOGICAL_ALIGNMENT for f in findings)
    assert any("before concept formalization" in f.finding.lower() for f in findings)
    assert metrics[0].score < 1.0


def test_format_evaluator_flags_missing_file(tmp_path: Path):
    non_existent = tmp_path / "does_not_exist.pdf"
    metrics, findings = FormatEvaluator.evaluate(non_existent, target_format="a4_portrait")

    assert len(findings) == 1
    assert findings[0].severity == QualitySeverity.CRITICAL
    assert findings[0].dimension == QualityDimension.FORMAT_INTEGRITY
    assert metrics[0].score == 0.0
