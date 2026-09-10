"""
Unit tests for deterministic corpus splitting and manifest generation.
"""

from pathlib import Path
import pytest

from app.benchmarking.corpus_registry import BenchmarkCorpusRegistry
from app.benchmarking.split_manager import CorpusSplitManager
from app.benchmarking.taxonomy import CorpusCategory, CorpusSplit


def test_01_deterministic_split_assignment():
    reg = BenchmarkCorpusRegistry()
    reg.scan_directory("tests/fixtures/benchmark_corpus")
    assert reg.count() >= 12

    sm = CorpusSplitManager(reg)
    sm.assign_canonical_splits()

    train_fixtures = reg.get_by_split(CorpusSplit.TRAINING_REFERENCE)
    unseen_fixtures = reg.get_by_split(CorpusSplit.UNSEEN_GENERALIZATION)
    adv_fixtures = reg.get_by_split(CorpusSplit.ADVERSARIAL)

    assert len(train_fixtures) >= 2
    assert len(unseen_fixtures) >= 6
    assert len(adv_fixtures) >= 4

    # Ensure known benchmarks are strictly separated from unseen
    train_ids = {f.fixture_id for f in train_fixtures}
    unseen_ids = {f.fixture_id for f in unseen_fixtures}
    assert train_ids.isdisjoint(unseen_ids)


def test_02_manifest_generation(tmp_path: Path):
    reg = BenchmarkCorpusRegistry()
    reg.scan_directory("tests/fixtures/benchmark_corpus")
    sm = CorpusSplitManager(reg)
    sm.assign_canonical_splits()

    out_json = tmp_path / "manifest.json"
    manifest = sm.generate_manifest(out_json)

    assert out_json.exists()
    assert manifest["total_fixtures"] == reg.count()
    assert "UNSEEN_GENERALIZATION" in manifest["distribution_by_split"]
    assert "CONCEPT_HEAVY" in manifest["distribution_by_category"]
