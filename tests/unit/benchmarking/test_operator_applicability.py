"""
Unit tests for operator applicability envelope synthesis and evidence strength rating.
"""

import pytest

from app.benchmarking.contracts import BenchmarkExecutionOutcome
from app.benchmarking.operator_analysis import OperatorEvidenceAnalyzer
from app.benchmarking.taxonomy import CorpusCategory, CorpusSplit, EvidenceStrength


def test_01_operator_insufficient_evidence_on_single_fixture():
    outcomes = [
        BenchmarkExecutionOutcome(
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
            operators_committed=("presentation_component_reflow",),
        )
    ]

    envelopes = OperatorEvidenceAnalyzer.evaluate_operators(outcomes)
    env = envelopes["presentation_component_reflow"]
    assert env.evidence_strength == EvidenceStrength.INSUFFICIENT
    assert env.fixture_diversity_count == 1


def test_02_operator_strong_evidence_across_multiple_fixtures():
    outcomes = []
    for i in range(7):
        outcomes.append(
            BenchmarkExecutionOutcome(
                job_id=f"j_{i}",
                fixture_id=f"fixture_{i}",
                artifact_type="PRESENTATION",
                corpus_category=CorpusCategory.CONCEPT_HEAVY if i % 2 == 0 else CorpusCategory.EXPERIMENT_HEAVY,
                split=CorpusSplit.UNSEEN_GENERALIZATION,
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
    assert env.evidence_strength == EvidenceStrength.STRONG
    assert env.regression_rate == 0.0
    assert env.fixture_diversity_count >= 6
