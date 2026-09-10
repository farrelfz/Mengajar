"""
Unit tests for benchmark integrity, immutability, and leakage guards.
"""

from pathlib import Path
import pytest

from app.benchmarking.contracts import BenchmarkFixtureMetadata, StructuralSignature
from app.benchmarking.corpus_registry import BenchmarkCorpusRegistry
from app.benchmarking.leakage_guard import BenchmarkLeakageError, BenchmarkLeakageGuard
from app.benchmarking.taxonomy import CorpusCategory, CorpusSplit
from app.quality.repair.actuation.learning import RepairOperatorPerformanceRegistry


def test_01_immutability_detection(tmp_path: Path):
    doc_path = tmp_path / "immutable_doc.md"
    doc_path.write_text("# Original Content", encoding="utf-8")

    meta = BenchmarkFixtureMetadata(
        fixture_id="doc1",
        source_path=str(doc_path.resolve()),
        corpus_category=CorpusCategory.CONCEPT_HEAVY,
        domain="Physics",
        difficulty_level="INTERMEDIATE",
        structural_signature=StructuralSignature(
            token_count=2,
            character_count=18,
            section_count=1,
            max_heading_depth=1,
        ),
        content_hash=BenchmarkFixtureMetadata.compute_hash("# Original Content"),
    )

    reg = BenchmarkCorpusRegistry()
    reg.register(meta)

    valid, issues = reg.verify_immutability()
    assert valid is True
    assert len(issues) == 0

    # Mutate the file
    doc_path.write_text("# Mutated Content", encoding="utf-8")
    valid_after, issues_after = reg.verify_immutability()
    assert valid_after is False
    assert len(issues_after) == 1
    assert "hash mismatch" in issues_after[0]


def test_02_leakage_guard_prevents_registry_mutation():
    reg = RepairOperatorPerformanceRegistry.get_default()
    initial_count = len(reg._records)

    with BenchmarkLeakageGuard(CorpusSplit.UNSEEN_GENERALIZATION) as guard:
        # Simulate an operator execution attempting to write into registry
        reg.record_execution(
            operator_id="test_op",
            artifact_type="PRESENTATION",
            root_cause="UNKNOWN",
            defect_signature="sig",
            success=True,
            score_delta=0.05,
            drift=0.0,
            execution_ms=1.0,
        )

    # After exit, guard must have detected the leak and restored initial state
    assert guard.leakage_detected is True
    assert len(reg._records) == initial_count


def test_03_leakage_guard_strict_raise():
    reg = RepairOperatorPerformanceRegistry.get_default()

    with pytest.raises(BenchmarkLeakageError):
        with BenchmarkLeakageGuard(CorpusSplit.UNSEEN_GENERALIZATION, strict_raise=True):
            reg.record_execution(
                operator_id="test_leak_op",
                artifact_type="WORKSHEET",
                root_cause="UNKNOWN",
                defect_signature="sig",
                success=True,
                score_delta=0.05,
                drift=0.0,
                execution_ms=1.0,
            )
