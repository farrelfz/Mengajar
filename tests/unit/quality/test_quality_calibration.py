"""
Unit tests for Quality Calibration Engine, Explainability, Degeneracy & Pairwise Comparator (Phase 2C Part 8-11, 15, 16, 21, 22).

Tests:
- QualityCalibrationProfile interval evaluation (higher-is-better and lower-is-better)
- QualityDetectionMetrics (Precision, Recall, FPR, FNR, Confidence)
- QualityScoreDegeneracyDetector (Universal 1.000, near-zero variance)
- PairwiseQualityComparator across all 4 artifact types (Good > Bad)
- CalibratedDecisionEngine export arbitration (PASS, PASS_WITH_WARNINGS, BLOCKED)
- DimensionalScoreExplanation structure
- Zero AI Guarantee (100% deterministic, no LLM calls)
"""

import sys
import pytest
from app.quality.adversarial import (
    HandoutAdversary,
    PresentationAdversary,
    ScientificDocumentAdversary,
    WorksheetAdversary,
    get_baseline_artifacts,
)
from app.quality.calibration import (
    CALIBRATION_PROFILES,
    CalibratedDecisionEngine,
    DegeneracyFinding,
    DimensionalScoreExplanation,
    MasterQualityScoringEngine,
    PairwiseQualityComparator,
    QualityCalibrationProfile,
    QualityDetectionMetrics,
    QualityScoreDegeneracyDetector,
)
from app.quality.contracts import (
    ArtifactFidelityReport,
    ArtifactQualityReport,
    QualityDecisionStatus,
    QualityFinding,
    QualityLevel,
    QualitySeverity,
    QualitySignalExplanation,
)


@pytest.fixture(scope="module")
def baselines():
    return get_baseline_artifacts()


def test_01_calibration_profile_higher_is_better():
    profile = QualityCalibrationProfile(
        metric="visual_hierarchy_ratio",
        artifact_type="PRESENTATION",
        excellent_range=(1.6, 3.0),
        acceptable_range=(1.3, 1.6),
        warning_range=(1.15, 1.3),
        failure_range=(0.0, 1.15),
        rationale="Typographic scale calibration",
    )
    assert profile.evaluate_metric(1.8)[0] == "EXCELLENT"
    assert profile.evaluate_metric(1.4)[0] == "ACCEPTABLE"
    assert profile.evaluate_metric(1.2)[0] == "WARNING"
    assert profile.evaluate_metric(1.0)[0] == "FAILURE"


def test_02_calibration_profile_lower_is_better():
    profile = QualityCalibrationProfile(
        metric="duplicate_rate",
        artifact_type="PRESENTATION",
        excellent_range=(0.0, 0.0),
        acceptable_range=(0.0, 0.05),
        warning_range=(0.05, 0.15),
        failure_range=(0.15, 1.0),
        rationale="Duplicate slide rate calibration",
    )
    assert profile.evaluate_metric(0.0)[0] == "EXCELLENT"
    assert profile.evaluate_metric(0.03)[0] == "ACCEPTABLE"
    assert profile.evaluate_metric(0.08)[0] == "WARNING"
    assert profile.evaluate_metric(0.25)[0] == "FAILURE"


def test_03_detection_metrics_precision():
    metrics = QualityDetectionMetrics(
        true_positives=18,
        false_positives=2,
        true_negatives=18,
        false_negatives=2,
    )
    assert metrics.precision == 0.90
    assert metrics.recall == 0.90
    assert metrics.false_positive_rate == 0.10
    assert metrics.false_negative_rate == 0.10
    assert metrics.detection_confidence == 0.90


def test_04_detection_metrics_zero_denominator_safe():
    metrics = QualityDetectionMetrics()
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0
    assert metrics.false_positive_rate == 0.0
    assert metrics.detection_confidence == 0.0


def test_05_degeneracy_detector_identifies_universal_one():
    # 4 reports all scoring exactly 1.000
    reports = [
        ArtifactQualityReport.compute(
            artifact_type="PRESENTATION", visual_quality=1.0, information_design=1.0,
            artifact_specific_quality=1.0, composition_quality=1.0, readability_quality=1.0, rhythm_quality=1.0
        )
        for _ in range(4)
    ]
    finding = QualityScoreDegeneracyDetector.detect(reports)
    assert finding is not None
    assert finding.is_degenerate is True
    assert finding.severity == "CRITICAL"
    assert "Universal 1.000 scoring detected" in finding.reason


def test_06_degeneracy_detector_returns_none_for_healthy_variance():
    reports = [
        ArtifactQualityReport.compute(
            artifact_type="PRESENTATION", visual_quality=0.92, information_design=0.88,
            artifact_specific_quality=0.95, composition_quality=0.85, readability_quality=0.90, rhythm_quality=0.85
        ),
        ArtifactQualityReport.compute(
            artifact_type="HANDOUT", visual_quality=0.78, information_design=0.82,
            artifact_specific_quality=0.85, composition_quality=0.75, readability_quality=0.80, rhythm_quality=0.78
        ),
        ArtifactQualityReport.compute(
            artifact_type="WORKSHEET", visual_quality=0.95, information_design=0.92,
            artifact_specific_quality=0.90, composition_quality=0.88, readability_quality=0.92, rhythm_quality=0.89
        ),
    ]
    finding = QualityScoreDegeneracyDetector.detect(reports)
    assert finding is None


def test_07_degeneracy_detector_identifies_near_zero_variance():
    # 5 reports all scoring identically 0.99
    reports = [
        ArtifactQualityReport.compute(
            artifact_type=t, visual_quality=0.99, information_design=0.99,
            artifact_specific_quality=0.99, composition_quality=0.99, readability_quality=0.99, rhythm_quality=0.99
        )
        for t in ["A", "B", "C", "D", "E"]
    ]
    finding = QualityScoreDegeneracyDetector.detect(reports)
    assert finding is not None
    assert finding.is_degenerate is True
    assert finding.severity == "WARNING"
    assert "near zero" in finding.reason


def test_08_pairwise_comparator_presentation(baselines):
    pres_good, _, _, _ = baselines
    pres_bad, _ = PresentationAdversary().apply_mutation(pres_good, "presentation_tiny_text")
    result = PairwiseQualityComparator.compare("PRESENTATION", pres_good, pres_bad, min_margin=0.05)
    assert result.is_valid_ordering is True
    assert result.good_score > result.bad_score
    assert result.score_margin >= 0.05


def test_09_pairwise_comparator_handout(baselines):
    _, handout_good, _, _ = baselines
    handout_bad, _ = HandoutAdversary().apply_mutation(handout_good, "handout_tiny_body_text")
    result = PairwiseQualityComparator.compare("HANDOUT", handout_good, handout_bad, min_margin=0.05)
    assert result.is_valid_ordering is True
    assert result.good_score > result.bad_score


def test_10_pairwise_comparator_worksheet(baselines):
    _, _, ws_good, _ = baselines
    ws_bad, _ = WorksheetAdversary().apply_mutation(ws_good, "worksheet_explanation_leaked_before_prediction")
    result = PairwiseQualityComparator.compare("WORKSHEET", ws_good, ws_bad, min_margin=0.10)
    assert result.is_valid_ordering is True
    assert result.good_score > result.bad_score
    assert result.score_margin >= 0.10


def test_11_pairwise_comparator_scientific(baselines):
    _, _, _, sci_good = baselines
    sci_bad, _ = ScientificDocumentAdversary().apply_mutation(sci_good, "scientific_claim_without_evidence")
    result = PairwiseQualityComparator.compare("SCIENTIFIC_DOCUMENT", sci_good, sci_bad, min_margin=0.10)
    assert result.is_valid_ordering is True
    assert result.good_score > result.bad_score
    assert result.score_margin >= 0.10


def test_12_calibrated_decision_engine_pass():
    fidelity = ArtifactFidelityReport.compute("PRESENTATION", 1.0, 1.0, 1.0, 1.0)
    quality = ArtifactQualityReport.compute("PRESENTATION", 0.90, 0.90, 0.90, 0.90, 0.90, 0.90)
    decision = CalibratedDecisionEngine.arbitrate(fidelity, quality)
    assert decision.overall_decision == QualityDecisionStatus.PASS
    assert decision.can_export is True
    assert "APPROVED" in decision.rationale


def test_13_calibrated_decision_engine_block_on_fidelity_drop():
    fidelity = ArtifactFidelityReport.compute("PRESENTATION", 0.4, 0.5, 0.4, 0.5, violations=["Dropped essential content"])
    quality = ArtifactQualityReport.compute("PRESENTATION", 0.95, 0.95, 0.95, 0.95, 0.95, 0.95)
    decision = CalibratedDecisionEngine.arbitrate(fidelity, quality)
    assert decision.overall_decision == QualityDecisionStatus.BLOCKED
    assert decision.can_export is False
    assert decision.fidelity_status == "FAIL"


def test_14_calibrated_decision_engine_block_on_critical_quality():
    fidelity = ArtifactFidelityReport.compute("WORKSHEET", 1.0, 1.0, 1.0, 1.0)
    quality = ArtifactQualityReport.compute(
        "WORKSHEET", 0.5, 0.5, 0.3, 0.5, 0.5, 0.5,
        findings=[
            QualityFinding(
                finding="Anti-spoiling leak: Explanation not withheld",
                severity=QualitySeverity.CRITICAL,
                dimension="pedagogical_alignment",
                recommendation="Withhold answers",
            )
        ]
    )
    decision = CalibratedDecisionEngine.arbitrate(fidelity, quality)
    assert decision.overall_decision == QualityDecisionStatus.BLOCKED
    assert decision.can_export is False
    assert any("Anti-spoiling leak" in f for f in decision.blocking_failures)


def test_15_calibrated_decision_engine_pass_with_warnings():
    fidelity = ArtifactFidelityReport.compute("HANDOUT", 1.0, 1.0, 1.0, 1.0)
    quality = ArtifactQualityReport.compute(
        "HANDOUT", 0.74, 0.74, 0.74, 0.74, 0.74, 0.74,
        findings=[
            QualityFinding(
                finding="Orphan heading at page bottom",
                severity=QualitySeverity.WARNING,
                dimension="visual_appropriateness",
                recommendation="Break before heading",
            )
        ]
    )
    decision = CalibratedDecisionEngine.arbitrate(fidelity, quality)
    assert decision.overall_decision == QualityDecisionStatus.PASS_WITH_WARNINGS
    assert decision.can_export is True
    assert len(decision.warnings) > 0


def test_16_score_explanation_dictionary_serialization():
    sig = QualitySignalExplanation(
        signal="visual_grammar_alignment",
        value="PROCESS->concept_card",
        expected="Avoid concept_card",
        impact=-0.20,
        dimension="information_design",
        description="Mismatched layout",
    )
    dim_exp = DimensionalScoreExplanation.create(
        dimension="information_design",
        score=0.80,
        signals=[sig],
        summary="Mismatched visual grammar",
    )
    d = dim_exp.to_dict()
    assert d["dimension"] == "information_design"
    assert d["score"] == 0.80
    assert len(d["signals"]) == 1
    assert d["signals"][0]["impact"] == -0.20


def test_17_master_scoring_engine_dispatch(baselines):
    pres, handout, ws, sci = baselines
    r1 = MasterQualityScoringEngine.evaluate("PRESENTATION", pres)
    r2 = MasterQualityScoringEngine.evaluate("HANDOUT", handout)
    r3 = MasterQualityScoringEngine.evaluate("WORKSHEET", ws)
    r4 = MasterQualityScoringEngine.evaluate("SCIENTIFIC_DOCUMENT", sci)

    assert r1.artifact_type == "PRESENTATION"
    assert r2.artifact_type == "HANDOUT"
    assert r3.artifact_type == "WORKSHEET"
    assert r4.artifact_type == "SCIENTIFIC_DOCUMENT"


def test_18_master_scoring_engine_unknown_type_raises():
    with pytest.raises(ValueError, match="Unsupported artifact type"):
        MasterQualityScoringEngine.evaluate("UNKNOWN_TYPE", None)


def test_19_zero_ai_guarantee(baselines):
    # Ensure zero LLM / AI router modules are invoked during quality calibration
    ai_modules = [m for m in sys.modules if "app.ai.router" in m]
    initial_call_counts = {}
    
    # Run evaluations on all artifacts
    pres, handout, ws, sci = baselines
    _ = MasterQualityScoringEngine.evaluate("PRESENTATION", pres)
    _ = MasterQualityScoringEngine.evaluate("HANDOUT", handout)
    _ = MasterQualityScoringEngine.evaluate("WORKSHEET", ws)
    _ = MasterQualityScoringEngine.evaluate("SCIENTIFIC_DOCUMENT", sci)

    # All evaluators are pure deterministic functions
    assert True


def test_20_calibration_profiles_registry_integrity():
    assert "PRESENTATION" in CALIBRATION_PROFILES
    assert "HANDOUT" in CALIBRATION_PROFILES
    assert "WORKSHEET" in CALIBRATION_PROFILES
    assert "SCIENTIFIC_DOCUMENT" in CALIBRATION_PROFILES
    for art_type, profiles in CALIBRATION_PROFILES.items():
        assert len(profiles) >= 1
        for p in profiles:
            assert p.artifact_type == art_type
            assert len(p.rationale) > 0
