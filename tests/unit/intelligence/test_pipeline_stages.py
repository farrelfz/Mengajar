"""
Unit tests for canonical 9-stage Knowledge Compilation Pipeline stages.
"""

import pytest
from pathlib import Path

from pydantic import ValidationError

from app.intelligence.pipeline import (
    AmbiguityResolver,
    ClaimEvidenceExtractor,
    ImportanceAnalyzer,
    KnowledgeCompiler,
    LocalClassifier,
    ManifestAssembler,
    ManifestAssemblyError,
    OfflineMockResolutionProvider,
    PayloadBuilder,
    RelationshipInferencer,
    ResolvedUnit,
    StructuralExtractor,
    UnitNormalizer,
)
from app.intelligence.schemas import (
    ConceptPayload,
    ContentType,
    EvidencePayload,
    FormalPayload,
    IntrinsicImportance,
    KnowledgeCategory,
    PedagogicalPayload,
    ProcedurePayload,
)

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"


def test_stage1_structural_extractor():
    raw_md = "# Title\n\n## Section 1\nParagraph 1\n\n## Section 2\nParagraph 2"
    extractor = StructuralExtractor()
    tree = extractor.extract(raw_md, source_filename="test.md")

    assert tree.title == "Test"
    assert len(tree.sections) >= 2
    assert tree.total_blocks_count >= 2


def test_stage2_unit_normalizer():
    raw_md = "# Title\n\n## Section 1\n  Text with extra   spaces  \n"
    extractor = StructuralExtractor()
    tree = extractor.extract(raw_md, source_filename="test.md")
    normalizer = UnitNormalizer()
    candidates = normalizer.normalize(tree)

    assert len(candidates) >= 1
    assert candidates[0].normalized_content == "Text with extra spaces"
    assert candidates[0].provenance.source_document_id == tree.source_document_id


def test_stage3_local_classifier_formula_and_procedure():
    raw_md = "# Physics\n\n$$Q = m \\cdot c \\cdot \\Delta T$$\n\n1. Langkah pertama\n2. Langkah kedua"
    tree = StructuralExtractor().extract(raw_md, "physics.md")
    candidates = UnitNormalizer().normalize(tree)
    classifier = LocalClassifier()
    classified = classifier.classify(candidates)

    types = [c.content_type for c in classified]
    assert ContentType.FORMULA in types or ContentType.PROCEDURE in types


@pytest.mark.asyncio
async def test_stage4_ambiguity_resolver_offline_fallback():
    raw_md = "# Intro\n\nParagraph text clear\n\nAmbiguous statement without keywords"
    tree = StructuralExtractor().extract(raw_md, "intro.md")
    candidates = UnitNormalizer().normalize(tree)
    classified = LocalClassifier().classify(candidates)

    resolver = AmbiguityResolver(provider=OfflineMockResolutionProvider())
    resolved = await resolver.resolve(classified)

    assert len(resolved) == len(classified)
    assert all(r.final_confidence >= 0.5 for r in resolved)


def test_stage5_payload_builder_typed_families():
    raw_md = "# Formula Section\n\n$$Q = m \\cdot c \\cdot \\Delta T$$\n\n## Procedure\n1. Tabung A\n2. Tabung B"
    tree = StructuralExtractor().extract(raw_md, "formula.md")
    cands = UnitNormalizer().normalize(tree)
    classified = LocalClassifier().classify(cands)
    builder = PayloadBuilder()

    # Create dummy resolved units
    resolved = [ResolvedUnit(classified_unit=c, final_content_type=c.content_type, final_category=c.category, final_confidence=0.9) for c in classified]

    units = builder.build_units(resolved)
    assert len(units) >= 1
    assert all(u.id.startswith("ku_") for u in units)


def test_stage6_claim_evidence_extractor():
    raw_md = "# Research\n\nHipotesis: Air memiliki kapasitas tinggi.\n\nData: Ketinggian busa 9.5 cm."
    tree = StructuralExtractor().extract(raw_md, "res.md")
    cands = UnitNormalizer().normalize(tree)
    classified = LocalClassifier().classify(cands)
    resolved = [ResolvedUnit(classified_unit=c, final_content_type=c.content_type, final_category=c.category, final_confidence=0.9) for c in classified]
    units = PayloadBuilder().build_units(resolved)

    extractor = ClaimEvidenceExtractor()
    associations = extractor.extract(units)

    assert isinstance(associations.associations, list)


def test_stage7_relationship_inferencer():
    raw_md = "# Physics\n\nTeori Kalor.\n\n$$Q = m \\cdot c \\cdot \\Delta T$$"
    tree = StructuralExtractor().extract(raw_md, "phys.md")
    cands = UnitNormalizer().normalize(tree)
    classified = LocalClassifier().classify(cands)
    resolved = [ResolvedUnit(classified_unit=c, final_content_type=c.content_type, final_category=c.category, final_confidence=0.9) for c in classified]
    units = PayloadBuilder().build_units(resolved)
    claim_ev = ClaimEvidenceExtractor().extract(units)

    inferencer = RelationshipInferencer()
    edges = inferencer.infer(units, claim_ev)

    assert isinstance(edges, list)
    assert all(e.evidence.origin is not None for e in edges)


def test_stage8_importance_analyzer():
    raw_md = "# Physics\n\nTeori Utama Kalor.\n\nContoh Sejarah."
    tree = StructuralExtractor().extract(raw_md, "phys.md")
    cands = UnitNormalizer().normalize(tree)
    classified = LocalClassifier().classify(cands)
    resolved = [ResolvedUnit(classified_unit=c, final_content_type=c.content_type, final_category=c.category, final_confidence=0.9) for c in classified]
    units = PayloadBuilder().build_units(resolved)
    edges = RelationshipInferencer().infer(units, ClaimEvidenceExtractor().extract(units))

    analyzer = ImportanceAnalyzer()
    scored_units = analyzer.analyze(units, edges)

    assert len(scored_units) == len(units)
    assert all(hasattr(u, "intrinsic_importance") for u in scored_units)


def test_stage9_manifest_assembler_immutability():
    raw_md = "# Title\n\nContent"
    tree = StructuralExtractor().extract(raw_md, "title.md")
    cands = UnitNormalizer().normalize(tree)
    classified = LocalClassifier().classify(cands)
    resolved = [ResolvedUnit(classified_unit=c, final_content_type=c.content_type, final_category=c.category, final_confidence=0.9) for c in classified]
    units = PayloadBuilder().build_units(resolved)

    assembler = ManifestAssembler()
    manifest = assembler.assemble(
        manifest_id="man_test",
        document_title="Title",
        domain="physics",
        units=units,
        relationships=[],
    )

    assert manifest.manifest_id == "man_test"
    # Verify Pydantic frozen immutability
    with pytest.raises(ValidationError):
        manifest.document_title = "New Title"
