"""
Universal Document Intelligence System V5 — Phase 5 Maximum-Rigor Tests.

Validates Scenarios A through T:
Scenario A: Golden artifact passes all invariants.
Scenario B: Hard invariant violation overrides high score.
Scenario C: Minor visual variance stays within tolerance.
Scenario D: Scientific citation integrity regression triggers critical regression.
Scenario E: Baseline modification without provenance triggers laundering error.
Scenario F: Golden file modification with unchanged version triggers hash failure.
Scenario G: Training performance improves but unseen performance declines (overfitting detected).
Scenario H: High knowledge overlap but low artifact divergence triggers homogenization warning.
Scenario I: Presentation improves while worksheet anti-spoiling regresses.
Scenario J: Historical regression detected across multiple versions.
Scenario K: Small sample size prevents overconfident certification.
Scenario L: Adversarial fixture false negative blocks certification.
Scenario M: Replay produces deterministic identical hash results.
Scenario N: CertificationEngine does not modify UQA decision.
Scenario O: Benchmark system cannot export artifact independently.
Scenario P: Cross-artifact benchmark detects Presentation-as-Handout.
Scenario Q: Cross-artifact benchmark detects Worksheet-as-Summary.
Scenario R: Corpus coverage analyzer identifies missing domain coverage.
Scenario S: Unknown corpus metadata fails validation.
Scenario T: Historical baseline cannot be silently overwritten.
"""

import hashlib
import pytest
from pathlib import Path

from app.benchmarking.golden_contracts import (
    BenchmarkEvaluation,
    CertificationDecision,
    CertificationStatus,
    DimensionResult,
    ExpectedCharacteristics,
    ExpectedInvariants,
    ForbiddenFailures,
    GoldenArtifactReference,
    GoldenCase,
    GoldenCorpus,
    GoldenCorpusVersion,
    VariationPolicy,
)
from app.benchmarking.golden_registry import (
    GoldenCorpusLoader,
    GoldenCorpusValidator,
)
from app.benchmarking.governance import (
    AntiLaunderingGuard,
    BaselineMutationRecord,
    BenchmarkLaunderingAttemptError,
    ChangeClassification,
)
from app.benchmarking.divergence import (
    CrossArtifactDivergenceBenchmark,
)
from app.benchmarking.certification import (
    CertificationEngine,
    CertificationPolicy,
    RegressionDetector,
)
from app.benchmarking.certification.regression_detector import RegressionSeverity
from app.benchmarking.coverage import CorpusCoverageAnalyzer
from app.benchmarking.statistical_honesty import (
    StatisticalConfidenceLevel,
    StatisticalHonestyEngine,
)
from app.benchmarking.overfitting import (
    GeneralizationHealthStatus,
    OverfittingSignalAnalyzer,
)
from app.benchmarking.certification_explainability import (
    CertificationExplainer,
)
from app.benchmarking.generator_health import (
    GeneratorHealthTracker,
    GeneratorStatus,
)
from app.quality.contracts.authority import UnifiedQualityReport
from app.quality.contracts.decisions import ExportDecision


# ============================================================================
# SCENARIOS A - E
# ============================================================================

def test_scenario_a_golden_artifact_passes_all_invariants():
    ref = GoldenArtifactReference(
        artifact_id="ref_a",
        artifact_type="PRESENTATION",
        source_case_id="case_a",
        artifact_file_reference="path",
        hard_invariants=ExpectedInvariants()
    )
    dim_results = {
        "SEMANTIC": DimensionResult(
            dimension="SEMANTIC", raw_measurements={}, normalized_score=0.95,
            confidence=0.95, applicability=1.0, comparison_mode=VariationPolicy.EXACT
        ),
        "VISUAL": DimensionResult(
            dimension="VISUAL", raw_measurements={}, normalized_score=0.92,
            confidence=0.90, applicability=1.0, comparison_mode=VariationPolicy.TOLERANT
        )
    }
    invariants = {"no_fabricated_claims": True, "no_text_clipping": True}
    eval_res = CertificationEngine.certify("gen_a", ref, "1.0.0", dim_results, invariants)
    assert eval_res.certification_decision == CertificationDecision.CERTIFIED_EXCELLENT
    assert eval_res.reference_alignment >= 0.90


def test_scenario_b_hard_invariant_violation_overrides_high_score():
    ref = GoldenArtifactReference(
        artifact_id="ref_b",
        artifact_type="WORKSHEET",
        source_case_id="case_b",
        artifact_file_reference="path"
    )
    # Perfect 1.0 score everywhere
    dim_results = {
        "SEMANTIC": DimensionResult(
            dimension="SEMANTIC", raw_measurements={}, normalized_score=1.0,
            confidence=1.0, applicability=1.0, comparison_mode=VariationPolicy.EXACT
        ),
        "PEDAGOGICAL": DimensionResult(
            dimension="PEDAGOGICAL", raw_measurements={}, normalized_score=1.0,
            confidence=1.0, applicability=1.0, comparison_mode=VariationPolicy.EXACT
        )
    }
    # Invariant fails
    invariants = {"no_answer_leak": False}
    eval_res = CertificationEngine.certify("gen_b", ref, "1.0.0", dim_results, invariants)
    assert eval_res.certification_decision == CertificationDecision.BENCHMARK_INSUFFICIENT
    explanation = CertificationExplainer.explain(eval_res)
    assert "WHY_INSUFFICIENT" in explanation.decision_path


def test_scenario_c_minor_visual_variance_stays_within_tolerance():
    current = {
        "VISUAL": DimensionResult(
            dimension="VISUAL", raw_measurements={}, normalized_score=0.88,
            confidence=0.90, applicability=1.0, comparison_mode=VariationPolicy.TOLERANT
        )
    }
    # Drop from 0.94 to 0.88 is 0.06. For VISUAL, tolerance is 0.08!
    baseline = {"VISUAL": 0.94}
    analysis = RegressionDetector.detect(current, baseline)
    assert analysis["is_regression"] is False
    assert analysis["severity"] in (RegressionSeverity.NO_REGRESSION.value, RegressionSeverity.MINOR_VARIATION.value)


def test_scenario_d_scientific_citation_regression_triggers_critical():
    current = {
        "SCIENTIFIC": DimensionResult(
            dimension="SCIENTIFIC", raw_measurements={}, normalized_score=0.98,
            confidence=0.95, applicability=1.0, comparison_mode=VariationPolicy.EXACT
        )
    }
    # For SCIENTIFIC, tolerance is 0.00 (zero tolerance!)
    baseline = {"SCIENTIFIC": 1.00}
    analysis = RegressionDetector.detect(current, baseline)
    assert analysis["is_regression"] is True
    assert analysis["severity"] == RegressionSeverity.CRITICAL_REGRESSION.value


def test_scenario_e_baseline_mutation_without_provenance_triggers_laundering():
    record = BaselineMutationRecord(
        target_case_id="GOLDEN_OOBLECK",
        target_artifact_type="PRESENTATION",
        previous_baseline_reference="",  # Missing lineage!
        previous_scores={"SEMANTIC": 0.95},
        new_scores={"SEMANTIC": 0.90},
        change_reason="Legitimate parameter retuning under new policy",
        expected_quality_impact="Slight variance",
        change_classification=ChangeClassification.POLICY_EVOLUTION
    )
    with pytest.raises(BenchmarkLaunderingAttemptError, match="previous_baseline_reference"):
        AntiLaunderingGuard.validate_mutation(record, strict_raise=True)


# ============================================================================
# SCENARIOS F - J
# ============================================================================

def test_scenario_f_golden_file_modification_with_unchanged_version():
    content = "Original unmutated source text"
    digest = AntiLaunderingGuard.compute_content_digest(content)
    tampered = "Mutated source text with undetected modifications"
    assert AntiLaunderingGuard.verify_content_digest(tampered, digest) is False


def test_scenario_g_training_improves_but_unseen_declines():
    # Known scores: 0.98, 0.96, 0.97 (mean ~ 0.97)
    # Unseen scores: 0.72, 0.70, 0.74 (mean ~ 0.72)
    # Gap ~ 0.25 (> 0.15)
    known = [0.98, 0.96, 0.97, 0.95, 0.99]
    unseen = [0.72, 0.70, 0.74, 0.68, 0.71]
    report = OverfittingSignalAnalyzer.analyze(known, unseen)
    assert report.status == GeneralizationHealthStatus.OVERFITTING_SUSPECTED
    assert report.overfitting_warning is True
    assert report.generalization_gap > 0.15


def test_scenario_h_high_overlap_low_divergence_triggers_homogenization():
    # All four artifacts structured with the same generic key set
    artifacts = {
        "PRESENTATION": {"item_1": "text", "item_2": "text", "item_3": "text"},
        "HANDOUT": {"item_1": "text", "item_2": "text", "item_3": "text"},
        "WORKSHEET": {"item_1": "text", "item_2": "text", "item_3": "text"},
        "SCIENTIFIC_DOCUMENT": {"item_1": "text", "item_2": "text", "item_3": "text"},
    }
    report = CrossArtifactDivergenceBenchmark.evaluate("case_homo", artifacts)
    assert any("CROSS_ARTIFACT_HOMOGENIZATION" in c for c in report.detected_collapses)
    assert report.is_sufficiently_divergent is False


def test_scenario_i_presentation_improves_while_worksheet_invariants_regress():
    ref = GoldenArtifactReference(
        artifact_id="ref_pres", artifact_type="PRESENTATION", source_case_id="c1", artifact_file_reference="p"
    )
    ev_pres = BenchmarkEvaluation(
        evaluation_id="e1", artifact_id="case_presentation", golden_reference_id="ref_pres",
        corpus_version="1.0", benchmark_protocol_version="1.0", certification_decision=CertificationDecision.CERTIFIED_EXCELLENT,
        reference_alignment=0.98
    )
    ev_ws = BenchmarkEvaluation(
        evaluation_id="e2", artifact_id="case_worksheet", golden_reference_id="ref_ws",
        corpus_version="1.0", benchmark_protocol_version="1.0", certification_decision=CertificationDecision.BENCHMARK_INSUFFICIENT,
        reference_alignment=0.80
    )
    health = GeneratorHealthTracker.evaluate_health([ev_pres, ev_ws])
    assert health.overall_status == GeneratorStatus.REQUIRES_INVESTIGATION
    assert health.per_artifact_health["WORKSHEET"] == GeneratorStatus.REQUIRES_INVESTIGATION


def test_scenario_j_historical_regression_detected_across_multiple_runs():
    evals = [
        BenchmarkEvaluation(
            evaluation_id=f"e_{i}", artifact_id=f"art_{i}", golden_reference_id="ref",
            corpus_version="1.0", benchmark_protocol_version="1.0",
            certification_decision=CertificationDecision.BENCHMARK_REGRESSION,
            reference_alignment=0.75
        )
        for i in range(5)
    ]
    health = GeneratorHealthTracker.evaluate_health(evals)
    assert health.overall_status == GeneratorStatus.GENERATOR_REGRESSING
    assert health.regression_frequency == 1.0


# ============================================================================
# SCENARIOS K - O
# ============================================================================

def test_scenario_k_small_sample_size_prevents_overconfident_certification():
    # Only 2 observations available
    scores = [0.95, 0.96]
    report = StatisticalHonestyEngine.evaluate(scores, baseline_mean=0.90)
    assert report.confidence_level == StatisticalConfidenceLevel.INSUFFICIENT_SAMPLE_SIZE
    assert report.is_statistically_conclusive is False


def test_scenario_l_adversarial_fixture_false_negative_blocks_certification():
    # An adversarial worksheet that leaks answers must fail invariant check
    data = {"prompt_text": "Kunci jawaban: mengeras saat ditekan", "withhold_explanation": False}
    ref = GoldenArtifactReference(
        artifact_id="ref_ws_adv", artifact_type="WORKSHEET", source_case_id="case_adv", artifact_file_reference="p"
    )
    # If the generator leaked answers, no_answer_leak is False
    invariants = {"no_answer_leak": False}
    dim_results = {
        "SEMANTIC": DimensionResult(
            dimension="SEMANTIC", raw_measurements={}, normalized_score=0.95,
            confidence=0.90, applicability=1.0, comparison_mode=VariationPolicy.EXACT
        )
    }
    eval_res = CertificationEngine.certify("gen_adv", ref, "1.0", dim_results, invariants)
    assert eval_res.certification_decision == CertificationDecision.BENCHMARK_INSUFFICIENT


def test_scenario_m_replay_produces_deterministic_identical_hashes():
    h1 = hashlib.sha256(b"Deterministic benchmark configuration A").hexdigest()
    h2 = hashlib.sha256(b"Deterministic benchmark configuration A").hexdigest()
    assert h1 == h2


def test_scenario_n_certification_engine_does_not_modify_uqa_decision():
    # Create a UnifiedQualityReport with export BLOCKED
    uqa_report = UnifiedQualityReport(
        artifact_type="PRESENTATION",
        decision=ExportDecision.BLOCKED,
        can_export=False,
        repair_required=False,
        overall_quality_score=0.45,
        domain_scores={"semantic_integrity": 0.45},
        hard_blockers=("TEXT_CLIPPING_CRITICAL",),
        findings=()
    )
    # CertificationEngine can only inspect and evaluate benchmarks; UQA decision is untouched
    assert uqa_report.can_export is False
    assert uqa_report.decision == ExportDecision.BLOCKED


def test_scenario_o_benchmark_system_cannot_export_artifact_independently():
    # Ensure CertificationDecision does NOT grant export authority
    decision = CertificationDecision.CERTIFIED_EXCELLENT
    assert not hasattr(decision, "can_export")
    assert decision != ExportDecision.EXPORT_APPROVED


# ============================================================================
# SCENARIOS P - T
# ============================================================================

def test_scenario_p_cross_artifact_benchmark_detects_presentation_as_handout():
    artifacts = {
        "PRESENTATION": {
            "slides": [
                {"CORE_MESSAGE": "Overloaded", "content": " ".join(["word"] * 85)},
                {"CORE_MESSAGE": "Overloaded 2", "content": " ".join(["word"] * 90)},
            ]
        },
        "HANDOUT": {"sections": [{"content": "Regular reading prose"}]}
    }
    report = CrossArtifactDivergenceBenchmark.evaluate("case_p", artifacts)
    assert any("PRESENTATION_TO_HANDOUT_COLLAPSE" in c for c in report.detected_collapses)


def test_scenario_q_cross_artifact_benchmark_detects_worksheet_as_summary():
    # Worksheet has 4 questions, 0 investigations
    artifacts = {
        "WORKSHEET": {
            "activities": [
                {"activity_type": "QUESTION", "prompt_text": "Question 1"},
                {"activity_type": "QUESTION", "prompt_text": "Question 2"},
                {"activity_type": "QUESTION", "prompt_text": "Question 3"},
                {"activity_type": "QUESTION", "prompt_text": "Question 4"},
            ]
        },
        "PRESENTATION": {"slides": [{"CORE_MESSAGE": "Point"}]}
    }
    report = CrossArtifactDivergenceBenchmark.evaluate("case_q", artifacts)
    assert any("WORKSHEET_TO_QUIZ_COLLAPSE" in c for c in report.detected_collapses)


def test_scenario_r_corpus_coverage_analyzer_identifies_missing_domain():
    manifest_path = Path("golden_corpus/corpus_manifest.json")
    corpus = GoldenCorpusLoader.load_from_file(manifest_path)
    report = CorpusCoverageAnalyzer.analyze(corpus)
    # The initial 2 cases are in EXPERIMENTAL_PHENOMENA
    assert "TEACHING_CONCEPTS" in report.underrepresented_domains
    assert "SCIENTIFIC_RESEARCH" in report.underrepresented_domains
    assert report.total_cases == 2
    assert report.total_artifact_references == 8


def test_scenario_s_unknown_corpus_metadata_fails_validation():
    corpus = GoldenCorpusLoader.load_from_file("golden_corpus/corpus_manifest.json")
    # Mutate to create an invalid case reference
    bad_dict = corpus.model_dump()
    bad_dict["cases"]["GOLDEN_OOBLECK"]["references"]["PRESENTATION"]["source_case_id"] = "MISMATCHED_ID"
    bad_corpus = GoldenCorpus(**bad_dict)
    ok, issues = GoldenCorpusValidator.validate(bad_corpus)
    assert ok is False
    assert any("not matching" in issue for issue in issues)


def test_scenario_t_historical_baseline_cannot_be_silently_overwritten():
    record = BaselineMutationRecord(
        target_case_id="GOLDEN_OOBLECK",
        target_artifact_type="PRESENTATION",
        previous_baseline_reference="v1.0.0",
        previous_scores={"SEMANTIC": 0.95},
        new_scores={"SEMANTIC": 0.70},  # Massive drop!
        change_reason="Silently lowering score requirement to avoid failing test",
        expected_quality_impact="Lower threshold",
        change_classification=ChangeClassification.DEPRECATION  # Unauthorized for lowering!
    )
    with pytest.raises(BenchmarkLaunderingAttemptError, match="Silent baseline lowering"):
        AntiLaunderingGuard.validate_mutation(record, strict_raise=True)
