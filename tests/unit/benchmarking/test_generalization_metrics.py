"""
Unit tests for generalization metric calculations (RGR, RRG, FRR, CRR, ZER, Gap).
"""

import pytest

from app.benchmarking.contracts import BenchmarkExecutionOutcome
from app.benchmarking.metrics import GeneralizationMetricEngine
from app.benchmarking.taxonomy import CorpusCategory, CorpusSplit


def test_01_metrics_calculation_healthy_corpus():
    outcomes = [
        # Known
        BenchmarkExecutionOutcome(
            job_id="j1",
            fixture_id="oobleck",
            artifact_type="PRESENTATION",
            corpus_category=CorpusCategory.EXPERIMENT_HEAVY,
            split=CorpusSplit.TRAINING_REFERENCE,
            success=True,
            final_state="EXPORTED",
            decision="EXPORT_APPROVED",
            overall_quality_score=0.98,
            total_iterations=1,
            elapsed_seconds=2.0,
            hard_blockers_count=0,
            operators_committed=("presentation_component_reflow",),
        ),
        # Unseen
        BenchmarkExecutionOutcome(
            job_id="j2",
            fixture_id="rotational",
            artifact_type="PRESENTATION",
            corpus_category=CorpusCategory.CONCEPT_HEAVY,
            split=CorpusSplit.UNSEEN_GENERALIZATION,
            success=True,
            final_state="EXPORTED",
            decision="EXPORT_APPROVED",
            overall_quality_score=0.96,
            total_iterations=1,
            elapsed_seconds=2.1,
            hard_blockers_count=0,
            operators_attempted=("presentation_component_reflow",),
            operators_committed=("presentation_component_reflow",),
        ),
    ]

    metrics = GeneralizationMetricEngine.compute_metrics(outcomes)
    assert metrics.total_jobs == 2
    assert metrics.known_jobs == 1
    assert metrics.unseen_jobs == 1
    assert metrics.known_corpus_mean_score == 0.98
    assert metrics.unseen_corpus_mean_score == 0.96
    assert metrics.generalization_gap == 0.02
    assert metrics.generalization_warning is False
    assert metrics.repair_generalization_rate == 1.0
    assert metrics.repair_regression_rate == 0.0


def test_02_metrics_generalization_warning_on_large_gap():
    outcomes = [
        BenchmarkExecutionOutcome(
            job_id="j1",
            fixture_id="f1",
            artifact_type="PRESENTATION",
            corpus_category=CorpusCategory.CONCEPT_HEAVY,
            split=CorpusSplit.TRAINING_REFERENCE,
            success=True,
            final_state="EXPORTED",
            decision="EXPORT_APPROVED",
            overall_quality_score=1.00,
            total_iterations=1,
            elapsed_seconds=1.0,
            hard_blockers_count=0,
        ),
        BenchmarkExecutionOutcome(
            job_id="j2",
            fixture_id="f2",
            artifact_type="PRESENTATION",
            corpus_category=CorpusCategory.CONCEPT_HEAVY,
            split=CorpusSplit.UNSEEN_GENERALIZATION,
            success=False,
            final_state="MANUAL_REVIEW_REQUIRED",
            decision="BLOCKED",
            overall_quality_score=0.72,
            total_iterations=3,
            elapsed_seconds=1.5,
            hard_blockers_count=1,
            hard_blockers=("ELEMENT_COLLISION",),
        ),
    ]

    metrics = GeneralizationMetricEngine.compute_metrics(outcomes)
    assert metrics.generalization_gap == 0.28  # 1.00 - 0.72 > 0.08
    assert metrics.generalization_warning is True
    assert metrics.worst_case_score == 0.72
    assert metrics.unseen_blocker_retention_rate == 1.0
