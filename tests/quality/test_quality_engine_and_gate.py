"""
Unit tests for QualityEvaluationEngine and QualityGate arbitration.
"""

import pytest

from app.quality.contracts import (
    QualityDimension,
    QualityFinding,
    QualityGateDecision,
    QualityScore,
    QualitySeverity,
)
from app.quality.engine import QualityEvaluationEngine


def test_quality_gate_fails_on_critical_finding():
    engine = QualityEvaluationEngine()
    score = QualityScore(overall_score=0.95, is_passing=True)
    findings = [
        QualityFinding(
            dimension=QualityDimension.FORMAT_INTEGRITY,
            severity=QualitySeverity.CRITICAL,
            finding="PDF generation corrupted.",
            recommendation="Fix renderer.",
        )
    ]

    gate = engine._arbitrate_quality_gate(score, findings)

    assert gate.decision == QualityGateDecision.FAIL
    assert gate.can_proceed is False
    assert len(gate.critical_findings) == 1


def test_quality_gate_triggers_needs_refinement_on_error():
    engine = QualityEvaluationEngine()
    score = QualityScore(overall_score=0.65, is_passing=False)
    findings = [
        QualityFinding(
            dimension=QualityDimension.PEDAGOGICAL_ALIGNMENT,
            severity=QualitySeverity.ERROR,
            finding="Worked example before concept.",
            recommendation="Reorder stages.",
        )
    ]

    gate = engine._arbitrate_quality_gate(score, findings)

    assert gate.decision == QualityGateDecision.NEEDS_REFINEMENT
    assert gate.can_proceed is False


def test_quality_gate_passes_with_warnings_on_minor_issue():
    engine = QualityEvaluationEngine()
    score = QualityScore(overall_score=0.82, is_passing=True)
    findings = [
        QualityFinding(
            dimension=QualityDimension.INFORMATION_DENSITY,
            severity=QualitySeverity.WARNING,
            finding="Slide slightly dense.",
            recommendation="Trim 10 words.",
        )
    ]

    gate = engine._arbitrate_quality_gate(score, findings)

    assert gate.decision == QualityGateDecision.PASS_WITH_WARNINGS
    assert gate.can_proceed is True
    assert len(gate.warnings) == 1
