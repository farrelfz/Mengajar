"""
Unit tests for typed Quality contracts, models, and enums.
"""

import pytest
from app.quality.contracts import (
    EvaluationStage,
    EvaluationTrace,
    QualityDimension,
    QualityFinding,
    QualityGateDecision,
    QualityGateResult,
    QualityLevel,
    QualityMetric,
    QualityReport,
    QualityScore,
    QualitySeverity,
)


def test_quality_enums_and_bounds():
    assert QualityDimension.SEMANTIC_CORRECTNESS.value == "semantic_correctness"
    assert QualityDimension.PEDAGOGICAL_ALIGNMENT.value == "pedagogical_alignment"
    assert QualityDimension.STRUCTURAL_COHERENCE.value == "structural_coherence"
    assert QualityDimension.INFORMATION_DENSITY.value == "information_density"
    assert QualityDimension.FORMAT_INTEGRITY.value == "format_integrity"

    assert QualitySeverity.CRITICAL.value == "critical"
    assert QualitySeverity.ERROR.value == "error"
    assert QualitySeverity.WARNING.value == "warning"
    assert QualitySeverity.INFO.value == "info"

    assert QualityLevel.EXCELLENT.value == "excellent"
    assert QualityLevel.GOOD.value == "good"
    assert QualityLevel.ACCEPTABLE.value == "acceptable"
    assert QualityLevel.NEEDS_IMPROVEMENT.value == "needs_improvement"
    assert QualityLevel.POOR.value == "poor"
    assert QualityLevel.CRITICAL.value == "critical"

    assert EvaluationStage.BLUEPRINT.value == "blueprint"
    assert EvaluationStage.COMPOSITION.value == "composition"
    assert EvaluationStage.ARTIFACT.value == "artifact"


def test_quality_finding_and_metric_instantiation():
    finding = QualityFinding(
        dimension=QualityDimension.INFORMATION_DENSITY,
        severity=QualitySeverity.WARNING,
        finding="Test finding",
        evidence={"count": 5},
        score_impact=-0.1,
        recommendation="Reduce density",
        confidence=0.95,
    )
    assert finding.confidence == 0.95
    assert finding.severity == QualitySeverity.WARNING

    metric = QualityMetric(
        name="test_metric",
        dimension=QualityDimension.PEDAGOGICAL_ALIGNMENT,
        score=0.88,
        weight=1.5,
        raw_value=12,
    )
    assert metric.score == 0.88
    assert metric.weight == 1.5


def test_quality_score_and_report_serialization():
    score = QualityScore(
        overall_score=0.92,
        dimensional_scores={"semantic_correctness": 1.0, "density": 0.84},
        quality_level=QualityLevel.GOOD,
        is_passing=True,
    )
    gate = QualityGateResult(
        decision=QualityGateDecision.PASS_WITH_WARNINGS,
        score=score,
        can_proceed=True,
        gate_reasoning="Good quality with minor warnings.",
    )
    report = QualityReport(
        job_id="job_123",
        overall_score=0.92,
        quality_level=QualityLevel.GOOD,
        gate_result=gate,
        findings=[],
        metrics=[],
        trace=EvaluationTrace(score_computation_log=["Log line 1"]),
    )

    data = report.model_dump()
    assert data["job_id"] == "job_123"
    assert data["quality_level"] == "good"
    assert data["gate_result"]["decision"] == "pass_with_warnings"
