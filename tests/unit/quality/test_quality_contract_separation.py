"""
Unit tests for Quality vs Fidelity Contract Separation (Phase 2C Part 1).

Verifies:
1. ArtifactFidelityReport and ArtifactQualityReport remain strictly separate.
2. High fidelity does NOT automatically imply high quality.
3. High quality does NOT hide semantic corruption.
4. CalibratedQualityDecision properly arbitrates export status.
"""

import pytest
from app.quality.contracts import (
    ArtifactFidelityReport,
    ArtifactQualityReport,
    CalibratedQualityDecision,
    QualityDecisionStatus,
    QualityFinding,
    QualityLevel,
    QualitySeverity,
    QualitySignalExplanation,
)


def test_01_fidelity_report_contract_fields():
    report = ArtifactFidelityReport.compute(
        artifact_type="PRESENTATION",
        semantic_preservation=1.0,
        structural_preservation=1.0,
        traceability_preservation=1.0,
        artifact_contract_preservation=1.0,
        execution_reliability=1.0,
    )
    assert report.artifact_type == "PRESENTATION"
    assert report.overall_fidelity_score == 1.0
    assert report.is_passing is True
    assert len(report.violations) == 0


def test_02_fidelity_report_dropped_elements_reduces_score():
    report = ArtifactFidelityReport.compute(
        artifact_type="HANDOUT",
        semantic_preservation=0.6,
        structural_preservation=1.0,
        traceability_preservation=0.7,
        artifact_contract_preservation=0.8,
        violations=["Dropped 4 blueprint elements"],
    )
    assert report.semantic_preservation == 0.6
    assert report.overall_fidelity_score < 0.85
    assert report.is_passing is False
    assert "Dropped 4 blueprint elements" in report.violations


def test_03_quality_report_contract_fields():
    report = ArtifactQualityReport.compute(
        artifact_type="WORKSHEET",
        visual_quality=0.9,
        information_design=0.85,
        artifact_specific_quality=0.95,
        composition_quality=0.88,
        readability_quality=0.92,
        rhythm_quality=0.80,
    )
    assert report.artifact_type == "WORKSHEET"
    assert 0.85 <= report.overall_quality_score <= 0.95
    assert report.quality_level in (QualityLevel.GOOD, QualityLevel.EXCELLENT)
    assert report.is_passing is True
    assert "visual_quality" in report.dimensional_scores


def test_04_quality_report_low_design_fails():
    report = ArtifactQualityReport.compute(
        artifact_type="PRESENTATION",
        visual_quality=0.4,
        information_design=0.3,
        artifact_specific_quality=0.5,
        composition_quality=0.4,
        readability_quality=0.3,
        rhythm_quality=0.3,
        findings=[
            QualityFinding(
                finding="Catastrophic text overflow on slide 2",
                severity=QualitySeverity.CRITICAL,
                dimension="visual_appropriateness",
                recommendation="Reduce font size",
            )
        ],
    )
    assert report.overall_quality_score < 0.60
    assert report.quality_level == QualityLevel.POOR or report.quality_level == QualityLevel.CRITICAL
    assert report.is_passing is False


def test_05_arbitrate_high_fidelity_high_quality_passes():
    fidelity = ArtifactFidelityReport.compute(
        artifact_type="PRESENTATION",
        semantic_preservation=1.0,
        structural_preservation=1.0,
        traceability_preservation=1.0,
        artifact_contract_preservation=1.0,
    )
    quality = ArtifactQualityReport.compute(
        artifact_type="PRESENTATION",
        visual_quality=0.90,
        information_design=0.90,
        artifact_specific_quality=0.95,
        composition_quality=0.85,
        readability_quality=0.92,
        rhythm_quality=0.88,
    )
    decision = CalibratedQualityDecision.arbitrate(fidelity, quality)
    assert decision.overall_decision == QualityDecisionStatus.PASS
    assert decision.can_export is True
    assert decision.fidelity_status == "PASS"
    assert decision.quality_status == "PASS"


def test_06_arbitrate_high_fidelity_low_quality_blocks():
    # Semantic preserved 100%, but visual design is broken
    fidelity = ArtifactFidelityReport.compute(
        artifact_type="HANDOUT",
        semantic_preservation=1.0,
        structural_preservation=1.0,
        traceability_preservation=1.0,
        artifact_contract_preservation=1.0,
    )
    quality = ArtifactQualityReport.compute(
        artifact_type="HANDOUT",
        visual_quality=0.3,
        information_design=0.3,
        artifact_specific_quality=0.4,
        composition_quality=0.3,
        readability_quality=0.2,
        rhythm_quality=0.3,
        findings=[
            QualityFinding(
                finding="Tiny unreadable font (5pt) in body text",
                severity=QualitySeverity.CRITICAL,
                dimension="format_integrity",
                recommendation="Increase font",
            )
        ],
    )
    decision = CalibratedQualityDecision.arbitrate(fidelity, quality)
    assert decision.overall_decision == QualityDecisionStatus.BLOCKED
    assert decision.can_export is False
    assert decision.fidelity_status == "PASS"
    assert decision.quality_status == "BLOCKED"
    assert any("Tiny unreadable font" in f for f in decision.blocking_failures)


def test_07_arbitrate_low_fidelity_high_quality_blocks():
    # Looks gorgeous, but dropped source content (Semantic Corruption)
    fidelity = ArtifactFidelityReport.compute(
        artifact_type="SCIENTIFIC_DOCUMENT",
        semantic_preservation=0.4,
        structural_preservation=0.5,
        traceability_preservation=0.4,
        artifact_contract_preservation=0.5,
        violations=["Dropped 12 essential empirical claims from source"],
    )
    quality = ArtifactQualityReport.compute(
        artifact_type="SCIENTIFIC_DOCUMENT",
        visual_quality=0.98,
        information_design=0.95,
        artifact_specific_quality=0.96,
        composition_quality=0.95,
        readability_quality=0.95,
        rhythm_quality=0.95,
    )
    decision = CalibratedQualityDecision.arbitrate(fidelity, quality)
    # CRITICAL: High quality MUST NOT hide semantic corruption
    assert decision.overall_decision == QualityDecisionStatus.BLOCKED
    assert decision.can_export is False
    assert decision.fidelity_status == "FAIL"
    assert any("Dropped 12 essential empirical claims" in f for f in decision.blocking_failures)


def test_08_arbitrate_high_fidelity_moderate_quality_warns():
    fidelity = ArtifactFidelityReport.compute(
        artifact_type="WORKSHEET",
        semantic_preservation=1.0,
        structural_preservation=1.0,
        traceability_preservation=1.0,
        artifact_contract_preservation=1.0,
    )
    quality = ArtifactQualityReport.compute(
        artifact_type="WORKSHEET",
        visual_quality=0.72,
        information_design=0.70,
        artifact_specific_quality=0.74,
        composition_quality=0.70,
        readability_quality=0.75,
        rhythm_quality=0.70,
        findings=[
            QualityFinding(
                finding="Workspace box is slightly constrained (45pt)",
                severity=QualitySeverity.WARNING,
                dimension="pedagogical_alignment",
                recommendation="Expand workspace",
            )
        ],
    )
    decision = CalibratedQualityDecision.arbitrate(fidelity, quality)
    assert decision.overall_decision == QualityDecisionStatus.PASS_WITH_WARNINGS
    assert decision.can_export is True
    assert len(decision.warnings) > 0


def test_09_reports_are_immutable_and_serializable():
    fidelity = ArtifactFidelityReport.compute(
        artifact_type="PRESENTATION",
        semantic_preservation=1.0,
        structural_preservation=1.0,
        traceability_preservation=1.0,
        artifact_contract_preservation=1.0,
    )
    with pytest.raises(Exception):
        fidelity.overall_fidelity_score = 0.5  # Frozen model cannot be mutated


def test_10_quality_signal_explanation_structure():
    signal = QualitySignalExplanation(
        signal="headline_body_ratio",
        value=1.2,
        expected=">= 1.8",
        impact=-0.15,
        dimension="visual_hierarchy",
        description="Headline is barely larger than body text",
    )
    assert signal.signal == "headline_body_ratio"
    assert signal.impact == -0.15
    assert signal.dimension == "visual_hierarchy"


def test_11_quality_levels_grading():
    def get_level(score):
        rep = ArtifactQualityReport.compute(
            artifact_type="HANDOUT",
            visual_quality=score,
            information_design=score,
            artifact_specific_quality=score,
            composition_quality=score,
            readability_quality=score,
            rhythm_quality=score,
        )
        return rep.quality_level

    assert get_level(0.96) == QualityLevel.EXCELLENT
    assert get_level(0.88) == QualityLevel.GOOD
    assert get_level(0.78) == QualityLevel.ACCEPTABLE
    assert get_level(0.65) == QualityLevel.NEEDS_IMPROVEMENT
    assert get_level(0.45) == QualityLevel.POOR
    assert get_level(0.30) == QualityLevel.CRITICAL
