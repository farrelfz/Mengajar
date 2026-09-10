"""
Integration tests for KnowledgeCompiler, offline Markdown execution, and traceability index.
"""

from pathlib import Path
import pytest

from app.intelligence.pipeline import KnowledgeCompiler
from app.intelligence.schemas import AudienceProfile, IntrinsicImportance, UniversalKnowledgeManifest
from app.intelligence.traceability import SourceToKnowledgeUnitTraceabilityIndex

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"


def test_compile_simple_physics_fixture_offline():
    fixture_path = FIXTURES_DIR / "simple_physics.md"
    raw_md = fixture_path.read_text(encoding="utf-8")

    compiler = KnowledgeCompiler()
    manifest = compiler.compile_sync(raw_md, source_filename="simple_physics.md", domain="physics")

    assert manifest.document_title == "Simple Physics"
    assert len(manifest.units) >= 3
    assert manifest.manifest_id.startswith("man_")
    assert manifest.ambiguity_ratio >= 0.0

    # Verify no presentation-specific fields exist in manifest
    manifest_dict = manifest.model_dump()
    assert "min_slides" not in manifest_dict
    assert "max_slides" not in manifest_dict
    assert "target_slides" not in manifest_dict
    assert "page_count" not in manifest_dict
    assert "css" not in manifest_dict


def test_compile_experiment_fixture_offline():
    fixture_path = FIXTURES_DIR / "experiment.md"
    raw_md = fixture_path.read_text(encoding="utf-8")

    compiler = KnowledgeCompiler()
    manifest = compiler.compile_sync(raw_md, source_filename="experiment.md", domain="experiment_kir")

    assert len(manifest.units) >= 4
    # Check that procedure or data payload was created
    payload_kinds = [u.payload.kind for u in manifest.units.values()]
    assert "procedure" in payload_kinds or "evidence" in payload_kinds or "concept" in payload_kinds


def test_compile_mixed_semantics_fixture_offline():
    fixture_path = FIXTURES_DIR / "mixed_semantics.md"
    raw_md = fixture_path.read_text(encoding="utf-8")

    compiler = KnowledgeCompiler()
    manifest = compiler.compile_sync(raw_md, source_filename="mixed_semantics.md", domain="physics")

    assert len(manifest.units) >= 3


def test_traceability_index_forward_and_reverse():
    fixture_path = FIXTURES_DIR / "simple_physics.md"
    raw_md = fixture_path.read_text(encoding="utf-8")

    compiler = KnowledgeCompiler()
    manifest = compiler.compile_sync(raw_md, source_filename="simple_physics.md", domain="physics")

    index = SourceToKnowledgeUnitTraceabilityIndex.build_from_manifest(manifest)

    # Forward lookup test
    first_unit_id = list(manifest.units.keys())[0]
    prov = index.get_provenance(first_unit_id)
    assert prov is not None
    assert prov.source_document_id is not None

    # Reverse lookup test
    sec_id = prov.source_section_id
    unit_ids = index.get_units_by_section(sec_id)
    assert first_unit_id in unit_ids


def test_manifest_json_roundtrip_serialization():
    fixture_path = FIXTURES_DIR / "simple_physics.md"
    raw_md = fixture_path.read_text(encoding="utf-8")

    compiler = KnowledgeCompiler()
    manifest = compiler.compile_sync(raw_md, source_filename="simple_physics.md", domain="physics")

    json_str = manifest.model_json_schema()
    json_bytes = manifest.model_dump_json()

    deserialized = UniversalKnowledgeManifest.model_validate_json(json_bytes)
    assert deserialized.manifest_id == manifest.manifest_id
    assert len(deserialized.units) == len(manifest.units)
