"""
Comprehensive Negative Integrity and Hardening Tests for Phase 1B.2.

Covers:
1. Offline Epistemic Honesty (ResolutionStatus enum, confidence integrity)
2. Safe Stable Semantic ID Normalization (Markdown stripping vs scientific preservation)
3. Semantic Identity vs Provenance Identity (duplicate unit merging, secondary provenances)
4. Negative & Adversarial Validation (schema boundaries, immutability, corrupted manifests)
"""

import json
import pytest
from pydantic import ValidationError

from app.intelligence.markdown_tree_parser import SemanticBlockType
from app.intelligence.pipeline import (
    AmbiguityResolver,
    CandidateUnit,
    LocalClassifier,
    ManifestAssembler,
    ManifestAssemblyError,
    OfflineMockResolutionProvider,
    PayloadBuilder,
    ResolvedUnit,
    StructuralExtractor,
    UnitNormalizer,
)
from app.intelligence.schemas import (
    ConceptPayload,
    ContentType,
    KnowledgeCategory,
    KnowledgeProvenance,
    KnowledgeRelationship,
    KnowledgeUnit,
    ResolutionStatus,
    UniversalKnowledgeManifest,
    generate_stable_knowledge_id,
    normalize_content_for_identity,
)
from app.intelligence.traceability import SourceToKnowledgeUnitTraceabilityIndex


def _make_candidate(content: str, sec_id: str = "sec1", block_id: str = "b1", doc_id: str = "doc1") -> CandidateUnit:
    prov = KnowledgeProvenance(source_document_id=doc_id, source_section_id=sec_id, block_ids=[block_id])
    return CandidateUnit(
        candidate_id=f"cand_{sec_id}_{block_id}",
        source_document_id=doc_id,
        source_fingerprint="fp123",
        raw_content=content,
        normalized_content=normalize_content_for_identity(content),
        parsed_block_type=SemanticBlockType.PARAGRAPH,
        provenance=prov,
        parent_section_title="Section Title",
        heading_path=["Section Title"],
    )


# ============================================================================
# PART 1 — OFFLINE EPISTEMIC HONESTY TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_confident_local_unit_bypasses_ai_and_becomes_local_confident():
    raw_md = "# Definition Section\n\nTitik nyala adalah suhu terendah di mana uap zat cair akan menyala."
    tree = StructuralExtractor().extract(raw_md, "test.md")
    candidates = UnitNormalizer().normalize(tree)
    classified = LocalClassifier().classify(candidates)

    # Make sure local classifier gives high confidence
    assert classified[0].local_confidence >= 0.8

    resolver = AmbiguityResolver(provider=OfflineMockResolutionProvider())
    resolved = await resolver.resolve(classified)

    assert resolved[0].resolution_status == ResolutionStatus.LOCAL_CONFIDENT
    assert resolved[0].final_confidence == classified[0].local_confidence


@pytest.mark.asyncio
async def test_ambiguous_unit_in_offline_mode_becomes_unresolved_offline():
    cand = _make_candidate("Text without triggers")
    classified = LocalClassifier().classify([cand])
    # Manually drop local confidence to force ambiguity
    classified[0].local_confidence = 0.45

    resolver = AmbiguityResolver(provider=OfflineMockResolutionProvider())
    resolved = await resolver.resolve(classified)

    assert resolved[0].resolution_status == ResolutionStatus.UNRESOLVED_OFFLINE
    # Offline fallback MUST NOT inflate confidence artificially to 0.85
    assert resolved[0].final_confidence == 0.45


@pytest.mark.asyncio
async def test_offline_mode_does_not_increase_confidence_artificially():
    cand = _make_candidate("Ambiguous concept statement")
    classified = LocalClassifier().classify([cand])
    classified[0].local_confidence = 0.30

    provider = OfflineMockResolutionProvider()
    res_unit = await provider.resolve_unit(classified[0])

    assert res_unit.resolution_status == ResolutionStatus.UNRESOLVED_OFFLINE
    assert res_unit.final_confidence == 0.30
    assert res_unit.final_confidence != 0.85


@pytest.mark.asyncio
async def test_deferred_resolution_remains_explicitly_represented():
    class FailingResolutionProvider:
        async def resolve_unit(self, classified_unit):
            raise RuntimeError("API quota exceeded")

    cand = _make_candidate("Ambiguous statement")
    classified = LocalClassifier().classify([cand])
    classified[0].local_confidence = 0.40

    resolver = AmbiguityResolver(provider=FailingResolutionProvider())
    resolved = await resolver.resolve(classified)

    assert resolved[0].resolution_status == ResolutionStatus.DEFERRED
    assert resolved[0].final_confidence == 0.40


def test_serialization_preserves_resolution_state():
    prov = KnowledgeProvenance(source_document_id="doc1", source_section_id="sec1", block_ids=["b1"])
    unit = KnowledgeUnit(
        id="ku_1234567890ab",
        source_document_id="doc1",
        content_type=ContentType.CONCEPT,
        category=KnowledgeCategory.CORE_CONCEPT,
        raw_content="Unresolved content",
        normalized_content="Unresolved content",
        provenance=prov,
        confidence=0.45,
        resolution_status=ResolutionStatus.UNRESOLVED_OFFLINE,
        payload=ConceptPayload(concept_name="Unresolved", summary="Unresolved content")
    )

    data = unit.model_dump()
    assert data["resolution_status"] == "UNRESOLVED_OFFLINE"

    json_str = unit.model_dump_json()
    reconstructed = KnowledgeUnit.model_validate_json(json_str)

    assert reconstructed.resolution_status == ResolutionStatus.UNRESOLVED_OFFLINE
    assert reconstructed.confidence == 0.45


# ============================================================================
# PART 2 — SAFE STABLE SEMANTIC ID NORMALIZATION TESTS
# ============================================================================

def test_heading_and_markdown_normalization_equality():
    assert normalize_content_for_identity("# Title") == "Title"
    assert normalize_content_for_identity("## Title") == "Title"
    assert normalize_content_for_identity("###   Title  ") == "Title"
    assert normalize_content_for_identity("**Concept**") == "Concept"
    assert normalize_content_for_identity("_Caution_") == "Caution"

    id1 = generate_stable_knowledge_id("doc1", "# Newton's Law", ContentType.CONCEPT)
    id2 = generate_stable_knowledge_id("doc1", "Newton's Law", ContentType.CONCEPT)
    assert id1 == id2


def test_scientific_and_math_preservation_in_normalization():
    # Formulas and operators
    assert normalize_content_for_identity("F = ma") == "F = ma"
    assert normalize_content_for_identity("F ≠ ma") == "F ≠ ma"
    assert normalize_content_for_identity("v = s/t") == "v = s/t"
    assert normalize_content_for_identity("v = s*t") == "v = s*t"
    assert normalize_content_for_identity("a = Δv/Δt") == "a = Δv/Δt"
    assert normalize_content_for_identity("x²") == "x²"
    assert normalize_content_for_identity("H₂O") == "H₂O"
    assert normalize_content_for_identity("Na+") == "Na+"
    assert normalize_content_for_identity("pH = 7") == "pH = 7"
    assert normalize_content_for_identity("10.5") == "10.5"
    assert normalize_content_for_identity("3,14") == "3,14"
    assert normalize_content_for_identity("50%") == "50%"

    # Verify distinction
    assert generate_stable_knowledge_id("doc1", "F = ma", ContentType.FORMULA) != generate_stable_knowledge_id("doc1", "F ≠ ma", ContentType.FORMULA)
    assert generate_stable_knowledge_id("doc1", "v = s/t", ContentType.FORMULA) != generate_stable_knowledge_id("doc1", "v = s*t", ContentType.FORMULA)
    assert generate_stable_knowledge_id("doc1", "10.5", ContentType.FACT) != generate_stable_knowledge_id("doc1", "10.6", ContentType.FACT)


# ============================================================================
# PART 3 — SEMANTIC IDENTITY VS PROVENANCE IDENTITY TESTS
# ============================================================================

def test_identical_content_multiple_sections_merges_provenance_anchors():
    raw_md = """# Theory
Viscosity is resistance of a fluid to flow.

# Summary
Viscosity is resistance of a fluid to flow."""

    tree = StructuralExtractor().extract(raw_md, "physics.md")
    candidates = UnitNormalizer().normalize(tree)
    classified = LocalClassifier().classify(candidates)

    resolved = [
        ResolvedUnit(classified_unit=c, final_content_type=ContentType.DEFINITION, final_category=KnowledgeCategory.CORE_CONCEPT, final_confidence=0.9)
        for c in classified
    ]

    units = PayloadBuilder().build_units(resolved)

    # Identical content + same type -> 1 semantic unit with 2 provenance anchors
    assert len(units) == 1
    unit = units[0]
    assert len(unit.all_provenances) == 2
    assert unit.provenance.source_section_id != unit.secondary_provenances[0].source_section_id


def test_duplicate_anchor_at_same_location_not_duplicated():
    cand1 = _make_candidate("Viscosity definition", sec_id="sec1", block_id="b1")
    cand2 = _make_candidate("Viscosity definition", sec_id="sec1", block_id="b1")

    c1 = LocalClassifier().classify([cand1])[0]
    c2 = LocalClassifier().classify([cand2])[0]

    resolved = [
        ResolvedUnit(classified_unit=c1, final_content_type=ContentType.DEFINITION, final_category=KnowledgeCategory.CORE_CONCEPT, final_confidence=0.9),
        ResolvedUnit(classified_unit=c2, final_content_type=ContentType.DEFINITION, final_category=KnowledgeCategory.CORE_CONCEPT, final_confidence=0.9),
    ]

    units = PayloadBuilder().build_units(resolved)
    assert len(units) == 1
    assert len(units[0].all_provenances) == 1


def test_near_identical_content_does_not_merge():
    cand1 = _make_candidate("Force causes acceleration.", sec_id="sec1", block_id="b1")
    cand2 = _make_candidate("Net force causes acceleration.", sec_id="sec2", block_id="b2")

    c1 = LocalClassifier().classify([cand1])[0]
    c2 = LocalClassifier().classify([cand2])[0]

    resolved = [
        ResolvedUnit(classified_unit=c1, final_content_type=ContentType.FACT, final_category=KnowledgeCategory.CORE_CONCEPT, final_confidence=0.9),
        ResolvedUnit(classified_unit=c2, final_content_type=ContentType.FACT, final_category=KnowledgeCategory.CORE_CONCEPT, final_confidence=0.9),
    ]

    units = PayloadBuilder().build_units(resolved)
    assert len(units) == 2


def test_different_content_types_do_not_merge():
    cand1 = _make_candidate("Kalor adalah energi.", sec_id="sec1", block_id="b1")
    cand2 = _make_candidate("Kalor adalah energi.", sec_id="sec2", block_id="b2")

    c1 = LocalClassifier().classify([cand1])[0]
    c2 = LocalClassifier().classify([cand2])[0]

    resolved = [
        ResolvedUnit(classified_unit=c1, final_content_type=ContentType.DEFINITION, final_category=KnowledgeCategory.CORE_CONCEPT, final_confidence=0.9),
        ResolvedUnit(classified_unit=c2, final_content_type=ContentType.CONCEPT, final_category=KnowledgeCategory.CORE_CONCEPT, final_confidence=0.9),
    ]

    units = PayloadBuilder().build_units(resolved)
    assert len(units) == 2


def test_source_index_reverse_lookup_returns_all_anchors():
    prov1 = KnowledgeProvenance(source_document_id="doc1", source_section_id="sec_theory", block_ids=["blk_1"])
    prov2 = KnowledgeProvenance(source_document_id="doc1", source_section_id="sec_summary", block_ids=["blk_9"])

    unit = KnowledgeUnit(
        id="ku_1234567890ab",
        source_document_id="doc1",
        content_type=ContentType.DEFINITION,
        category=KnowledgeCategory.CORE_CONCEPT,
        raw_content="Viscosity is resistance of a fluid to flow.",
        normalized_content="Viscosity is resistance of a fluid to flow.",
        provenance=prov1,
        secondary_provenances=[prov2],
        confidence=0.9,
        payload=ConceptPayload(formal_definition="resistance of a fluid to flow.")
    )

    manifest = ManifestAssembler().assemble(
        manifest_id="man_test",
        document_title="Test Doc",
        domain="physics",
        units=[unit],
        relationships=[]
    )

    index = SourceToKnowledgeUnitTraceabilityIndex.build_from_manifest(manifest)

    # Forward lookup all provenances
    assert len(index.get_all_provenances(unit.id)) == 2

    # Reverse lookup by section
    assert index.get_units_by_section("sec_theory") == [unit.id]
    assert index.get_units_by_section("sec_summary") == [unit.id]

    # Reverse lookup by block
    assert index.get_units_by_block("blk_1") == [unit.id]
    assert index.get_units_by_block("blk_9") == [unit.id]


# ============================================================================
# PART 4 — NEGATIVE & ADVERSARIAL VALIDATION TESTS
# ============================================================================

def test_invalid_resolution_status_rejected():
    with pytest.raises(ValidationError):
        KnowledgeUnit(
            id="ku_1234567890ab",
            source_document_id="doc1",
            content_type=ContentType.CONCEPT,
            category=KnowledgeCategory.CORE_CONCEPT,
            raw_content="Test",
            normalized_content="Test",
            provenance=KnowledgeProvenance(source_document_id="doc1", source_section_id="s1", block_ids=["b1"]),
            confidence=0.9,
            resolution_status="INVALID_STATUS_STRING",
            payload=ConceptPayload(concept_name="Test", summary="Test")
        )


def test_impossible_confidence_rejected():
    prov = KnowledgeProvenance(source_document_id="doc1", source_section_id="s1", block_ids=["b1"])

    with pytest.raises(ValidationError):
        KnowledgeUnit(
            id="ku_1234567890ab",
            source_document_id="doc1",
            content_type=ContentType.CONCEPT,
            category=KnowledgeCategory.CORE_CONCEPT,
            raw_content="Test",
            normalized_content="Test",
            provenance=prov,
            confidence=1.5,  # > 1.0 invalid
            payload=ConceptPayload(concept_name="Test", summary="Test")
        )

    with pytest.raises(ValidationError):
        KnowledgeUnit(
            id="ku_1234567890ab",
            source_document_id="doc1",
            content_type=ContentType.CONCEPT,
            category=KnowledgeCategory.CORE_CONCEPT,
            raw_content="Test",
            normalized_content="Test",
            provenance=prov,
            confidence=-0.1,  # < 0.0 invalid
            payload=ConceptPayload(concept_name="Test", summary="Test")
        )


def test_relationship_referencing_missing_knowledge_unit_rejected():
    unit1 = KnowledgeUnit(
        id="ku_111111111111",
        source_document_id="doc1",
        content_type=ContentType.CONCEPT,
        category=KnowledgeCategory.CORE_CONCEPT,
        raw_content="Concept 1",
        normalized_content="Concept 1",
        provenance=KnowledgeProvenance(source_document_id="doc1", source_section_id="s1", block_ids=["b1"]),
        confidence=0.9,
        payload=ConceptPayload(concept_name="C1", summary="C1")
    )

    bad_rel = KnowledgeRelationship(
        relationship_id="rel_123",
        source_unit_id="ku_111111111111",
        target_unit_id="ku_999999999999",  # MISSING target unit
        relationship_type="EXPLAINS",
        weight=0.8
    )

    with pytest.raises(ManifestAssemblyError):
        ManifestAssembler().assemble(
            manifest_id="man_bad",
            document_title="Title",
            domain="physics",
            units=[unit1],
            relationships=[bad_rel]
        )


def test_corrupted_serialized_manifest_fails_validation_clearly():
    manifest_data = {
        "manifest_id": "man_corrupted",
        "document_title": "Bad Manifest",
        "units": {
            "ku_1": {
                "id": "ku_1",
                "source_document_id": "doc1",
                "content_type": "INVALID_CONTENT_TYPE",  # Invalid enum
                "raw_content": "bad"
            }
        }
    }

    with pytest.raises(ValidationError):
        UniversalKnowledgeManifest.model_validate(manifest_data)


def test_manifest_immutability():
    unit = KnowledgeUnit(
        id="ku_111111111111",
        source_document_id="doc1",
        content_type=ContentType.CONCEPT,
        category=KnowledgeCategory.CORE_CONCEPT,
        raw_content="Concept 1",
        normalized_content="Concept 1",
        provenance=KnowledgeProvenance(source_document_id="doc1", source_section_id="s1", block_ids=["b1"]),
        confidence=0.9,
        payload=ConceptPayload(concept_name="C1", summary="C1")
    )

    manifest = ManifestAssembler().assemble(
        manifest_id="man_1",
        document_title="Title",
        domain="physics",
        units=[unit],
        relationships=[]
    )

    with pytest.raises(ValidationError):
        manifest.manifest_id = "new_id"
