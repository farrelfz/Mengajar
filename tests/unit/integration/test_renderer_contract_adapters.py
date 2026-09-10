"""
Universal Knowledge Core — Renderer Contract Adapters Test Suite.

Phase 2A Controlled Renderer Adapter Integration:
Comprehensive unit test suite verifying deterministic contract adaptation,
many-to-one mapping support, bidirectional traceability preservation,
anti-corruption boundaries, and fragmentation risk analysis.
"""

import asyncio
import copy
from pathlib import Path
import pytest

from app.intelligence.pipeline import (
    KnowledgeCompiler,
    OfflineMockResolutionProvider,
)
from app.intelligence.schemas import UniversalKnowledgeManifest
from app.intelligence.transformation import (
    ArtifactType,
    HandoutTransformer,
    KnowledgeSelectionEngine,
    PresentationTransformer,
    ScientificDocumentTransformer,
    WorksheetTransformer,
    get_default_intent,
)
from app.integration.artifact_bridge import (
    HandoutBlueprintBridge,
    PresentationBlueprintBridge,
    RenderArtifact,
    RenderMetadata,
    RenderSection,
    RenderTraceabilityRef,
    RenderUnit,
    ScientificDocumentBlueprintBridge,
    WorksheetBlueprintBridge,
)
from app.integration.renderer_adapters import (
    AdapterTraceabilityValidator,
    FragmentationRiskAnalyzer,
    HandoutContractAdapter,
    LegacyPresentationDeck,
    LegacyScientificDocument,
    LegacyWorksheetDocument,
    LegacyWorksheetSection,
    PresentationContractAdapter,
    ScientificDocumentContractAdapter,
    SlideBlueprint,
    DocumentContent,
    WorksheetContractAdapter,
)

FIXTURE_PATH = Path(__file__).parent.parent.parent / "fixtures" / "oobleck_experiment.md"


@pytest.fixture(scope="module")
def oobleck_manifest() -> UniversalKnowledgeManifest:
    assert FIXTURE_PATH.exists(), f"Fixture missing at {FIXTURE_PATH}"
    raw_md = FIXTURE_PATH.read_text(encoding="utf-8")
    compiler = KnowledgeCompiler(resolution_provider=OfflineMockResolutionProvider())
    manifest = asyncio.run(compiler.compile(raw_md, source_filename="oobleck_experiment.md"))
    return manifest


@pytest.fixture
def pres_render_artifact(oobleck_manifest) -> RenderArtifact:
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)
    return PresentationBlueprintBridge().bridge(bp)


@pytest.fixture
def handout_render_artifact(oobleck_manifest) -> RenderArtifact:
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.HANDOUT)
    bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)
    return HandoutBlueprintBridge().bridge(bp)


@pytest.fixture
def worksheet_render_artifact(oobleck_manifest) -> RenderArtifact:
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.WORKSHEET)
    bp = WorksheetTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)
    return WorksheetBlueprintBridge().bridge(bp)


@pytest.fixture
def scientific_render_artifact(oobleck_manifest) -> RenderArtifact:
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)
    return ScientificDocumentBlueprintBridge().bridge(bp)


# ============================================================================
# BASE TESTS (1 - 4)
# ============================================================================

def test_01_invalid_artifact_rejection(pres_render_artifact, handout_render_artifact):
    """1. Invalid artifact type, wrong object type, or empty units must be rejected."""
    adapter = PresentationContractAdapter()
    
    # Passing wrong artifact type (HANDOUT to PresentationContractAdapter)
    with pytest.raises(ValueError, match="Unsupported artifact type"):
        adapter.adapt(handout_render_artifact)

    # Passing non-RenderArtifact
    with pytest.raises(TypeError, match="Expected RenderArtifact"):
        adapter.adapt("not an artifact")

    # Passing empty units
    empty_artifact = RenderArtifact(
        artifact_id="empty",
        artifact_type="PRESENTATION",
        document_title="Empty",
        source_blueprint_id="bp_empty",
        source_manifest_id="man_empty",
        metadata=pres_render_artifact.metadata,
        sections=(),
        units=(),
    )
    with pytest.raises(ValueError, match="contains no RenderUnits"):
        adapter.adapt(empty_artifact)


def test_02_deterministic_adaptation(pres_render_artifact):
    """2. Adapting the same RenderArtifact twice must yield identical output models."""
    adapter = PresentationContractAdapter()
    d1 = adapter.adapt(pres_render_artifact)
    d2 = adapter.adapt(pres_render_artifact)

    assert d1.total_slides == d2.total_slides
    assert len(d1.slides) == len(d2.slides)
    for s1, s2 in zip(d1.slides, d2.slides):
        assert s1.slide_id == s2.slide_id
        assert s1.title == s2.title
        assert s1.source_element_ids == s2.source_element_ids
        assert s1.layout == s2.layout


def test_03_immutable_input(pres_render_artifact):
    """3. Input RenderArtifact must remain untouched and immutable."""
    original_dict = pres_render_artifact.model_dump()
    adapter = PresentationContractAdapter()
    _ = adapter.adapt(pres_render_artifact)

    # Assert model_dump matches completely
    assert pres_render_artifact.model_dump() == original_dict


def test_04_serialization_integrity(pres_render_artifact, handout_render_artifact, worksheet_render_artifact, scientific_render_artifact):
    """4. Output legacy intermediate models must serialize cleanly to dict and JSON."""
    p_deck = PresentationContractAdapter().adapt(pres_render_artifact)
    h_doc = HandoutContractAdapter().adapt(handout_render_artifact)
    w_doc = WorksheetContractAdapter().adapt(worksheet_render_artifact)
    s_doc = ScientificDocumentContractAdapter().adapt(scientific_render_artifact)

    for doc in (p_deck, h_doc, w_doc, s_doc):
        dumped = doc.model_dump()
        assert isinstance(dumped, dict)
        json_str = doc.model_dump_json()
        assert isinstance(json_str, str)
        assert len(json_str) > 0


# ============================================================================
# PRESENTATION ADAPTER TESTS (5 - 10)
# ============================================================================

def test_05_presentation_conceptual_mapping(pres_render_artifact):
    """5. Conceptual beats map accurately to legacy slide structures."""
    adapter = PresentationContractAdapter()
    deck = adapter.adapt(pres_render_artifact)

    assert deck.total_slides > 0
    assert len(deck.slides) == deck.total_slides
    for slide in deck.slides:
        assert isinstance(slide, SlideBlueprint)
        assert slide.slide_id.startswith("slide_")
        assert slide.title != ""
        assert slide.act_id.startswith("act-")
        assert len(slide.source_element_ids) >= 1


def test_06_presentation_sequence_preserved(pres_render_artifact):
    """6. Slide sequence is strictly 1-based, monotonic, and preserves narrative flow."""
    adapter = PresentationContractAdapter()
    deck = adapter.adapt(pres_render_artifact)

    nums = [s.slide_number for s in deck.slides]
    assert nums == list(range(1, len(deck.slides) + 1))


def test_07_presentation_progressive_metadata_preserved(pres_render_artifact):
    """7. Cognitive load and information gain survive into legacy slide blueprints."""
    adapter = PresentationContractAdapter()
    deck = adapter.adapt(pres_render_artifact)

    for slide in deck.slides:
        assert 0.0 <= slide.cognitive_load <= 1.0
        assert 0.0 <= slide.information_gain <= 1.0
        assert slide.narrative_function != ""


def test_08_presentation_visual_priority_preserved(pres_render_artifact):
    """8. Visual priorities and layout intents survive without CSS/pixels."""
    adapter = PresentationContractAdapter()
    deck = adapter.adapt(pres_render_artifact)

    valid_vps = {"HIGH_DIAGRAM", "EQUATION_FOCUS", "CONCEPT_TEXT", "MEDIUM"}
    for slide in deck.slides:
        assert slide.visual_priority in valid_vps
        assert slide.layout != ""
        assert slide.visual_intent != ""


def test_09_presentation_grouping_traceability(pres_render_artifact):
    """9. Grouped slides maintain all source element IDs with bidirectional maps."""
    adapter = PresentationContractAdapter()
    deck = adapter.adapt(pres_render_artifact, grouping_mode="capacity_constraint", max_beats_per_slide=2)

    total_sources_in_slides = sum(len(s.source_element_ids) for s in deck.slides)
    assert total_sources_in_slides == len(pres_render_artifact.units)

    # All units are recorded in source_to_slide_map
    for unit in pres_render_artifact.units:
        bp_id = unit.traceability_refs.blueprint_element_id
        assert bp_id in deck.source_to_slide_map
        assert len(deck.source_to_slide_map[bp_id]) >= 1


def test_10_presentation_no_forced_one_to_one_invariant(pres_render_artifact):
    """10. Cardinality is flexible: 23 beats can map to fewer than 23 slides without losing traceability."""
    adapter = PresentationContractAdapter()
    deck_grouped = adapter.adapt(pres_render_artifact, grouping_mode="capacity_constraint", max_beats_per_slide=2)
    deck_1to1 = adapter.adapt(pres_render_artifact, grouping_mode="1_to_1")

    assert len(pres_render_artifact.units) == 23
    assert deck_1to1.total_slides == 23
    assert deck_grouped.total_slides < 23
    assert deck_grouped.total_slides >= 12


# ============================================================================
# HANDOUT ADAPTER TESTS (11 - 15)
# ============================================================================

def test_11_handout_hierarchy_preserved(handout_render_artifact):
    """11. Heading levels and outline hierarchy survive in DocumentContent and DocumentOutline."""
    adapter = HandoutContractAdapter()
    doc = adapter.adapt(handout_render_artifact)

    assert doc.outline is not None
    assert len(doc.outline.items) == len(doc.sections)
    for item, sec in zip(doc.outline.items, doc.sections):
        assert item.level == sec.level
        assert item.title == sec.title
        assert item.sequence_index == sec.sequence_index


def test_12_handout_definitions_preserved(handout_render_artifact):
    """12. Definitions survive into DocumentContentSection."""
    adapter = HandoutContractAdapter()
    doc = adapter.adapt(handout_render_artifact)

    total_defs = sum(len(s.definitions) for s in doc.sections)
    assert total_defs > 0
    for s in doc.sections:
        if s.definitions:
            assert isinstance(s.definitions, tuple)
            assert all(isinstance(d, str) for d in s.definitions)


def test_13_handout_examples_preserved(handout_render_artifact):
    """13. Examples survive into DocumentContentSection."""
    # Create an artifact with explicit examples to verify adapter preservation
    unit_with_exs = RenderUnit(
        unit_id="r_sec_ex",
        role="EXPLANATORY_SECTION",
        title="Section With Examples",
        content="""Core text explaining non-newtonian behavior.

Examples:
- Oobleck cornstarch mix
- Quicksand
- Silly putty""",
        supporting_content=("Oobleck cornstarch mix", "Quicksand"),
        sequence_index=1,
        semantic_metadata={
            "heading_level": 2,
            "reading_depth": "IN_DEPTH",
            "examples": ["Oobleck cornstarch mix", "Quicksand", "Silly putty"],
        },
        traceability_refs=RenderTraceabilityRef(
            blueprint_element_id="sec_ex_bp",
            knowledge_unit_ids=("ku_ex",),
        ),
    )
    art = RenderArtifact(
        artifact_id="art_with_exs",
        artifact_type="HANDOUT",
        document_title="Handout With Examples",
        source_blueprint_id="bp_ex",
        source_manifest_id="man_ex",
        metadata=handout_render_artifact.metadata,
        sections=(),
        units=(unit_with_exs,),
    )
    adapter = HandoutContractAdapter()
    doc = adapter.adapt(art)

    assert len(doc.sections) == 1
    sec = doc.sections[0]
    assert len(sec.examples) >= 2
    assert "Oobleck cornstarch mix" in sec.examples
    assert "Quicksand" in sec.examples


def test_14_handout_continuity_preserved(handout_render_artifact):
    """14. Reading continuity is preserved through sequential indices."""
    adapter = HandoutContractAdapter()
    doc = adapter.adapt(handout_render_artifact)

    indices = [s.sequence_index for s in doc.sections]
    assert indices == list(range(1, len(doc.sections) + 1))


def test_15_handout_section_grouping_traceability(handout_render_artifact):
    """15. Section grouping preserves source element IDs."""
    adapter = HandoutContractAdapter()
    doc = adapter.adapt(handout_render_artifact, group_by_section=True)

    expected_bp_ids = {u.traceability_refs.blueprint_element_id for u in handout_render_artifact.units}
    found_bp_ids = {bp_id for s in doc.sections for bp_id in s.source_element_ids}
    assert found_bp_ids == expected_bp_ids


# ============================================================================
# WORKSHEET ADAPTER TESTS (16 - 20)
# ============================================================================

def test_16_worksheet_activity_type_preserved(worksheet_render_artifact):
    """16. Typed activities (PHENOMENON, PREDICTION, etc.) strictly survive."""
    adapter = WorksheetContractAdapter()
    doc = adapter.adapt(worksheet_render_artifact)

    expected_types = {"PHENOMENON", "PREDICTION", "QUESTION", "OBSERVATION", "INVESTIGATION", "DATA_ANALYSIS", "REFLECTION"}
    found_types = set()
    for sec in doc.sections:
        for act in sec.activities:
            assert act.activity_type in expected_types
            found_types.add(act.activity_type)

    assert len(found_types) >= 4


def test_17_worksheet_inquiry_order_preserved(worksheet_render_artifact):
    """17. Inquiry order sequence is strictly monotonic."""
    adapter = WorksheetContractAdapter()
    doc = adapter.adapt(worksheet_render_artifact)

    all_activities = [act for s in doc.sections for act in s.activities]
    indices = [a.sequence_index for a in all_activities]
    assert indices == list(range(1, len(all_activities) + 1))


def test_18_worksheet_withholding_preserved(worksheet_render_artifact):
    """18. Withhold explanation policy and workspace requirements survive on all activities."""
    adapter = WorksheetContractAdapter()
    doc = adapter.adapt(worksheet_render_artifact)

    for sec in doc.sections:
        for act in sec.activities:
            assert act.withhold_explanation is True
            assert act.requires_student_workspace is True


def test_19_worksheet_grouping_preserved(worksheet_render_artifact):
    """19. Grouping activities into worksheet sections preserves identities and sources."""
    adapter = WorksheetContractAdapter()
    doc = adapter.adapt(worksheet_render_artifact, activities_per_section=3)

    assert len(worksheet_render_artifact.units) == 45
    assert len(doc.sections) == 15  # 45 / 3 = 15 sections
    for sec in doc.sections:
        assert len(sec.activities) == 3
        assert len(sec.source_element_ids) == 3


def test_20_worksheet_no_paragraph_flattening(worksheet_render_artifact):
    """20. Activities must NEVER be flattened to generic prose paragraphs."""
    adapter = WorksheetContractAdapter()
    doc = adapter.adapt(worksheet_render_artifact)

    for sec in doc.sections:
        for act in sec.activities:
            assert act.activity_type not in ("paragraph", "generic_text", "PROSE")
            assert act.prompt_text != ""
            assert len(act.target_knowledge_unit_ids) > 0


# ============================================================================
# SCIENTIFIC DOCUMENT ADAPTER TESTS (21 - 25)
# ============================================================================

def test_21_scientific_claim_preserved(scientific_render_artifact):
    """21. Scientific claims survive in structured subsections."""
    adapter = ScientificDocumentContractAdapter()
    doc = adapter.adapt(scientific_render_artifact)

    assert doc.total_arguments == len(scientific_render_artifact.units)
    for bab in doc.babs:
        for sub in bab.subsections:
            assert len(sub.claims) > 0
            assert all(len(c) > 0 for c in sub.claims)


def test_22_scientific_evidence_preserved(scientific_render_artifact):
    """22. Supporting evidence unit IDs survive without flattening."""
    adapter = ScientificDocumentContractAdapter()
    doc = adapter.adapt(scientific_render_artifact)

    assert doc.total_evidence_links > 0
    all_evidence_ids = [eid for b in doc.babs for s in b.subsections for eid in s.evidence_ids]
    assert len(all_evidence_ids) > 0


def test_23_scientific_evidence_relationship_preserved(scientific_render_artifact):
    """23. Evidence relationship IDs survive and are recorded in graph."""
    adapter = ScientificDocumentContractAdapter()
    doc = adapter.adapt(scientific_render_artifact)

    all_rel_ids = [rid for b in doc.babs for s in b.subsections for rid in s.relationship_ids]
    assert len(all_rel_ids) > 0
    assert len(doc.evidence_traceability_graph) > 0


def test_24_scientific_unsupported_claim_behavior_preserved(scientific_render_artifact):
    """24. Unsupported empirical claims are flagged without failing silently."""
    # Create a synthetic RenderArtifact containing an unsupported empirical argument
    units_list = list(scientific_render_artifact.units)
    fake_ref = RenderTraceabilityRef(
        blueprint_element_id="arg_unsupported_test",
        knowledge_unit_ids=("ku_test",),
        relationship_ids=(),
        source_section_ids=(),
    )
    unsupported_unit = RenderUnit(
        unit_id="r_arg_unsupported",
        role="SCIENTIFIC_ARGUMENT",
        title="Unsupported empirical claim",
        content="This claim has no empirical backing.",
        supporting_content=(),
        sequence_index=99,
        semantic_metadata={
            "argument_role": "EMPIRICAL_EVIDENCE",
            "claim_unit_id": "claim_unsupported",
            "supporting_evidence_unit_ids": [],
            "evidence_relationship_ids": [],
            "confidence": 0.2,
        },
        traceability_refs=fake_ref,
    )
    units_list.append(unsupported_unit)
    
    corrupt_artifact = RenderArtifact(
        artifact_id="corrupt_sci",
        artifact_type="SCIENTIFIC_DOCUMENT",
        document_title="Corrupt Sci Doc",
        source_blueprint_id="bp_sci_corrupt",
        source_manifest_id="man_corrupt",
        metadata=scientific_render_artifact.metadata,
        sections=(),
        units=tuple(units_list),
    )

    doc = ScientificDocumentContractAdapter().adapt(corrupt_artifact)
    assert len(doc.unsupported_claims_flagged) > 0
    assert any("r_arg_unsupported" in msg for msg in doc.unsupported_claims_flagged)


def test_25_scientific_limitation_preserved(scientific_render_artifact):
    """25. Limitations are preserved in Bab 5 (Kesimpulan dan Saran)."""
    # Create an artifact containing a limitation unit to verify preservation
    units = list(scientific_render_artifact.units)
    lim_unit = RenderUnit(
        unit_id="r_arg_lim",
        role="SCIENTIFIC_ARGUMENT",
        title="Research Limitations",
        content="Shear rate measurements limited by manual timing precision.",
        supporting_content=(),
        sequence_index=len(units) + 1,
        semantic_metadata={
            "argument_role": "LIMITATION",
            "claim_unit_id": "claim_lim_01",
            "confidence": 1.0,
        },
        traceability_refs=RenderTraceabilityRef(
            blueprint_element_id="arg_lim_bp",
            knowledge_unit_ids=("ku_lim",),
        ),
    )
    units.append(lim_unit)

    art = RenderArtifact(
        artifact_id="art_with_lim",
        artifact_type="SCIENTIFIC_DOCUMENT",
        document_title="Scientific Doc With Limitation",
        source_blueprint_id="bp_sci_lim",
        source_manifest_id="man_sci_lim",
        metadata=scientific_render_artifact.metadata,
        sections=(),
        units=tuple(units),
    )

    adapter = ScientificDocumentContractAdapter()
    doc = adapter.adapt(art)

    bab_5 = [b for b in doc.babs if b.bab.value == "BAB_5"][0]
    limitations = [lim for s in bab_5.subsections for lim in s.limitations]
    assert len(limitations) > 0
    assert "Shear rate measurements limited by manual timing precision." in limitations


# ============================================================================
# TRACEABILITY TESTS (26 - 29)
# ============================================================================

def test_26_traceability_many_to_one_mapping(pres_render_artifact):
    """26. Validator verifies many-to-one mapping with 100% source coverage."""
    adapter = PresentationContractAdapter()
    deck = adapter.adapt(pres_render_artifact, grouping_mode="capacity_constraint", max_beats_per_slide=2)

    val = AdapterTraceabilityValidator().validate(pres_render_artifact, deck)
    assert val.is_valid is True
    assert val.mapped_source_count == len(pres_render_artifact.units)
    assert val.dropped_source_count == 0


def test_27_traceability_orphan_detection(pres_render_artifact):
    """27. Orphan legacy objects (referencing unknown sources or empty sources) are caught."""
    adapter = PresentationContractAdapter()
    deck = adapter.adapt(pres_render_artifact)

    # Introduce an orphan slide
    orphan_slide = SlideBlueprint(
        slide_id="slide_orphan",
        slide_number=999,
        act_name="ACT 99 — ORPHAN",
        title="Orphan Slide",
        source_element_ids=(),  # No sources!
    )
    corrupt_deck = LegacyPresentationDeck(
        deck_title=deck.deck_title,
        total_slides=deck.total_slides + 1,
        slides=deck.slides + (orphan_slide,),
        source_to_slide_map=deck.source_to_slide_map,
        slide_to_source_map=deck.slide_to_source_map,
    )

    val = AdapterTraceabilityValidator().validate(pres_render_artifact, corrupt_deck)
    assert val.is_valid is False
    assert len(val.orphan_legacy_objects) > 0


def test_28_traceability_dropped_source_detection(pres_render_artifact):
    """28. Dropping a source element silently must fail validation."""
    adapter = PresentationContractAdapter()
    deck = adapter.adapt(pres_render_artifact)

    # Omit the first slide
    corrupt_deck = LegacyPresentationDeck(
        deck_title=deck.deck_title,
        total_slides=len(deck.slides) - 1,
        slides=deck.slides[1:],  # Dropped first slide and its sources!
        source_to_slide_map=deck.source_to_slide_map,
        slide_to_source_map=deck.slide_to_source_map,
    )

    val = AdapterTraceabilityValidator().validate(pres_render_artifact, corrupt_deck)
    assert val.is_valid is False
    assert val.dropped_source_count > 0
    assert len(val.dropped_source_ids) > 0


def test_29_traceability_duplicated_semantic_content_detection(worksheet_render_artifact):
    """29. Unintended duplicated activities trigger validation errors."""
    adapter = WorksheetContractAdapter()
    doc = adapter.adapt(worksheet_render_artifact)

    # Introduce duplicated activity into first section
    first_sec = doc.sections[0]
    corrupted_sec = LegacyWorksheetSection(
        section_id=first_sec.section_id,
        title=first_sec.title,
        sequence_index=first_sec.sequence_index,
        activities=first_sec.activities + (first_sec.activities[0],),  # duplicate!
        source_element_ids=first_sec.source_element_ids,
    )
    corrupted_doc = LegacyWorksheetDocument(
        document_id=doc.document_id,
        title=doc.title,
        pedagogical_blueprint=doc.pedagogical_blueprint,
        content_groups=doc.content_groups,
        sections=(corrupted_sec,) + doc.sections[1:],
        total_activities=doc.total_activities + 1,
        source_to_activity_map=doc.source_to_activity_map,
    )

    val = AdapterTraceabilityValidator().validate(worksheet_render_artifact, corrupted_doc)
    assert val.is_valid is False
    assert len(val.duplicated_content_violations) > 0


# ============================================================================
# RISK TESTS (30 - 32)
# ============================================================================

def test_30_risk_mechanical_presentation_mapping_warning(pres_render_artifact):
    """30. Analyzer flags mechanical 1:1 presentation mapping when beats are high."""
    adapter = PresentationContractAdapter()
    deck_1to1 = adapter.adapt(pres_render_artifact, grouping_mode="1_to_1")

    analyzer = FragmentationRiskAnalyzer()
    report = analyzer.analyze_presentation(deck_1to1, pres_render_artifact)

    assert report.is_pathological is True
    assert report.risk_score >= 0.8
    assert len(report.warnings) > 0
    assert "mechanical presentation mapping" in report.warnings[0]


def test_31_risk_worksheet_micro_fragmentation_warning(worksheet_render_artifact):
    """31. Analyzer flags micro-activity fragmentation when 45 activities are 1:1 in sections."""
    adapter = WorksheetContractAdapter()
    doc_1to1 = adapter.adapt(worksheet_render_artifact, activities_per_section=1)

    analyzer = FragmentationRiskAnalyzer()
    report = analyzer.analyze_worksheet(doc_1to1, worksheet_render_artifact)

    assert report.is_pathological is True
    assert report.risk_score >= 0.8
    assert len(report.warnings) > 0
    assert "micro-activity fragmentation" in report.warnings[0]


def test_32_risk_scientific_micro_argument_warning(scientific_render_artifact):
    """32. Analyzer flags micro-argument fragmentation when 45 arguments are 1:1 in subsections."""
    adapter = ScientificDocumentContractAdapter()
    doc_1to1 = adapter.adapt(scientific_render_artifact, arguments_per_subsection=1)

    analyzer = FragmentationRiskAnalyzer()
    report = analyzer.analyze_scientific(doc_1to1, scientific_render_artifact)

    assert report.is_pathological is True
    assert report.risk_score >= 0.8
    assert len(report.warnings) > 0
    assert "micro-argument fragmentation" in report.warnings[0]


# ============================================================================
# GOLDEN FIXTURE DRY RUN TEST (33)
# ============================================================================

def test_33_golden_fixture_adapter_dry_run(
    pres_render_artifact,
    handout_render_artifact,
    worksheet_render_artifact,
    scientific_render_artifact,
):
    """33. Complete Golden Fixture Dry Run across all four artifacts."""
    val = AdapterTraceabilityValidator()
    analyzer = FragmentationRiskAnalyzer()

    # 1. Presentation
    p_deck = PresentationContractAdapter().adapt(pres_render_artifact, grouping_mode="capacity_constraint", max_beats_per_slide=2)
    p_val = val.validate(pres_render_artifact, p_deck)
    p_risk = analyzer.analyze_presentation(p_deck, pres_render_artifact)
    assert p_val.is_valid is True
    assert p_deck.total_slides == 14

    # 2. Handout
    h_doc = HandoutContractAdapter().adapt(handout_render_artifact, group_by_section=True)
    h_val = val.validate(handout_render_artifact, h_doc)
    assert h_val.is_valid is True
    assert h_doc.total_sections == 6

    # 3. Worksheet
    w_doc = WorksheetContractAdapter().adapt(worksheet_render_artifact, activities_per_section=3)
    w_val = val.validate(worksheet_render_artifact, w_doc)
    w_risk = analyzer.analyze_worksheet(w_doc, worksheet_render_artifact)
    assert w_val.is_valid is True
    assert len(w_doc.sections) == 15

    # 4. Scientific Document
    s_doc = ScientificDocumentContractAdapter().adapt(scientific_render_artifact, arguments_per_subsection=3)
    s_val = val.validate(scientific_render_artifact, s_doc)
    s_risk = analyzer.analyze_scientific(s_doc, scientific_render_artifact)
    assert s_val.is_valid is True
    assert s_doc.total_arguments == 45
