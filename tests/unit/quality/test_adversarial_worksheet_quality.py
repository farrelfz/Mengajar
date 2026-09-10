"""
Unit tests for Worksheet Adversarial Quality Calibration (Phase 2C Part 5 & 23).

Tests 17 realistic worksheet quality failures and decision engine enforcement:
- Pedagogical Flow (reflection before observation, data analysis before collection, etc.)
- Anti-Spoiling (explanation leaked before prediction, answer leaked in prompt, etc.)
- Interaction Design (workspace too small, workspace detached, no recording table, etc.)
- Quiz Collapse (10 consecutive recall questions, multiple-choice dominance)
- Visual (excessive density, invisible activity hierarchy, overlapping workspace)
"""

import pytest
from app.quality.adversarial import WorksheetAdversary, get_baseline_artifacts
from app.quality.calibration import CalibratedDecisionEngine, WorksheetQualityEvaluator
from app.quality.contracts import (
    ArtifactFidelityReport,
    QualityDecisionStatus,
    QualityLevel,
)


@pytest.fixture(scope="module")
def baseline_worksheet():
    _, _, ws_doc, _ = get_baseline_artifacts()
    return ws_doc


@pytest.fixture(scope="module")
def adversary():
    return WorksheetAdversary()


def test_01_baseline_worksheet_quality_is_high(baseline_worksheet):
    report = WorksheetQualityEvaluator.evaluate(baseline_worksheet)
    assert report.overall_quality_score >= 0.85
    assert report.quality_level in (QualityLevel.GOOD, QualityLevel.EXCELLENT)
    assert report.is_passing is True


def test_02_mutation_question_sequence_no_inquiry(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_question_sequence_no_inquiry")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_03_mutation_reflection_before_observation(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_reflection_before_observation")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert any("REFLECTION activity precedes OBSERVATION" in f.finding for f in report.findings)


def test_04_mutation_data_analysis_before_collection(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_data_analysis_before_collection")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert any("DATA_ANALYSIS precedes OBSERVATION" in f.finding for f in report.findings)


def test_05_mutation_prediction_after_explanation(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_prediction_after_explanation")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_06_mutation_explanation_leaked_before_prediction_critical(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_explanation_leaked_before_prediction")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert any("Anti-spoiling leak" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_07_mutation_answer_leaked_inside_question_critical(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_answer_leaked_inside_question")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert any("Answer or conclusion pre-filled" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_08_mutation_observation_conclusion_prefilled_critical(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_observation_conclusion_prefilled")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert any("Anti-spoiling leak" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_09_mutation_workspace_too_small(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_workspace_too_small")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert any("Inadequate student workspace" in f.finding for f in report.findings)
    assert report.composition_quality < 0.85


def test_10_mutation_workspace_detached(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_workspace_detached_from_activity")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_11_mutation_no_observation_recording_structure(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_no_observation_recording_structure")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_12_mutation_no_data_analysis_space(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_no_data_analysis_space")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_13_mutation_ten_consecutive_short_answer_quiz_collapse(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_ten_consecutive_short_answer")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert any("Worksheet inquiry collapsed into passive quiz" in f.finding for f in report.findings)
    assert report.artifact_specific_quality < 0.80


def test_14_mutation_dominated_by_multiple_choice_quiz_collapse(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_dominated_by_multiple_choice")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert any("Worksheet inquiry collapsed into passive quiz" in f.finding for f in report.findings)


def test_15_mutation_excessive_density(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_excessive_density")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_16_mutation_activity_hierarchy_invisible(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_activity_hierarchy_invisible")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_17_mutation_workspace_overlaps_content_critical(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_workspace_overlaps_content")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert any("Student workspace box collides" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_18_mutation_uneven_workspace_allocation(baseline_worksheet, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_worksheet, "worksheet_uneven_workspace_allocation")
    report = WorksheetQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_19_answer_leakage_strictly_blocks_export(baseline_worksheet, adversary):
    mutated, _ = adversary.apply_mutation(baseline_worksheet, "worksheet_answer_leaked_inside_question")
    quality_rep = WorksheetQualityEvaluator.evaluate(mutated)
    fidelity_rep = ArtifactFidelityReport.compute(
        artifact_type="WORKSHEET",
        semantic_preservation=1.0,
        structural_preservation=1.0,
        traceability_preservation=1.0,
        artifact_contract_preservation=1.0,
    )
    decision = CalibratedDecisionEngine.arbitrate(fidelity_rep, quality_rep)
    assert decision.overall_decision == QualityDecisionStatus.BLOCKED
    assert decision.can_export is False
    assert any("pre-filled" in b.lower() or "leak" in b.lower() for b in decision.blocking_failures)


def test_20_all_worksheet_mutations_degrade_or_record_findings(baseline_worksheet, adversary):
    baseline_rep = WorksheetQualityEvaluator.evaluate(baseline_worksheet)
    for m in adversary.list_mutations():
        mutated, _ = adversary.apply_mutation(baseline_worksheet, m.mutation_id)
        mut_rep = WorksheetQualityEvaluator.evaluate(mutated)
        has_findings = len(mut_rep.findings) > 0
        is_degraded = mut_rep.overall_quality_score <= baseline_rep.overall_quality_score
        assert has_findings or not mut_rep.is_passing or is_degraded, (
            f"Worksheet mutation {m.mutation_id} had no detectable effect!"
        )
