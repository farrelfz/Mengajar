"""
Unit tests for fixture metadata extraction, validation, and content hashing.
"""

from pathlib import Path
import pytest

from app.benchmarking.contracts import BenchmarkFixtureMetadata, StructuralSignature
from app.benchmarking.fixture_metadata import FixtureMetadataAnalyzer
from app.benchmarking.taxonomy import CorpusCategory, CorpusSplit


def test_01_structural_signature_analysis():
    sample_text = """# Title
## Section 1
Berikut rumus fisika: $$E = mc^2$$ dan formula $F=ma$.
| Param | Nilai |
| :--- | :--- |
| Massa | 10 kg |
"""
    sig = FixtureMetadataAnalyzer.analyze_source_structure(sample_text)
    assert sig.token_count > 10
    assert sig.section_count >= 2
    assert sig.max_heading_depth == 2
    assert sig.table_count >= 1
    assert sig.formula_count >= 1
    assert isinstance(sig.character_count, int)


def test_02_metadata_hash_reproducibility():
    content_a = "# Test Document A\nContent"
    content_b = "# Test Document B\nContent"
    hash_a1 = BenchmarkFixtureMetadata.compute_hash(content_a)
    hash_a2 = BenchmarkFixtureMetadata.compute_hash(content_a)
    hash_b = BenchmarkFixtureMetadata.compute_hash(content_b)

    assert hash_a1 == hash_a2
    assert hash_a1 != hash_b
    assert len(hash_a1) == 16


def test_03_load_or_infer_metadata(tmp_path: Path):
    doc_path = tmp_path / "sample_concept.md"
    doc_path.write_text("# Dinamika Rotasi\nMomen inersia $I = mr^2$.\n", encoding="utf-8")

    meta = FixtureMetadataAnalyzer.load_or_infer_metadata(doc_path)
    assert meta.fixture_id == "sample_concept"
    assert meta.content_hash != ""
    assert meta.structural_signature.formula_count >= 1
