"""
Unit tests for generalization failure taxonomy classification.
"""

import pytest

from app.benchmarking.contracts import BenchmarkExecutionOutcome
from app.benchmarking.generalization import GeneralizationValidator
from app.benchmarking.taxonomy import (
    CorpusCategory,
    CorpusSplit,
    GeneralizationFailureType,
)


def test_01_classify_clean_export_has_no_failure():
    outcome = BenchmarkExecutionOutcome(
        job_id="j1",
        fixture_id="f1",
        artifact_type="PRESENTATION",
        corpus_category=CorpusCategory.CONCEPT_HEAVY,
        split=CorpusSplit.UNSEEN_GENERALIZATION,
        success=True,
        final_state="EXPORTED",
        decision="EXPORT_APPROVED",
        overall_quality_score=0.98,
        total_iterations=1,
        elapsed_seconds=1.0,
        hard_blockers_count=0,
        has_export_package=True,
    )
    fail_type = GeneralizationValidator.classify_outcome_failure(outcome)
    assert fail_type is None


def test_02_classify_regression_failure():
    outcome = BenchmarkExecutionOutcome(
        job_id="j2",
        fixture_id="f2",
        artifact_type="PRESENTATION",
        corpus_category=CorpusCategory.CONCEPT_HEAVY,
        split=CorpusSplit.UNSEEN_GENERALIZATION,
        success=False,
        final_state="MANUAL_REVIEW_REQUIRED",
        decision="BLOCKED",
        overall_quality_score=0.85,
        total_iterations=2,
        elapsed_seconds=1.0,
        hard_blockers_count=1,
        operators_rolled_back=("presentation_component_reflow",),
        has_export_package=False,
    )
    fail_type = GeneralizationValidator.classify_outcome_failure(outcome)
    assert fail_type == GeneralizationFailureType.REGRESSION_FAILURE


def test_03_classify_pathological_non_automatable_failure():
    outcome = BenchmarkExecutionOutcome(
        job_id="j3",
        fixture_id="path_sparse",
        artifact_type="WORKSHEET",
        corpus_category=CorpusCategory.PATHOLOGICAL,
        split=CorpusSplit.ADVERSARIAL,
        success=False,
        final_state="MANUAL_REVIEW_REQUIRED",
        decision="BLOCKED",
        overall_quality_score=0.60,
        total_iterations=3,
        elapsed_seconds=1.0,
        hard_blockers_count=1,
        has_export_package=False,
    )
    fail_type = GeneralizationValidator.classify_outcome_failure(outcome)
    assert fail_type == GeneralizationFailureType.NON_AUTOMATABLE_GENERALIZATION_FAILURE
