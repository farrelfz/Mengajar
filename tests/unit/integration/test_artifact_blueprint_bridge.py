"""
Comprehensive Unit Test Suite for Phase 1D — Artifact Blueprint Bridge Integration.

28+ test cases covering Base contract, Presentation bridge, Handout bridge, Worksheet bridge,
Scientific document bridge, Traceability invariants, Cross-artifact render contract differentiation,
and Golden Fixture Dry Run (oobleck_experiment.md).
"""

import asyncio
from pathlib import Path
import pytest
from pydantic import ValidationError

from app.intelligence.pipeline import (
    KnowledgeCompiler,
    OfflineMockResolutionProvider,
    StructuralExtractor,
)
from app.intelligence.schemas import UniversalKnowledgeManifest
from app.intelligence.transformation import (
    ArtifactType,
    HandoutBlueprint,
    HandoutTransformer,
    KnowledgeSelectionEngine,
    PresentationBlueprint,
    PresentationTransformer,
    ScientificDocumentBlueprint,
    ScientificDocumentTransformer,
    WorksheetBlueprint,
    WorksheetTransformer,
    get_default_intent,
)
from app.integration.artifact_bridge import (
    ArtifactBridgeValidator,
    HandoutBlueprintBridge,
    PresentationBlueprintBridge,
    RenderArtifact,
    ScientificDocumentBlueprintBridge,
    WorksheetBlueprintBridge,
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
# 1. BASE CONTRACT TESTS
# ============================================================================

def test_01_invalid_blueprint_rejection(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.HANDOUT)
    handout_bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    bridge = PresentationBlueprintBridge()
    with pytest.raises(TypeError):
        bridge.bridge(handout_bp)  # Passing HandoutBlueprint to PresentationBlueprintBridge


def test_02_deterministic_transformation(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    bridge = PresentationBlueprintBridge()
    r1 = bridge.bridge(p_bp)
    r2 = bridge.bridge(p_bp)

    assert r1.model_dump(exclude={"created_at"}) == r2.model_dump(exclude={"created_at"})


def test_03_serialization_integrity(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = PresentationBlueprintBridge().bridge(p_bp)
    json_str = r_art.model_dump_json()
    reconstructed = RenderArtifact.model_validate_json(json_str)

    assert reconstructed.artifact_id == r_art.artifact_id
    assert len(reconstructed.units) == len(r_art.units)


# ============================================================================
# 2. PRESENTATION BRIDGE TESTS
# ============================================================================

def test_04_presentation_beat_mapping(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = PresentationBlueprintBridge().bridge(p_bp)
    assert r_art.artifact_type == "PRESENTATION"
    assert len(r_art.units) == len(p_bp.beats)


def test_05_presentation_semantic_ordering_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = PresentationBlueprintBridge().bridge(p_bp)
    indices = [u.sequence_index for u in r_art.units]
    assert indices == list(range(1, len(p_bp.beats) + 1))


def test_06_presentation_progressive_sequence_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = PresentationBlueprintBridge().bridge(p_bp)
    for u in r_art.units:
        assert "narrative_function" in u.semantic_metadata


def test_07_presentation_cognitive_metadata_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = PresentationBlueprintBridge().bridge(p_bp)
    for u in r_art.units:
        assert "cognitive_load_target" in u.semantic_metadata
        assert 0.0 <= u.semantic_metadata["cognitive_load_target"] <= 1.0


def test_08_presentation_visual_priority_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = PresentationBlueprintBridge().bridge(p_bp)
    for u in r_art.units:
        assert "visual_priority" in u.semantic_metadata


# ============================================================================
# 3. HANDOUT BRIDGE TESTS
# ============================================================================

def test_09_handout_hierarchy_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.HANDOUT)
    h_bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = HandoutBlueprintBridge().bridge(h_bp)
    assert r_art.artifact_type == "HANDOUT"
    for u in r_art.units:
        assert "heading_level" in u.semantic_metadata


def test_10_handout_definitions_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.HANDOUT)
    h_bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = HandoutBlueprintBridge().bridge(h_bp)
    for u in r_art.units:
        assert "definitions_count" in u.semantic_metadata


def test_11_handout_examples_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.HANDOUT)
    h_bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = HandoutBlueprintBridge().bridge(h_bp)
    for u in r_art.units:
        assert "examples_count" in u.semantic_metadata


def test_12_handout_continuity_metadata_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.HANDOUT)
    h_bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = HandoutBlueprintBridge().bridge(h_bp)
    for u in r_art.units:
        assert u.semantic_metadata.get("reading_depth") == "COMPREHENSIVE_REFERENCE"


# ============================================================================
# 4. WORKSHEET BRIDGE TESTS
# ============================================================================

def test_13_worksheet_activity_types_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.WORKSHEET)
    w_bp = WorksheetTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = WorksheetBlueprintBridge().bridge(w_bp)
    assert r_art.artifact_type == "WORKSHEET"
    for u in r_art.units:
        assert "inquiry_activity_type" in u.semantic_metadata


def test_14_worksheet_inquiry_ordering_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.WORKSHEET)
    w_bp = WorksheetTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = WorksheetBlueprintBridge().bridge(w_bp)
    indices = [u.sequence_index for u in r_art.units]
    assert indices == list(range(1, len(w_bp.activities) + 1))


def test_15_worksheet_withheld_explanation_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.WORKSHEET)
    w_bp = WorksheetTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = WorksheetBlueprintBridge().bridge(w_bp)
    for u in r_art.units:
        assert u.semantic_metadata.get("withhold_explanation") is True


def test_16_worksheet_activity_not_flattened_to_paragraph(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.WORKSHEET)
    w_bp = WorksheetTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = WorksheetBlueprintBridge().bridge(w_bp)
    for u in r_art.units:
        assert u.role == "LEARNING_ACTIVITY"
        assert u.semantic_metadata.get("requires_student_workspace") is True


# ============================================================================
# 5. SCIENTIFIC DOCUMENT BRIDGE TESTS
# ============================================================================

def test_17_scientific_claim_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    s_bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = ScientificDocumentBlueprintBridge().bridge(s_bp)
    assert r_art.artifact_type == "SCIENTIFIC_DOCUMENT"
    for u in r_art.units:
        assert u.role == "SCIENTIFIC_ARGUMENT"
        assert "claim_unit_id" in u.semantic_metadata


def test_18_scientific_evidence_relationship_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    s_bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = ScientificDocumentBlueprintBridge().bridge(s_bp)
    for u in r_art.units:
        assert "evidence_relationship_ids" in u.semantic_metadata


def test_19_scientific_unsupported_evidence_rejected(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    s_bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = ScientificDocumentBlueprintBridge().bridge(s_bp)
    for u in r_art.units:
        assert "confidence" in u.semantic_metadata

    # Corrupted argument with ungrounded / unsupported evidence is strictly rejected
    from app.intelligence.transformation.blueprints import ScientificArgumentRole, ScientificArgumentUnit
    fake_arg = ScientificArgumentUnit(
        argument_id="arg_fake_unsupported",
        sequence_index=99,
        claim_unit_id="ku_claim",
        argument_role=ScientificArgumentRole.EMPIRICAL_EVIDENCE,
        claim_statement="Unproven fabricated claim",
        supporting_evidence_unit_ids=("ku_fabricated_evidence_unit",),  # Not in knowledge_unit_ids!
        evidence_relationship_ids=(),
        counter_considerations=(),
        confidence=0.1,
        source_traceability=(),
        knowledge_unit_ids=("ku_claim",),  # ku_fabricated_evidence_unit is missing
    )
    bad_bp = ScientificDocumentBlueprint(
        blueprint_id="bp_bad_sci",
        artifact_type=ArtifactType.SCIENTIFIC_DOCUMENT,
        source_manifest_id=s_bp.source_manifest_id,
        document_title="Bad Sci Doc",
        intent=intent,
        arguments=(fake_arg,),
    )
    with pytest.raises(ValueError, match="Unsupported evidence rejected"):
        ScientificDocumentBlueprintBridge().bridge(bad_bp)


def test_20_scientific_limitations_preserved(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    s_bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = ScientificDocumentBlueprintBridge().bridge(s_bp)
    for u in r_art.units:
        assert "counter_considerations" in u.semantic_metadata


# ============================================================================
# 6. TRACEABILITY & VALIDATION TESTS
# ============================================================================

def test_21_forward_traceability(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = PresentationBlueprintBridge().bridge(p_bp)
    val = ArtifactBridgeValidator().validate(p_bp, r_art)
    assert val.is_valid is True
    assert val.orphan_render_unit_count == 0


def test_22_reverse_traceability(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.WORKSHEET)
    w_bp = WorksheetTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = WorksheetBlueprintBridge().bridge(w_bp)
    for u in r_art.units:
        assert u.traceability_refs.blueprint_element_id is not None
        assert len(u.traceability_refs.knowledge_unit_ids) > 0


def test_23_orphan_detection(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.HANDOUT)
    h_bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = HandoutBlueprintBridge().bridge(h_bp)
    # Corrupt traceability ref to simulate orphan unit
    corrupted_unit = r_art.units[0].model_copy(update={"traceability_refs": None})
    bad_r_art = r_art.model_copy(update={"units": (corrupted_unit,) + r_art.units[1:]})

    val = ArtifactBridgeValidator().validate(h_bp, bad_r_art)
    assert val.is_valid is False
    assert val.orphan_render_unit_count > 0


def test_24_lost_element_detection(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = PresentationBlueprintBridge().bridge(p_bp)
    # Drop first render unit to simulate lost element
    bad_r_art = r_art.model_copy(update={"units": r_art.units[1:]})

    val = ArtifactBridgeValidator().validate(p_bp, bad_r_art)
    assert val.is_valid is False
    assert len(val.lost_blueprint_element_ids) > 0


# ============================================================================
# 7. CROSS ARTIFACT & GOLDEN FIXTURE DRY RUN
# ============================================================================

def test_25_artifact_render_contracts_differ(oobleck_manifest):
    engine = KnowledgeSelectionEngine()

    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.PRESENTATION)), get_default_intent(ArtifactType.PRESENTATION))
    h_bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.HANDOUT)), get_default_intent(ArtifactType.HANDOUT))
    w_bp = WorksheetTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.WORKSHEET)), get_default_intent(ArtifactType.WORKSHEET))
    s_bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)), get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT))

    p_r = PresentationBlueprintBridge().bridge(p_bp)
    h_r = HandoutBlueprintBridge().bridge(h_bp)
    w_r = WorksheetBlueprintBridge().bridge(w_bp)
    s_r = ScientificDocumentBlueprintBridge().bridge(s_bp)

    assert p_r.artifact_type != h_r.artifact_type
    assert w_r.units[0].role == "LEARNING_ACTIVITY"
    assert s_r.units[0].role == "SCIENTIFIC_ARGUMENT"
    assert p_r.units[0].role == "CONCEPTUAL_BEAT"
    assert h_r.units[0].role == "EXPLANATORY_SECTION"


def test_26_shared_knowledge_unit_reuse_remains_valid(oobleck_manifest):
    engine = KnowledgeSelectionEngine()

    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.PRESENTATION)), get_default_intent(ArtifactType.PRESENTATION))
    h_bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, get_default_intent(ArtifactType.HANDOUT)), get_default_intent(ArtifactType.HANDOUT))

    p_r = PresentationBlueprintBridge().bridge(p_bp)
    h_r = HandoutBlueprintBridge().bridge(h_bp)

    p_ku = set(uid for u in p_r.units for uid in u.traceability_refs.knowledge_unit_ids)
    h_ku = set(uid for u in h_r.units for uid in u.traceability_refs.knowledge_unit_ids)

    # Shared knowledge units exist and are valid
    assert len(p_ku.intersection(h_ku)) > 0


def test_27_bridge_does_not_fabricate_content(oobleck_manifest):
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)

    r_art = PresentationBlueprintBridge().bridge(p_bp)
    bp_titles = set(b.title for b in p_bp.beats)
    for u in r_art.units:
        assert u.title in bp_titles


def test_28_bridge_does_not_duplicate_content(oobleck_manifest):
    """Verifies that bridging preserves strict 1:1 element mapping without duplicating units."""
    engine = KnowledgeSelectionEngine()
    for art_type, transformer_cls, bridge_cls in [
        (ArtifactType.PRESENTATION, PresentationTransformer, PresentationBlueprintBridge),
        (ArtifactType.HANDOUT, HandoutTransformer, HandoutBlueprintBridge),
        (ArtifactType.WORKSHEET, WorksheetTransformer, WorksheetBlueprintBridge),
        (ArtifactType.SCIENTIFIC_DOCUMENT, ScientificDocumentTransformer, ScientificDocumentBlueprintBridge),
    ]:
        intent = get_default_intent(art_type)
        bp = transformer_cls().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)
        r_art = bridge_cls().bridge(bp)

        # 1. Total render units must not exceed blueprint elements
        bp_elements = (
            getattr(bp, "beats", None)
            or getattr(bp, "sections", None)
            or getattr(bp, "activities", None)
            or getattr(bp, "arguments", None)
        )
        assert len(r_art.units) == len(bp_elements)

        # 2. Render unit IDs must all be unique
        unit_ids = [u.unit_id for u in r_art.units]
        assert len(unit_ids) == len(set(unit_ids))

        # 3. Mapped blueprint element IDs must all be unique
        mapped_bp_ids = [u.traceability_refs.blueprint_element_id for u in r_art.units]
        assert len(mapped_bp_ids) == len(set(mapped_bp_ids))

        # 4. Validator confirms zero duplication
        val = ArtifactBridgeValidator().validate(bp, r_art)
        assert len(val.duplicated_unit_violations) == 0
        assert val.is_valid is True


def test_29_golden_fixture_dry_run(oobleck_manifest):
    """Executes a dry run bridging all four artifacts from Oobleck Golden Fixture."""
    engine = KnowledgeSelectionEngine()

    # 1. Presentation
    p_intent = get_default_intent(ArtifactType.PRESENTATION)
    p_bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, p_intent), p_intent)
    p_render = PresentationBlueprintBridge().bridge(p_bp)
    p_val = ArtifactBridgeValidator().validate(p_bp, p_render)
    assert p_val.is_valid is True

    # 2. Handout
    h_intent = get_default_intent(ArtifactType.HANDOUT)
    h_bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, h_intent), h_intent)
    h_render = HandoutBlueprintBridge().bridge(h_bp)
    h_val = ArtifactBridgeValidator().validate(h_bp, h_render)
    assert h_val.is_valid is True

    # 3. Worksheet
    w_intent = get_default_intent(ArtifactType.WORKSHEET)
    w_bp = WorksheetTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, w_intent), w_intent)
    w_render = WorksheetBlueprintBridge().bridge(w_bp)
    w_val = ArtifactBridgeValidator().validate(w_bp, w_render)
    assert w_val.is_valid is True

    # 4. Scientific Document
    s_intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    s_bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, s_intent), s_intent)
    s_render = ScientificDocumentBlueprintBridge().bridge(s_bp)
    s_val = ArtifactBridgeValidator().validate(s_bp, s_render)
    assert s_val.is_valid is True
