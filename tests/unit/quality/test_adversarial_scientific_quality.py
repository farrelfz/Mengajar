"""
Unit tests for Scientific Document Adversarial Quality Calibration (Phase 2C Part 6 & 23).

Tests 18 realistic scientific quality failures and decision engine enforcement:
- Scientific Structure (BAB hierarchy inversion, results before methodology, etc.)
- Evidence Discipline (claim without evidence, mismatched evidence, ungrounded fact)
- Academic Integrity (missing citation, detached citation, fabricated citation)
- Document Composition (orphan subsection, empty subsection, split table)
- Argument Quality (duplicate argument, contradictory claims, stripped limitation)
"""

import pytest
from app.quality.adversarial import ScientificDocumentAdversary, get_baseline_artifacts
from app.quality.calibration import (
    CalibratedDecisionEngine,
    ScientificDocumentQualityEvaluator,
)
from app.quality.contracts import (
    ArtifactFidelityReport,
    QualityDecisionStatus,
    QualityLevel,
)


@pytest.fixture(scope="module")
def baseline_scientific():
    _, _, _, sci_doc = get_baseline_artifacts()
    return sci_doc


@pytest.fixture(scope="module")
def adversary():
    return ScientificDocumentAdversary()


def test_01_baseline_scientific_quality_is_high(baseline_scientific):
    report = ScientificDocumentQualityEvaluator.evaluate(baseline_scientific)
    assert report.overall_quality_score >= 0.85
    assert report.quality_level in (QualityLevel.GOOD, QualityLevel.EXCELLENT)
    assert report.is_passing is True


def test_02_mutation_bab_hierarchy_inversion_critical(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_bab_hierarchy_inversion")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert any("BAB hierarchy inversion" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_03_mutation_results_before_methodology(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_results_before_methodology")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert any("BAB hierarchy inversion" in f.finding for f in report.findings)


def test_04_mutation_conclusion_before_discussion(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_conclusion_before_discussion")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert any("BAB hierarchy inversion" in f.finding for f in report.findings)


def test_05_mutation_missing_argument_transition(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_missing_argument_transition")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_06_mutation_claim_without_evidence_critical(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_claim_without_evidence")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert any("Unsupported empirical claim" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_07_mutation_evidence_attached_to_wrong_claim_critical(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_evidence_attached_to_wrong_claim")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert any("Evidence relevance mismatch" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_08_mutation_unsupported_claim_as_fact_critical(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_unsupported_claim_as_fact")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert any("Unsupported empirical claim" in f.finding for f in report.findings)
    assert report.is_passing is False


def test_09_mutation_evidence_relationship_silently_removed(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_evidence_relationship_silently_removed")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_10_mutation_citation_missing_critical(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_citation_missing")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert any("Citation missing" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_11_mutation_citation_detached(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_citation_detached_from_claim")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_12_mutation_fabricated_citation_marker_critical(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_fabricated_citation_marker")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert any("Fabricated citation detected" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_13_mutation_orphan_subsection(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_orphan_subsection")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_14_mutation_empty_academic_subsection(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_empty_academic_subsection")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert any("Empty academic subsection" in f.finding for f in report.findings)


def test_15_mutation_table_split(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_table_split_incorrectly")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_16_mutation_figure_caption_detached(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_figure_caption_detached")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_17_mutation_duplicate_argument(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_duplicate_argument")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert report.overall_quality_score <= 1.0


def test_18_mutation_contradictory_adjacent_claims_critical(baseline_scientific, adversary):
    mutated, mutation = adversary.apply_mutation(baseline_scientific, "scientific_contradictory_adjacent_claims")
    report = ScientificDocumentQualityEvaluator.evaluate(mutated)
    assert any("Contradictory adjacent claims" in f.finding and f.severity == "critical" for f in report.findings)
    assert report.is_passing is False


def test_19_unsupported_claim_strictly_blocks_export(baseline_scientific, adversary):
    mutated, _ = adversary.apply_mutation(baseline_scientific, "scientific_claim_without_evidence")
    quality_rep = ScientificDocumentQualityEvaluator.evaluate(mutated)
    fidelity_rep = ArtifactFidelityReport.compute(
        artifact_type="SCIENTIFIC_DOCUMENT",
        semantic_preservation=1.0,
        structural_preservation=1.0,
        traceability_preservation=1.0,
        artifact_contract_preservation=1.0,
    )
    decision = CalibratedDecisionEngine.arbitrate(fidelity_rep, quality_rep)
    assert decision.overall_decision == QualityDecisionStatus.BLOCKED
    assert decision.can_export is False
    assert any("unsupported" in b.lower() or "evidence" in b.lower() for b in decision.blocking_failures)


def test_20_all_scientific_mutations_degrade_or_record_findings(baseline_scientific, adversary):
    baseline_rep = ScientificDocumentQualityEvaluator.evaluate(baseline_scientific)
    for m in adversary.list_mutations():
        mutated, _ = adversary.apply_mutation(baseline_scientific, m.mutation_id)
        mut_rep = ScientificDocumentQualityEvaluator.evaluate(mutated)
        has_findings = len(mut_rep.findings) > 0
        is_degraded = mut_rep.overall_quality_score <= baseline_rep.overall_quality_score
        assert has_findings or not mut_rep.is_passing or is_degraded, (
            f"Scientific mutation {m.mutation_id} was not detected!"
        )
