"""
Unit tests for Presentation Adversarial Quality Calibration (Phase 2C Part 3 & 23).

Tests 20 realistic presentation quality failures:
- Duplication (exact, near, 5 consecutive identical, repeated generic card)
- Visual Hierarchy (headline/body ratio, visually equal, competing primary elements)
- Density (excessive density, extreme whitespace, >6 cards)
- Semantic Visual Mismatch (PROCESS as cards, COMPARISON as paragraph, etc.)
- Readability (tiny text, text clipping, overlapping content)
- Rhythm (same composition streak, high density streak, abrupt collapse)
"""

import pytest
from app.quality.adversarial import PresentationAdversary, get_baseline_artifacts
from app.quality.calibration import (
    FailureCategory,
    FailureSeverity,
    MasterQualityScoringEngine,
    PresentationQualityEvaluator,
)
from app.quality.contracts import QualityLevel


@pytest.fixture(scope="module")
def baseline_deck():
    deck, _, _, _ = get_baseline_artifacts()
    return deck


@pytest.fixture(scope="module")
def adversary():
    return PresentationAdversary()


def test_01_baseline_presentation_quality_is_high(baseline_deck):
    report = PresentationQualityEvaluator.evaluate(baseline_deck)
    assert report.overall_quality_score >= 0.85
    assert report.quality_level in (QualityLevel.GOOD, QualityLevel.EXCELLENT)
    assert report.is_passing is True


def test_02_mutation_exact_duplicate_slides(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_exact_duplicate_slides")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert report.rhythm_quality < 0.80
    assert any("Redundant/duplicate slides detected" in f.finding for f in report.findings)
    assert any(s.signal == "duplicate_slides_count" for s in report.signals)


def test_03_mutation_near_duplicate_composition(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_near_duplicate_composition")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert any("Redundant/duplicate slides" in f.finding for f in report.findings)


def test_04_mutation_five_consecutive_identical_layout(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_five_consecutive_identical_layout")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert any("Monotonous visual pacing" in f.finding for f in report.findings)


def test_05_mutation_repeated_generic_card(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_repeated_generic_card")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert any("Monotonous visual pacing" in f.finding for f in report.findings)


def test_06_mutation_headline_body_ratio_small(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_headline_body_ratio_small")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert any("Weak visual hierarchy ratio" in f.finding for f in report.findings)
    assert any(s.signal == "visual_hierarchy_ratio" for s in report.signals)


def test_07_mutation_all_text_visually_equal(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_all_text_visually_equal")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert any("Weak visual hierarchy ratio" in f.finding for f in report.findings)


def test_08_mutation_competing_primary_elements(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_competing_primary_elements")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert any("Multiple competing primary" in f.finding for f in report.findings)


def test_09_mutation_excessive_density(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_excessive_density")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert any("Excessive text density" in f.finding for f in report.findings)
    assert report.readability_quality < 0.80


def test_10_mutation_extreme_whitespace(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_extreme_whitespace")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score < 1.0


def test_11_mutation_more_than_six_cards(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_more_than_six_cards")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert any("Card overload" in f.finding for f in report.findings)


def test_12_mutation_process_as_cards(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_process_as_cards")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert report.information_design < 0.90
    assert any("Semantic-visual layout mismatch" in f.finding for f in report.findings)
    assert any(s.signal == "visual_grammar_alignment" for s in report.signals)


def test_13_mutation_comparison_as_paragraph(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_comparison_as_paragraph")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score < 1.0


def test_14_mutation_question_as_dense_explanation(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_question_as_dense_explanation")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score < 1.0


def test_15_mutation_cause_effect_unrelated(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_cause_effect_unrelated")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score < 1.0


def test_16_mutation_tiny_text_triggers_critical(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_tiny_text")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert any("Unreadable tiny text" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_17_mutation_text_clipping_triggers_critical(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_text_clipping")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert any("Text overflow" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_18_mutation_overlapping_content_triggers_critical(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_overlapping_content")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert any("Element collision" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_19_mutation_long_streak_high_density(baseline_deck, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_deck, "presentation_long_streak_high_density")
    report = PresentationQualityEvaluator.evaluate(mutated)
    assert any("High cognitive load streak" in f.finding for f in report.findings)


def test_20_all_presentation_mutations_degrade_quality_or_flag_issues(baseline_deck, adversary):
    baseline_rep = PresentationQualityEvaluator.evaluate(baseline_deck)
    for m in adversary.list_mutations():
        mutated, _ = adversary.apply_mutation(baseline_deck, m.mutation_id)
        mut_rep = PresentationQualityEvaluator.evaluate(mutated)
        # Every mutation must produce at least one finding or degrade quality or trigger non-passing
        has_findings = len(mut_rep.findings) > 0
        has_signals = len(mut_rep.signals) > 0
        is_degraded = mut_rep.overall_quality_score <= baseline_rep.overall_quality_score
        assert has_findings or has_signals or not mut_rep.is_passing or is_degraded, (
            f"Mutation {m.mutation_id} had no detectable effect on quality report!"
        )
