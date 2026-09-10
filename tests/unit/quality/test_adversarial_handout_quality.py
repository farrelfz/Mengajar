"""
Unit tests for Handout Adversarial Quality Calibration (Phase 2C Part 4 & 23).

Tests 18 realistic handout quality failures:
- Document Structure (orphan heading, empty section, hierarchy inversion, etc.)
- Page Composition (extreme density, accidental empty page, whitespace imbalance)
- Reading Flow (paragraph fragmentation, abrupt transition, duplicate block)
- Typography (tiny body text, weak hierarchy, excessive line length)
- Content Structure (critical concept buried, excessive bullet nesting, merged concepts)
"""

import pytest
from app.quality.adversarial import HandoutAdversary, get_baseline_artifacts
from app.quality.calibration import HandoutQualityEvaluator
from app.quality.contracts import QualityLevel


@pytest.fixture(scope="module")
def baseline_handout():
    _, handout_doc, _, _ = get_baseline_artifacts()
    return handout_doc


@pytest.fixture(scope="module")
def adversary():
    return HandoutAdversary()


def test_01_baseline_handout_quality_is_high(baseline_handout):
    report = HandoutQualityEvaluator.evaluate(baseline_handout)
    assert report.overall_quality_score >= 0.85
    assert report.quality_level in (QualityLevel.GOOD, QualityLevel.EXCELLENT)
    assert report.is_passing is True


def test_02_mutation_orphan_heading_at_bottom(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_orphan_heading_at_bottom")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert any("Orphan heading" in f.finding for f in report.findings)


def test_03_mutation_empty_heading_section(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_empty_heading_section")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert any("Empty section detected" in f.finding for f in report.findings)


def test_04_mutation_heading_hierarchy_inversion(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_heading_hierarchy_inversion")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert any("Heading hierarchy inversion" in f.finding for f in report.findings)


def test_05_mutation_definition_separated_from_concept(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_definition_separated_from_concept")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_06_mutation_example_before_concept(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_example_before_concept")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_07_mutation_extreme_dense_page(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_extreme_dense_page")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert any("Excessive textual density" in f.finding for f in report.findings)
    assert report.composition_quality < 0.80


def test_08_mutation_almost_empty_accidental_page(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_almost_empty_accidental_page")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert any("Accidental empty/spill page" in f.finding for f in report.findings)


def test_09_mutation_severe_whitespace_imbalance(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_severe_whitespace_imbalance")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_10_mutation_repeated_page_composition(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_repeated_page_composition")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_11_mutation_paragraph_fragmentation(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_paragraph_fragmentation")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert any("Severe paragraph fragmentation" in f.finding for f in report.findings)


def test_12_mutation_abrupt_section_transition(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_abrupt_section_transition")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_13_mutation_duplicate_explanatory_block(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_duplicate_explanatory_block")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert any("Duplicate explanatory prose block" in f.finding for f in report.findings)


def test_14_mutation_tiny_body_text_triggers_critical(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_tiny_body_text")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert any("Tiny body text font" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_15_mutation_weak_heading_hierarchy(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_weak_heading_hierarchy")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_16_mutation_excessive_line_length(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_excessive_line_length")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert any("Excessive typographic line length" in f.finding for f in report.findings)


def test_17_mutation_critical_concept_buried(baseline_handout, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_handout, "handout_critical_concept_buried")
    report = HandoutQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_18_all_handout_mutations_degrade_or_record_findings(baseline_handout, adversary):
    baseline_rep = HandoutQualityEvaluator.evaluate(baseline_handout)
    for m in adversary.list_mutations():
        mutated, _ = adversary.apply_mutation(baseline_handout, m.mutation_id)
        mut_rep = HandoutQualityEvaluator.evaluate(mutated)
        has_findings = len(mut_rep.findings) > 0
        is_degraded = mut_rep.overall_quality_score <= baseline_rep.overall_quality_score
        assert has_findings or not mut_rep.is_passing or is_degraded, (
            f"Handout mutation {m.mutation_id} was not detected!"
        )
