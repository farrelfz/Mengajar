"""
Comprehensive Unit Test Suite for Phase 1C — Universal Artifact Transformation Contract.

30+ test cases covering Intent, Selection, Transformers, Differentiation Validation,
Traceability, Serialization, and Negative/Adversarial integrity.
"""

import json
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
from app.intelligence.transformation import (
    ArtifactBlueprint,
    ArtifactDifferentiationValidator,
    ArtifactType,
    HandoutBlueprint,
    HandoutTransformer,
    KnowledgeSelectionEngine,
    LearningActivityType,
    PresentationBlueprint,
    PresentationTransformer,
    ResolvedArtifactIntent,
    ScientificDocumentBlueprint,
    ScientificDocumentTransformer,
    TransformationTraceabilityEngine,
    UncertaintyHandlingPolicy,
    WorksheetBlueprint,
    WorksheetTransformer,
    get_default_intent,
)


@pytest.fixture
def sample_manifest() -> UniversalKnowledgeManifest:
    raw_md = """# Physics Overview

## Definition
Kalor adalah bentuk energi yang berpindah dari benda bersuhu tinggi ke suhu rendah.

## Formula
$$Q = m \\cdot c \\cdot \\Delta T$$

## Procedure
1. Ukur massa benda.
2. Catat suhu awal.
3. Panaskan dan catat suhu akhir.

## Ambiguous Statement
Pernyataan tanpa kata kunci kontekstual yang jelas.
"""
    compiler = KnowledgeCompiler(resolution_provider=OfflineMockResolutionProvider())
    import asyncio
    manifest = asyncio.run(compiler.compile(raw_md, source_filename="physics.md"))
    return manifest


# ============================================================================
# PART 1 — ARTIFACT INTENT TESTS
# ============================================================================

def test_01_presentation_intent_resolves_correctly():
    intent = get_default_intent(ArtifactType.PRESENTATION)
    assert intent.artifact_type == ArtifactType.PRESENTATION
    assert intent.information_density <= 0.40
    assert intent.narrative_mode == "PROGRESSIVE_REVEAL"
    assert intent.uncertainty_policy == UncertaintyHandlingPolicy.EXCLUDE_UNRESOLVED


def test_02_handout_intent_resolves_correctly():
    intent = get_default_intent(ArtifactType.HANDOUT)
    assert intent.artifact_type == ArtifactType.HANDOUT
    assert intent.information_density >= 0.65
    assert intent.narrative_mode == "HIERARCHICAL_EXPLANATORY"
    assert intent.uncertainty_policy == UncertaintyHandlingPolicy.FLAG_FOR_CLARIFICATION


def test_03_worksheet_intent_resolves_correctly():
    intent = get_default_intent(ArtifactType.WORKSHEET)
    assert intent.artifact_type == ArtifactType.WORKSHEET
    assert intent.interaction_level >= 0.80
    assert intent.narrative_mode == "GUIDED_DISCOVERY"


def test_04_scientific_intent_resolves_correctly():
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    assert intent.artifact_type == ArtifactType.SCIENTIFIC_DOCUMENT
    assert intent.evidence_requirement >= 0.90
    assert intent.uncertainty_policy == UncertaintyHandlingPolicy.ISOLATE_AS_LIMITATION


# ============================================================================
# PART 2 — KNOWLEDGE SELECTION TESTS
# ============================================================================

def test_05_critical_knowledge_selected(sample_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    selection = engine.select(sample_manifest, intent)

    assert len(selection.selected_units) > 0
    assert all(uid in sample_manifest.units for uid in selection.selected_unit_ids)


def test_06_low_importance_knowledge_filtered_appropriately(sample_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION, {"min_importance_threshold": "HIGH"})
    selection = engine.select(sample_manifest, intent)

    for uid in selection.selected_unit_ids:
        unit = selection.selected_units[uid]
        assert unit.intrinsic_importance in (IntrinsicImportance.FOUNDATIONAL, IntrinsicImportance.CENTRAL)


def test_07_unresolved_offline_knowledge_handled_conservatively(sample_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION, {"uncertainty_policy": UncertaintyHandlingPolicy.EXCLUDE_UNRESOLVED})
    selection = engine.select(sample_manifest, intent)

    for uid in selection.selected_unit_ids:
        unit = selection.selected_units[uid]
        assert unit.resolution_status != ResolutionStatus.UNRESOLVED_OFFLINE


def test_08_selection_traceability_preserved(sample_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.HANDOUT)
    selection = engine.select(sample_manifest, intent)

    assert "total_source_units" in selection.traceability_metadata
    assert selection.traceability_metadata["total_source_units"] == len(sample_manifest.units)


# ============================================================================
# PART 3 — PRESENTATION TRANSFORMER TESTS
# ============================================================================

def test_09_presentation_produces_conceptual_beats(sample_manifest):
    intent = get_default_intent(ArtifactType.PRESENTATION)
    selection = KnowledgeSelectionEngine().select(sample_manifest, intent)
    bp = PresentationTransformer().transform(sample_manifest, selection, intent)

    assert isinstance(bp, PresentationBlueprint)
    assert len(bp.beats) > 0


def test_10_presentation_compression_occurs(sample_manifest):
    intent = get_default_intent(ArtifactType.PRESENTATION)
    selection = KnowledgeSelectionEngine().select(sample_manifest, intent)
    bp = PresentationTransformer().transform(sample_manifest, selection, intent)

    assert len(bp.beats) <= len(sample_manifest.units)


def test_11_presentation_narrative_order_preserved(sample_manifest):
    intent = get_default_intent(ArtifactType.PRESENTATION)
    selection = KnowledgeSelectionEngine().select(sample_manifest, intent)
    bp = PresentationTransformer().transform(sample_manifest, selection, intent)

    indices = [b.sequence_index for b in bp.beats]
    assert indices == list(range(1, len(bp.beats) + 1))


def test_12_presentation_cognitive_load_metadata_exists(sample_manifest):
    intent = get_default_intent(ArtifactType.PRESENTATION)
    selection = KnowledgeSelectionEngine().select(sample_manifest, intent)
    bp = PresentationTransformer().transform(sample_manifest, selection, intent)

    for beat in bp.beats:
        assert 0.0 <= beat.cognitive_load_target <= 1.0


# ============================================================================
# PART 4 — HANDOUT TRANSFORMER TESTS
# ============================================================================

def test_13_handout_produces_explanatory_sections(sample_manifest):
    intent = get_default_intent(ArtifactType.HANDOUT)
    selection = KnowledgeSelectionEngine().select(sample_manifest, intent)
    bp = HandoutTransformer().transform(sample_manifest, selection, intent)

    assert isinstance(bp, HandoutBlueprint)
    assert len(bp.sections) > 0


def test_14_handout_supporting_context_retained(sample_manifest):
    intent = get_default_intent(ArtifactType.HANDOUT)
    selection = KnowledgeSelectionEngine().select(sample_manifest, intent)
    bp = HandoutTransformer().transform(sample_manifest, selection, intent)

    total_section_uids = sum(len(s.knowledge_unit_ids) for s in bp.sections)
    assert total_section_uids >= len(selection.selected_unit_ids)


def test_15_handout_hierarchical_structure_preserved(sample_manifest):
    intent = get_default_intent(ArtifactType.HANDOUT)
    selection = KnowledgeSelectionEngine().select(sample_manifest, intent)
    bp = HandoutTransformer().transform(sample_manifest, selection, intent)

    assert any(s.heading_level in (1, 2) for s in bp.sections)


# ============================================================================
# PART 5 — WORKSHEET TRANSFORMER TESTS
# ============================================================================

def test_16_worksheet_produces_active_learning_activities(sample_manifest):
    intent = get_default_intent(ArtifactType.WORKSHEET)
    selection = KnowledgeSelectionEngine().select(sample_manifest, intent)
    bp = WorksheetTransformer().transform(sample_manifest, selection, intent)

    assert isinstance(bp, WorksheetBlueprint)
    assert len(bp.activities) > 0


def test_17_worksheet_questions_map_to_knowledge_targets(sample_manifest):
    intent = get_default_intent(ArtifactType.WORKSHEET)
    selection = KnowledgeSelectionEngine().select(sample_manifest, intent)
    bp = WorksheetTransformer().transform(sample_manifest, selection, intent)

    for act in bp.activities:
        assert len(act.target_knowledge_unit_ids) > 0


def test_18_worksheet_withholds_explanation_answers(sample_manifest):
    intent = get_default_intent(ArtifactType.WORKSHEET)
    selection = KnowledgeSelectionEngine().select(sample_manifest, intent)
    bp = WorksheetTransformer().transform(sample_manifest, selection, intent)

    for act in bp.activities:
        assert act.withhold_explanation is True


# ============================================================================
# PART 6 — SCIENTIFIC DOCUMENT TRANSFORMER TESTS
# ============================================================================

def test_19_scientific_claim_evidence_traceability_preserved(sample_manifest):
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    selection = KnowledgeSelectionEngine().select(sample_manifest, intent)
    bp = ScientificDocumentTransformer().transform(sample_manifest, selection, intent)

    assert isinstance(bp, ScientificDocumentBlueprint)
    assert len(bp.arguments) > 0


def test_20_unsupported_evidence_cannot_be_fabricated(sample_manifest):
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    selection = KnowledgeSelectionEngine().select(sample_manifest, intent)
    bp = ScientificDocumentTransformer().transform(sample_manifest, selection, intent)

    manifest_rel_ids = set(r.relationship_id for r in sample_manifest.relationships)
    for arg in bp.arguments:
        for rel_id in arg.evidence_relationship_ids:
            assert rel_id in manifest_rel_ids


def test_21_scientific_argument_structure_explicit(sample_manifest):
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    selection = KnowledgeSelectionEngine().select(sample_manifest, intent)
    bp = ScientificDocumentTransformer().transform(sample_manifest, selection, intent)

    for arg in bp.arguments:
        assert arg.argument_role is not None


# ============================================================================
# PART 7 — DIFFERENTIATION VALIDATION TESTS
# ============================================================================

def test_22_to_25_all_four_blueprints_differ_semantically(sample_manifest):
    engine = KnowledgeSelectionEngine()

    p_intent = get_default_intent(ArtifactType.PRESENTATION)
    h_intent = get_default_intent(ArtifactType.HANDOUT)
    w_intent = get_default_intent(ArtifactType.WORKSHEET)
    s_intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)

    p_bp = PresentationTransformer().transform(sample_manifest, engine.select(sample_manifest, p_intent), p_intent)
    h_bp = HandoutTransformer().transform(sample_manifest, engine.select(sample_manifest, h_intent), h_intent)
    w_bp = WorksheetTransformer().transform(sample_manifest, engine.select(sample_manifest, w_intent), w_intent)
    s_bp = ScientificDocumentTransformer().transform(sample_manifest, engine.select(sample_manifest, s_intent), s_intent)

    validator = ArtifactDifferentiationValidator()
    res = validator.validate(p_bp, h_bp, w_bp, s_bp)

    assert res.is_differentiated is True
    assert len(res.violations) == 0


# ============================================================================
# PART 8 — TRACEABILITY AND INTEGRITY TESTS
# ============================================================================

def test_26_no_orphan_blueprint_elements(sample_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    bp = PresentationTransformer().transform(sample_manifest, engine.select(sample_manifest, intent), intent)

    trace = TransformationTraceabilityEngine().verify_traceability(bp, sample_manifest)
    assert trace.is_fully_traceable is True
    assert trace.orphan_element_count == 0


def test_27_all_references_resolve(sample_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    bp = ScientificDocumentTransformer().transform(sample_manifest, engine.select(sample_manifest, intent), intent)

    trace = TransformationTraceabilityEngine().verify_traceability(bp, sample_manifest)
    assert len(trace.unresolved_unit_references) == 0


def test_28_serialization_roundtrip(sample_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    bp = PresentationTransformer().transform(sample_manifest, engine.select(sample_manifest, intent), intent)

    json_str = bp.model_dump_json()
    reconstructed = PresentationBlueprint.model_validate_json(json_str)

    assert reconstructed.blueprint_id == bp.blueprint_id
    assert len(reconstructed.beats) == len(bp.beats)


def test_29_deterministic_repeated_compilation(sample_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.WORKSHEET)

    bp1 = WorksheetTransformer().transform(sample_manifest, engine.select(sample_manifest, intent), intent)
    bp2 = WorksheetTransformer().transform(sample_manifest, engine.select(sample_manifest, intent), intent)

    assert bp1.model_dump(exclude={"created_at"}) == bp2.model_dump(exclude={"created_at"})


def test_30_invalid_artifact_intent_rejected():
    with pytest.raises(ValidationError):
        ResolvedArtifactIntent(
            artifact_type="INVALID_ARTIFACT_TYPE",  # Invalid enum
            primary_goal="Test",
            depth="TEST",
            information_density=1.5,  # > 1.0 invalid
            interaction_level=0.5,
            evidence_requirement=0.5,
            narrative_mode="TEST",
            compression_strategy="TEST",
            sequencing_strategy="TEST",
            knowledge_selection_policy="TEST",
        )
