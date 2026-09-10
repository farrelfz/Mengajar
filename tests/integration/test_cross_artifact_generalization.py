"""
Universal Document Intelligence System V5 — Cross-Artifact Generalization Test Suite.

Phase 4.1: Evaluates cross-artifact transformation invariants across diverse unseen inputs:
Presentation (16:9, cognitive load, typography floor), Handout (explanatory hierarchy),
Worksheet (inquiry arc, explanation withholding), and Scientific Document (formal structure, claims).
"""

from pathlib import Path
import pytest

from app.benchmarking.benchmark_runner import BenchmarkGeneralizationRunner
from app.benchmarking.corpus_registry import BenchmarkCorpusRegistry
from app.benchmarking.split_manager import CorpusSplitManager


@pytest.mark.asyncio
async def test_01_cross_artifact_invariants_on_unseen_concept(tmp_path: Path):
    reg = BenchmarkCorpusRegistry()
    reg.scan_directory("tests/fixtures/benchmark_corpus")
    sm = CorpusSplitManager(reg)
    sm.assign_canonical_splits()

    runner = BenchmarkGeneralizationRunner(
        registry=reg,
        output_dir=tmp_path / "cross_art_concept",
    )

    # Run all 4 artifact formats on unseen concept fixture
    outcomes, metrics, envelopes = await runner.run_suite(
        fixture_ids=["concept_harmonic_motion"],
        artifact_types=("HANDOUT", "PRESENTATION", "WORKSHEET", "SCIENTIFIC_DOCUMENT"),
    )

    assert len(outcomes) == 4
    for o in outcomes:
        assert o.overall_quality_score >= 0.85
        assert o.hard_blockers_count == 0
        assert o.final_state in ("EXPORTED", "MANUAL_REVIEW_REQUIRED")
        if o.artifact_type in ("HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"):
            assert o.has_export_package is True
            assert o.final_state == "EXPORTED"


@pytest.mark.asyncio
async def test_02_worksheet_explanation_withholding_on_unseen_experiment(tmp_path: Path):
    reg = BenchmarkCorpusRegistry()
    reg.scan_directory("tests/fixtures/benchmark_corpus")
    sm = CorpusSplitManager(reg)
    sm.assign_canonical_splits()

    runner = BenchmarkGeneralizationRunner(
        registry=reg,
        output_dir=tmp_path / "ws_unseen",
    )

    # Run worksheet on unseen pendulum investigation
    outcomes, metrics, envelopes = await runner.run_suite(
        fixture_ids=["experiment_pendulum_investigation"],
        artifact_types=("WORKSHEET",),
    )

    assert len(outcomes) == 1
    ws_outcome = outcomes[0]
    assert ws_outcome.artifact_type == "WORKSHEET"
    assert ws_outcome.overall_quality_score >= 0.90
    assert ws_outcome.hard_blockers_count == 0
    assert ws_outcome.has_export_package is True
