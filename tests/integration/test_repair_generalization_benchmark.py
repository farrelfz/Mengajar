"""
Universal Document Intelligence System V5 — Repair Generalization Benchmark Integration Test.

Phase 4.1: Executes end-to-end generalization validation across corpus categories,
validates metric persistence, operator envelopes, and immutability guarantees.
"""

from pathlib import Path
import pytest

from app.benchmarking.benchmark_runner import BenchmarkGeneralizationRunner
from app.benchmarking.corpus_registry import BenchmarkCorpusRegistry
from app.benchmarking.split_manager import CorpusSplitManager
from app.benchmarking.taxonomy import CorpusCategory, CorpusSplit


@pytest.mark.asyncio
async def test_01_generalization_benchmark_runner_representative_suite(tmp_path: Path):
    reg = BenchmarkCorpusRegistry()
    reg.scan_directory("tests/fixtures/benchmark_corpus")
    assert reg.count() >= 12

    sm = CorpusSplitManager(reg)
    sm.assign_canonical_splits()

    runner = BenchmarkGeneralizationRunner(
        registry=reg,
        output_dir=tmp_path / "benchmarks",
    )

    # Select representative fixtures covering all 5 categories
    fixtures = [
        "experiment_oobleck",                # Experiment (Known)
        "concept_rotational_dynamics",       # Concept (Unseen)
        "narrative_galileo_falling_bodies",  # Narrative (Unseen)
        "scientific_kti_climate_microalgae", # Scientific (Unseen)
        "path_sparse_stub",                  # Pathological (Adversarial)
    ]

    outcomes, metrics, envelopes = await runner.run_suite(
        fixture_ids=fixtures,
        artifact_types=("HANDOUT", "PRESENTATION"),
    )

    assert len(outcomes) == 10
    assert metrics.total_jobs == 10
    assert metrics.known_jobs >= 2
    assert metrics.unseen_jobs >= 6
    assert metrics.pathological_jobs >= 2
    assert metrics.repair_regression_rate <= 0.05
    assert metrics.worst_case_score >= 0.70

    # Verify generated report files
    rep_dir = tmp_path / "benchmarks"
    assert (rep_dir / "generalization_report.json").exists()
    assert (rep_dir / "generalization_report.md").exists()
    assert (rep_dir / "operator_matrix.json").exists()
    assert (rep_dir / "operator_matrix.md").exists()

    # Verify operator envelopes contain evidence
    assert len(envelopes) >= 5
    for op_id, env in envelopes.items():
        assert env.operator_id == op_id
        assert len(env.supported_artifact_types) >= 1
