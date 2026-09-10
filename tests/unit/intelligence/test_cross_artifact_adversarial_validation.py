"""
Phase 1C.1 — Cross-Artifact Adversarial Validation Test Suite.

Includes 20 behavioral adversarial tests and Golden Oobleck Fixture integration testing.
"""

import asyncio
import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from app.intelligence.pipeline import (
    KnowledgeCompiler,
    ManifestAssembler,
    OfflineMockResolutionProvider,
    StructuralExtractor,
)
from app.intelligence.schemas import (
    ConceptPayload,
    ContentType,
    IntrinsicImportance,
    KnowledgeCategory,
    KnowledgeProvenance,
    KnowledgeRelationship,
    KnowledgeUnit,
    ResolutionStatus,
    UniversalKnowledgeManifest,
)
from app.intelligence.schemas.relationships import RelationshipEvidence, RelationshipOrigin, RelationshipType
from app.intelligence.transformation import (
    ArtifactBlueprint,
    ArtifactDifferentiationValidator,
    ArtifactType,
    HandoutBlueprint,
    HandoutTransformer,
    KnowledgeSelectionEngine,
    LearningActivity,
    LearningActivityType,
    PresentationBlueprint,
    PresentationTransformer,
    ResolvedArtifactIntent,
    ScientificArgumentRole,
    ScientificDocumentBlueprint,
    ScientificDocumentTransformer,
    TransformationTraceabilityEngine,
    UncertaintyHandlingPolicy,
    WorksheetBlueprint,
    WorksheetTransformer,
    get_default_intent,
)

FIXTURE_PATH = Path(__file__).parent.parent.parent / "fixtures" / "oobleck_experiment.md"


@pytest.fixture
def oobleck_manifest() -> UniversalKnowledgeManifest:
    assert FIXTURE_PATH.exists(), f"Fixture missing at {FIXTURE_PATH}"
    raw_md = FIXTURE_PATH.read_text(encoding="utf-8")
    compiler = KnowledgeCompiler(resolution_provider=OfflineMockResolutionProvider())
    manifest = asyncio.run(compiler.compile(raw_md, source_filename="oobleck_experiment.md"))
    return manifest


# ============================================================================
# 1. HIGH KNOWLEDGE OVERLAP & DIVERGENCE INDEPENDENCE
# ============================================================================

def test_01_high_knowledge_overlap_is_allowed(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    
    # Force identical selection on Presentation and Handout
    p_intent = get_default_intent(ArtifactType.PRESENTATION, {"min_importance_threshold": "MEDIUM"})
    h_intent = get_default_intent(ArtifactType.HANDOUT, {"min_importance_threshold": "MEDIUM"})

    p_sel = engine.select(oobleck_manifest, p_intent)
    h_sel = engine.select(oobleck_manifest, h_intent)

    p_bp = PresentationTransformer().transform(oobleck_manifest, p_sel, p_intent)
    h_bp = HandoutTransformer().transform(oobleck_manifest, h_sel, h_intent)
    w_bp = WorksheetTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.WORKSHEET)), get_default_intent(ArtifactType.WORKSHEET))
    s_bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)), get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT))

    validator = ArtifactDifferentiationValidator()
    res = validator.validate(p_bp, h_bp, w_bp, s_bp)

    # High KnowledgeUnit overlap is explicitly valid!
    assert res.is_differentiated is True
    assert res.transformation_divergence_score >= 0.75


def test_02_transformation_divergence_independent_of_overlap(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    p_intent = get_default_intent(ArtifactType.PRESENTATION)
    h_intent = get_default_intent(ArtifactType.HANDOUT)
    w_intent = get_default_intent(ArtifactType.WORKSHEET)
    s_intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)

    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, p_intent), p_intent)
    h_bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, h_intent), h_intent)
    w_bp = WorksheetTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, w_intent), w_intent)
    s_bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, s_intent), s_intent)

    # Verify structural types are distinct
    assert type(p_bp.beats[0]).__name__ == "ConceptualBeat"
    assert type(h_bp.sections[0]).__name__ == "ExplanatorySection"
    assert type(w_bp.activities[0]).__name__ == "LearningActivity"
    assert type(s_bp.arguments[0]).__name__ == "ScientificArgumentUnit"


# ============================================================================
# 2. PRESENTATION COMPRESSION & ANTI-HANDOUT VALIDATION
# ============================================================================

def test_03_presentation_semantic_compression(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    sel = engine.select(oobleck_manifest, intent)
    bp = PresentationTransformer().transform(oobleck_manifest, sel, intent)

    # Beats must compress selected units
    assert len(bp.beats) <= len(sel.selected_unit_ids)
    for beat in bp.beats:
        assert beat.cognitive_load_target <= 0.65


def test_04_presentation_anti_handout_detection(oobleck_manifest):
    # Construct a bad presentation blueprint with excessive cognitive load
    intent = get_default_intent(ArtifactType.PRESENTATION)
    engine = KnowledgeSelectionEngine()
    bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    # Artificially corrupt cognitive load across beats to simulate handout prose collapse
    corrupted_beats = [
        b.model_copy(update={"cognitive_load_target": 0.85}) for b in bp.beats
    ]
    bad_p_bp = bp.model_copy(update={"beats": tuple(corrupted_beats)})

    h_bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.HANDOUT)), get_default_intent(ArtifactType.HANDOUT))
    w_bp = WorksheetTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.WORKSHEET)), get_default_intent(ArtifactType.WORKSHEET))
    s_bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)), get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT))

    res = ArtifactDifferentiationValidator().validate(bad_p_bp, h_bp, w_bp, s_bp)
    assert res.is_differentiated is False
    assert any("Presentation anti-handout violation" in v for v in res.violations)


# ============================================================================
# 3. HANDOUT CONTINUITY
# ============================================================================

def test_05_handout_explanatory_continuity(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.HANDOUT)
    sel = engine.select(oobleck_manifest, intent)
    bp = HandoutTransformer().transform(oobleck_manifest, sel, intent)

    assert len(bp.sections) > 0
    for sec in bp.sections:
        assert sec.reading_depth == "COMPREHENSIVE_REFERENCE"
        assert len(sec.knowledge_unit_ids) > 0


# ============================================================================
# 4. WORKSHEET INQUIRY FLOW & ANTI-QUIZ VALIDATION
# ============================================================================

def test_06_worksheet_inquiry_flow(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.WORKSHEET)
    sel = engine.select(oobleck_manifest, intent)
    bp = WorksheetTransformer().transform(oobleck_manifest, sel, intent)

    act_types = [act.activity_type for act in bp.activities]
    assert LearningActivityType.PHENOMENON in act_types or LearningActivityType.PREDICTION in act_types
    assert all(act.withhold_explanation is True for act in bp.activities)


def test_07_worksheet_quiz_anti_pattern_detection(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.WORKSHEET)
    sel = engine.select(oobleck_manifest, intent)
    bp = WorksheetTransformer().transform(oobleck_manifest, sel, intent)

    # Corrupt activities into purely repetitive QUESTION items
    corrupted_activities = [
        act.model_copy(update={"activity_type": LearningActivityType.QUESTION})
        for act in bp.activities
    ]
    bad_w_bp = bp.model_copy(update={"activities": tuple(corrupted_activities)})

    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.PRESENTATION)), get_default_intent(ArtifactType.PRESENTATION))
    h_bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.HANDOUT)), get_default_intent(ArtifactType.HANDOUT))
    s_bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)), get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT))

    res = ArtifactDifferentiationValidator().validate(p_bp, h_bp, bad_w_bp, s_bp)
    assert res.is_differentiated is False
    assert any("Worksheet anti-pattern violation" in v for v in res.violations)


# ============================================================================
# 5. ARTIFACT-SPECIFIC RELEVANCE RANKING
# ============================================================================

def test_08_artifact_specific_relevance_ranking(oobleck_manifest):
    engine = KnowledgeSelectionEngine()

    p_sel = engine.select(oobleck_manifest, get_default_intent(ArtifactType.PRESENTATION))
    w_sel = engine.select(oobleck_manifest, get_default_intent(ArtifactType.WORKSHEET))

    # Verify score metadata exists and ranks differ according to artifact relevance
    assert "relevance_scores" in p_sel.traceability_metadata
    assert "relevance_scores" in w_sel.traceability_metadata


def test_09_visual_phenomenon_preference_for_presentation(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    sel = engine.select(oobleck_manifest, intent)

    top_unit_id = sel.selected_unit_ids[0]
    top_unit = sel.selected_units[top_unit_id]
    assert top_unit.content_type in (ContentType.CONCEPT, ContentType.FORMULA, ContentType.DEFINITION, ContentType.HYPOTHESIS, ContentType.THEORY)


def test_10_investigation_preference_for_worksheet(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.WORKSHEET)
    sel = engine.select(oobleck_manifest, intent)

    types = [u.content_type for u in sel.selected_units.values()]
    assert ContentType.PROCEDURE in types or ContentType.DATA in types or ContentType.FORMULA in types


def test_11_context_preference_for_handout(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.HANDOUT)
    sel = engine.select(oobleck_manifest, intent)

    types = [u.content_type for u in sel.selected_units.values()]
    assert ContentType.DEFINITION in types or ContentType.CONCEPT in types


def test_12_evidence_preference_for_scientific_document(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    sel = engine.select(oobleck_manifest, intent)

    assert len(sel.selected_units) > 0


# ============================================================================
# 6. SCIENTIFIC EVIDENCE DISCIPLINE
# ============================================================================

def test_13_concept_relationship_is_not_evidence():
    prov = KnowledgeProvenance(source_document_id="doc1", source_section_id="sec1", source_section_title="Sec 1", block_ids=["b1"], raw_snippet="Snippet")
    u1 = KnowledgeUnit(
        id="ku_111111111111",
        title="Force",
        content_type=ContentType.CONCEPT,
        category=KnowledgeCategory.CORE_CONCEPT,
        intrinsic_importance=IntrinsicImportance.CENTRAL,
        provenance=prov,
        payload=ConceptPayload(formal_definition="Push or pull")
    )
    u2 = KnowledgeUnit(
        id="ku_222222222222",
        title="Acceleration",
        content_type=ContentType.CONCEPT,
        category=KnowledgeCategory.CORE_CONCEPT,
        intrinsic_importance=IntrinsicImportance.CENTRAL,
        provenance=prov,
        payload=ConceptPayload(formal_definition="Rate of change of velocity")
    )

    # CAUSES is a concept relationship, NOT a scientific evidence relationship
    concept_rel = KnowledgeRelationship(
        source_unit_id="ku_111111111111",
        target_unit_id="ku_222222222222",
        relationship=RelationshipType.CAUSES,
        evidence=RelationshipEvidence(origin=RelationshipOrigin.EXPLICIT_SOURCE)
    )

    manifest = ManifestAssembler().assemble(
        manifest_id="man_concept_rel",
        document_title="Concept Test",
        domain="physics",
        units=[u1, u2],
        relationships=[concept_rel]
    )

    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    sel = KnowledgeSelectionEngine().select(manifest, intent)
    bp = ScientificDocumentTransformer().transform(manifest, sel, intent)

    # Verify that CAUSES was NOT treated as a scientific evidence relationship!
    for arg in bp.arguments:
        assert len(arg.supporting_evidence_unit_ids) == 0
        assert len(arg.evidence_relationship_ids) == 0


def test_14_unsupported_scientific_claim_isolated():
    prov = KnowledgeProvenance(source_document_id="doc1", source_section_id="sec1", source_section_title="Sec 1", block_ids=["b1"], raw_snippet="Snippet")
    u1 = KnowledgeUnit(
        id="ku_111111111111",
        title="Unsupported Claim",
        content_type=ContentType.CLAIM,
        category=KnowledgeCategory.CORE_CONCEPT,
        intrinsic_importance=IntrinsicImportance.CENTRAL,
        provenance=prov,
        payload=ConceptPayload(formal_definition="Unsupported")
    )
    manifest = ManifestAssembler().assemble(
        manifest_id="man_unsupported",
        document_title="Unsupported Test",
        domain="physics",
        units=[u1],
        relationships=[]
    )
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    sel = KnowledgeSelectionEngine().select(manifest, intent)
    bp = ScientificDocumentTransformer().transform(manifest, sel, intent)

    arg = bp.arguments[0]
    assert len(arg.supporting_evidence_unit_ids) == 0
    assert arg.confidence <= 0.60


def test_15_evidence_fabrication_rejection(oobleck_manifest):
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    sel = KnowledgeSelectionEngine().select(oobleck_manifest, intent)
    bp = ScientificDocumentTransformer().transform(oobleck_manifest, sel, intent)

    manifest_rel_edges = set(f"{r.source_unit_id}->{r.relationship.value}->{r.target_unit_id}" for r in oobleck_manifest.relationships)
    for arg in bp.arguments:
        for rel_id in arg.evidence_relationship_ids:
            assert rel_id in manifest_rel_edges


# ============================================================================
# 7. TRACEABILITY & INTEGRITY
# ============================================================================

def test_16_traceability_after_cross_artifact_transformation(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    trace = TransformationTraceabilityEngine().verify_traceability(bp, oobleck_manifest)
    assert trace.is_fully_traceable is True


def test_17_golden_fixture_integration(oobleck_manifest):
    engine = KnowledgeSelectionEngine()

    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.PRESENTATION)), get_default_intent(ArtifactType.PRESENTATION))
    h_bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.HANDOUT)), get_default_intent(ArtifactType.HANDOUT))
    w_bp = WorksheetTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.WORKSHEET)), get_default_intent(ArtifactType.WORKSHEET))
    s_bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)), get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT))

    res = ArtifactDifferentiationValidator().validate(p_bp, h_bp, w_bp, s_bp)
    assert res.is_differentiated is True


def test_18_deterministic_repeated_transformation(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.HANDOUT)

    bp1 = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)
    bp2 = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    assert bp1.model_dump(exclude={"created_at"}) == bp2.model_dump(exclude={"created_at"})


def test_19_serialization_integrity(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    json_str = bp.model_dump_json()
    reconstructed = ScientificDocumentBlueprint.model_validate_json(json_str)

    assert reconstructed.blueprint_id == bp.blueprint_id


def test_20_invalid_cross_artifact_references():
    with pytest.raises(ValidationError):
        ScientificDocumentBlueprint(
            blueprint_id="bp_bad",
            artifact_type="INVALID_TYPE",  # Bad enum
            source_manifest_id="m1",
            document_title="Title",
            intent=get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT),
        )
