"""
Universal Document Intelligence System V5 — Generalization Adversarial Test Suite.

Phase 4.1: Tests Scenarios A through O evaluating generalization limits,
anti-leakage guards, anti-masking guarantees, and applicability boundaries.
"""

from pathlib import Path
import pytest

from app.benchmarking.contracts import (
    BenchmarkExecutionOutcome,
    BenchmarkFixtureMetadata,
    StructuralSignature,
)
from app.benchmarking.corpus_registry import BenchmarkCorpusRegistry
from app.benchmarking.generalization import GeneralizationValidator
from app.benchmarking.leakage_guard import BenchmarkLeakageError, BenchmarkLeakageGuard
from app.benchmarking.metrics import GeneralizationMetricEngine
from app.benchmarking.operator_analysis import OperatorEvidenceAnalyzer
from app.benchmarking.taxonomy import (
    CorpusCategory,
    CorpusSplit,
    EvidenceStrength,
    GeneralizationFailureType,
)
from app.quality.repair.actuation.learning import RepairOperatorPerformanceRegistry
from app.quality.repair.effectiveness.firewall import (
    RepairStrategyCompatibilityFirewall,
)
from app.quality.repair.registry import DEFAULT_STRATEGY_REGISTRY
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType


def test_scenario_a_generalization_gap_detected():
    """Scenario A: Operator performs well on known fixture but fails on unseen signature -> Gap detected."""
    outcomes = [
        BenchmarkExecutionOutcome(
            job_id="j_known",
            fixture_id="oobleck",
            artifact_type="PRESENTATION",
            corpus_category=CorpusCategory.EXPERIMENT_HEAVY,
            split=CorpusSplit.TRAINING_REFERENCE,
            success=True,
            final_state="EXPORTED",
            decision="EXPORT_APPROVED",
            overall_quality_score=0.99,
            total_iterations=1,
            elapsed_seconds=1.0,
            hard_blockers_count=0,
        ),
        BenchmarkExecutionOutcome(
            job_id="j_unseen",
            fixture_id="unseen_structure",
            artifact_type="PRESENTATION",
            corpus_category=CorpusCategory.CONCEPT_HEAVY,
            split=CorpusSplit.UNSEEN_GENERALIZATION,
            success=False,
            final_state="MANUAL_REVIEW_REQUIRED",
            decision="BLOCKED",
            overall_quality_score=0.82,
            total_iterations=3,
            elapsed_seconds=1.5,
            hard_blockers_count=1,
            hard_blockers=("ELEMENT_COLLISION",),
        ),
    ]
    metrics = GeneralizationMetricEngine.compute_metrics(outcomes)
    assert metrics.generalization_gap == 0.17  # 0.99 - 0.82 > 0.08
    assert metrics.generalization_warning is True


def test_scenario_b_firewall_rejection_cross_artifact():
    """Scenario B: Presentation strategy attempted on Worksheet is rejected by firewall."""
    pres_strat = DEFAULT_STRATEGY_REGISTRY.get_strategy("presentation_component_reflow")
    assert pres_strat is not None

    eligible, rejections = RepairStrategyCompatibilityFirewall.filter_eligible_strategies(
        strategies=[pres_strat],
        artifact_type="WORKSHEET",
        root_cause=RootCauseType.GRID_GEOMETRY,
    )
    assert len(eligible) == 0
    assert len(rejections) == 1
    assert rejections[0].filter_stage == "ARTIFACT_COMPATIBILITY"


def test_scenario_c_semantic_drift_triggers_rollback():
    """Scenario C: Operator fixes visual defect but creates semantic drift -> rolled back."""
    outcome = BenchmarkExecutionOutcome(
        job_id="j_drift",
        fixture_id="drift_doc",
        artifact_type="WORKSHEET",
        corpus_category=CorpusCategory.CONCEPT_HEAVY,
        split=CorpusSplit.UNSEEN_GENERALIZATION,
        success=False,
        final_state="ROLLED_BACK",
        decision="REVISE",
        overall_quality_score=0.88,
        total_iterations=2,
        elapsed_seconds=1.2,
        hard_blockers_count=1,
        operators_rolled_back=("aggressive_content_truncator",),
    )
    fail_type = GeneralizationValidator.classify_outcome_failure(outcome)
    assert fail_type == GeneralizationFailureType.REGRESSION_FAILURE


def test_scenario_d_not_counted_as_generalized_success_when_blocker_retained():
    """Scenario D: Operator improves aggregate score but leaves hard blocker -> not counted as generalized success."""
    outcome = BenchmarkExecutionOutcome(
        job_id="j_retained",
        fixture_id="unseen_math",
        artifact_type="PRESENTATION",
        corpus_category=CorpusCategory.CONCEPT_HEAVY,
        split=CorpusSplit.UNSEEN_GENERALIZATION,
        success=False,
        final_state="MANUAL_REVIEW_REQUIRED",
        decision="BLOCKED",
        overall_quality_score=0.91,
        total_iterations=3,
        elapsed_seconds=1.5,
        hard_blockers_count=1,
        hard_blockers=("ELEMENT_COLLISION",),
        operators_attempted=("presentation_component_reflow",),
        operators_committed=(),
    )
    metrics = GeneralizationMetricEngine.compute_metrics([outcome])
    assert metrics.repair_generalization_rate == 0.0
    assert metrics.unseen_blocker_retention_rate == 1.0


def test_scenario_e_benchmark_fixture_immutability_failure(tmp_path: Path):
    """Scenario E: Benchmark fixture accidentally mutated on disk -> immutability failure raised."""
    fpath = tmp_path / "fixture.md"
    fpath.write_text("# Initial Text", encoding="utf-8")

    meta = BenchmarkFixtureMetadata(
        fixture_id="fix1",
        source_path=str(fpath.resolve()),
        corpus_category=CorpusCategory.CONCEPT_HEAVY,
        domain="Physics",
        structural_signature=StructuralSignature(
            token_count=2,
            character_count=14,
            section_count=1,
            max_heading_depth=1,
        ),
        content_hash=BenchmarkFixtureMetadata.compute_hash("# Initial Text"),
    )
    reg = BenchmarkCorpusRegistry()
    reg.register(meta)

    # Mutate file
    fpath.write_text("# Altered Text In Place", encoding="utf-8")
    valid, issues = reg.verify_immutability()
    assert valid is False
    assert len(issues) == 1
    assert "hash mismatch" in issues[0]


def test_scenario_f_benchmark_leakage_detection():
    """Scenario F: Unseen benchmark execution attempting to contaminate operator weights is caught."""
    reg = RepairOperatorPerformanceRegistry.get_default()
    initial_len = len(reg._records)

    with pytest.raises(BenchmarkLeakageError):
        with BenchmarkLeakageGuard(CorpusSplit.UNSEEN_GENERALIZATION, strict_raise=True):
            reg.record_execution(
                operator_id="leaking_operator",
                artifact_type="PRESENTATION",
                root_cause="ELEMENT_COLLISION",
                defect_signature="sig_leak",
                success=True,
                score_delta=0.08,
                drift=0.0,
                execution_ms=2.0,
            )

    # Registry state restored
    assert len(reg._records) == initial_len


def test_scenario_g_low_structural_diversity_evidence_strength():
    """Scenario G: High success rate based on repeated identical structures has limited evidence strength."""
    # 6 executions but all on the EXACT same category and format
    outcomes = []
    for i in range(6):
        outcomes.append(
            BenchmarkExecutionOutcome(
                job_id=f"j_{i}",
                fixture_id=f"copy_{i}",
                artifact_type="PRESENTATION",
                corpus_category=CorpusCategory.EXPERIMENT_HEAVY,
                split=CorpusSplit.TRAINING_REFERENCE,
                success=True,
                final_state="EXPORTED",
                decision="EXPORT_APPROVED",
                overall_quality_score=0.98,
                total_iterations=1,
                elapsed_seconds=1.0,
                hard_blockers_count=0,
                operators_committed=("presentation_component_reflow",),
            )
        )
    envelopes = OperatorEvidenceAnalyzer.evaluate_operators(outcomes)
    env = envelopes["presentation_component_reflow"]
    # Only 1 unique signature ("EXPERIMENT_HEAVY:PRESENTATION"), so evidence cannot be STRONG
    assert env.evidence_strength != EvidenceStrength.STRONG


def test_scenario_h_high_execution_low_causal_resolution_downgrade():
    """Scenario H: Operator has high execution success but low causal blocker resolution."""
    outcomes = [
        BenchmarkExecutionOutcome(
            job_id="j_h",
            fixture_id="fix_h",
            artifact_type="PRESENTATION",
            corpus_category=CorpusCategory.CONCEPT_HEAVY,
            split=CorpusSplit.UNSEEN_GENERALIZATION,
            success=False,
            final_state="MANUAL_REVIEW_REQUIRED",
            decision="BLOCKED",
            overall_quality_score=0.86,
            total_iterations=3,
            elapsed_seconds=1.0,
            hard_blockers_count=1,
            hard_blockers=("ELEMENT_COLLISION",),
            operators_attempted=("presentation_component_reflow",),
            operators_committed=(),
        )
    ]
    metrics = GeneralizationMetricEngine.compute_metrics(outcomes)
    assert metrics.causal_resolution_rate == 0.0


def test_scenario_i_applicability_envelope_distinction():
    """Scenario I: Slide split actuator marked supported for PRESENTATION and unsupported for WORKSHEET."""
    outcomes = [
        BenchmarkExecutionOutcome(
            job_id="j_pres",
            fixture_id="pres_doc",
            artifact_type="PRESENTATION",
            corpus_category=CorpusCategory.CONCEPT_HEAVY,
            split=CorpusSplit.UNSEEN_GENERALIZATION,
            success=True,
            final_state="EXPORTED",
            decision="EXPORT_APPROVED",
            overall_quality_score=0.95,
            total_iterations=1,
            elapsed_seconds=1.0,
            hard_blockers_count=0,
            operators_committed=("presentation_slide_split_actuator",),
        )
    ]
    envelopes = OperatorEvidenceAnalyzer.evaluate_operators(outcomes)
    env = envelopes["presentation_slide_split_actuator"]
    assert "PRESENTATION" in env.supported_artifact_types
    assert "WORKSHEET" not in env.supported_artifact_types


def test_scenario_j_unseen_score_collapse_triggers_warning():
    """Scenario J: Known fixtures score high but unseen collapses -> GENERALIZATION_WARNING."""
    outcomes = [
        BenchmarkExecutionOutcome(
            job_id="j_k",
            fixture_id="known_1",
            artifact_type="PRESENTATION",
            corpus_category=CorpusCategory.EXPERIMENT_HEAVY,
            split=CorpusSplit.TRAINING_REFERENCE,
            success=True,
            final_state="EXPORTED",
            decision="EXPORT_APPROVED",
            overall_quality_score=0.99,
            total_iterations=1,
            elapsed_seconds=1.0,
            hard_blockers_count=0,
        ),
        BenchmarkExecutionOutcome(
            job_id="j_u",
            fixture_id="unseen_1",
            artifact_type="PRESENTATION",
            corpus_category=CorpusCategory.CONCEPT_HEAVY,
            split=CorpusSplit.UNSEEN_GENERALIZATION,
            success=False,
            final_state="MANUAL_REVIEW_REQUIRED",
            decision="BLOCKED",
            overall_quality_score=0.78,
            total_iterations=3,
            elapsed_seconds=1.0,
            hard_blockers_count=1,
        ),
    ]
    metrics = GeneralizationMetricEngine.compute_metrics(outcomes)
    assert metrics.generalization_warning is True
    assert metrics.generalization_gap > 0.08


def test_scenario_k_pathological_fixture_non_automatable_classification():
    """Scenario K: Pathological fixture requiring manual review classified as NON_AUTOMATABLE, not engine failure."""
    outcome = BenchmarkExecutionOutcome(
        job_id="j_p",
        fixture_id="path_sparse_stub",
        artifact_type="SCIENTIFIC_DOCUMENT",
        corpus_category=CorpusCategory.PATHOLOGICAL,
        split=CorpusSplit.ADVERSARIAL,
        success=False,
        final_state="MANUAL_REVIEW_REQUIRED",
        decision="BLOCKED",
        overall_quality_score=0.65,
        total_iterations=2,
        elapsed_seconds=0.8,
        hard_blockers_count=1,
        hard_blockers=("EMPTY_SECTIONS",),
    )
    fail_type = GeneralizationValidator.classify_outcome_failure(outcome)
    assert fail_type == GeneralizationFailureType.NON_AUTOMATABLE_GENERALIZATION_FAILURE


def test_scenario_l_no_filename_based_classification():
    """Scenario L: Fixture category is derived from metadata contract, not filename pattern."""
    meta = BenchmarkFixtureMetadata(
        fixture_id="experiment_like_name_that_is_actually_narrative",
        source_path="/path/test.md",
        corpus_category=CorpusCategory.NARRATIVE_HEAVY,
        domain="History of Science",
        structural_signature=StructuralSignature(
            token_count=100, character_count=500, section_count=3, max_heading_depth=2
        ),
    )
    assert meta.corpus_category == CorpusCategory.NARRATIVE_HEAVY
    assert meta.corpus_category != CorpusCategory.EXPERIMENT_HEAVY


def test_scenario_m_meaningfulness_exclusion_explicit():
    """Scenario M: If an artifact type is omitted for a fixture, it is explicit in expected_artifact_types."""
    meta = BenchmarkFixtureMetadata(
        fixture_id="narrative_pure",
        source_path="/path/narrative.md",
        corpus_category=CorpusCategory.NARRATIVE_HEAVY,
        domain="History",
        structural_signature=StructuralSignature(
            token_count=100, character_count=500, section_count=3, max_heading_depth=2
        ),
        expected_artifact_types=("HANDOUT", "PRESENTATION"),  # Worksheet & Scientific explicitly excluded
    )
    assert "WORKSHEET" not in meta.expected_artifact_types
    assert "SCIENTIFIC_DOCUMENT" not in meta.expected_artifact_types


def test_scenario_n_anti_masking_surfaces_catastrophic_failure():
    """Scenario N: High average score does not mask a single catastrophic failure."""
    # 9 pristine scores (0.99) + 1 catastrophic failure (0.60) -> average is 0.951 (looks high!)
    outcomes = [
        BenchmarkExecutionOutcome(
            job_id=f"j_{i}",
            fixture_id=f"doc_{i}",
            artifact_type="PRESENTATION",
            corpus_category=CorpusCategory.CONCEPT_HEAVY,
            split=CorpusSplit.UNSEEN_GENERALIZATION,
            success=True,
            final_state="EXPORTED",
            decision="EXPORT_APPROVED",
            overall_quality_score=0.99,
            total_iterations=1,
            elapsed_seconds=1.0,
            hard_blockers_count=0,
        )
        for i in range(9)
    ]
    outcomes.append(
        BenchmarkExecutionOutcome(
            job_id="j_catastrophic",
            fixture_id="doc_collapsed",
            artifact_type="PRESENTATION",
            corpus_category=CorpusCategory.CONCEPT_HEAVY,
            split=CorpusSplit.UNSEEN_GENERALIZATION,
            success=False,
            final_state="MANUAL_REVIEW_REQUIRED",
            decision="BLOCKED",
            overall_quality_score=0.60,
            total_iterations=3,
            elapsed_seconds=1.0,
            hard_blockers_count=2,
            hard_blockers=("ELEMENT_COLLISION", "TEXT_TOO_SMALL"),
        )
    )
    metrics = GeneralizationMetricEngine.compute_metrics(outcomes)
    has_masking, violations = GeneralizationValidator.check_anti_masking(outcomes, metrics)

    assert has_masking is True
    assert len(violations) >= 1
    assert "Catastrophic score drop masked by average" in violations[0]
    assert metrics.worst_case_score == 0.60


def test_scenario_o_single_success_is_insufficient_evidence():
    """Scenario O: Operator succeeding only once rated INSUFFICIENT, not high reliability."""
    outcomes = [
        BenchmarkExecutionOutcome(
            job_id="j_one",
            fixture_id="doc_one",
            artifact_type="SCIENTIFIC_DOCUMENT",
            corpus_category=CorpusCategory.SCIENTIFIC_HEAVY,
            split=CorpusSplit.UNSEEN_GENERALIZATION,
            success=True,
            final_state="EXPORTED",
            decision="EXPORT_APPROVED",
            overall_quality_score=1.00,
            total_iterations=1,
            elapsed_seconds=1.0,
            hard_blockers_count=0,
            operators_committed=("scientific_citation_visibility",),
        )
    ]
    envelopes = OperatorEvidenceAnalyzer.evaluate_operators(outcomes)
    env = envelopes["scientific_citation_visibility"]
    assert env.evidence_strength == EvidenceStrength.INSUFFICIENT
