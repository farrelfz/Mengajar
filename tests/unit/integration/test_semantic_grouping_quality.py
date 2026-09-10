"""
Universal Knowledge Core — Semantic Grouping Quality Test Suite.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Validates that Many-to-One grouping across all four artifacts (Presentation, Handout,
Worksheet, Scientific Document) is structurally and semantically justified.

Tests:
1-5: Presentation Grouping (Narrative function, sequential continuity, cognitive load, traces)
6-10: Worksheet Grouping (Inquiry progression, regression prevention, withholding, traces)
11-15: Scientific Document Grouping (Chapter integrity, ungrounded claim isolation, capacity, traces)
16-19: Handout Grouping (Heading hierarchy, empty section checks, structural trace audit)
20-22: Golden Fixture Comprehensive Audit & Edge Cases
"""

import asyncio
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
    HandoutContractAdapter,
    PresentationContractAdapter,
    ScientificDocumentContractAdapter,
    WorksheetContractAdapter,
)
from app.integration.renderer_adapters.contracts import (
    DocumentContent,
    DocumentContentSection,
    DocumentOutline,
    DocumentOutlineItem,
    GroupingDecisionTrace,
    LegacyKtiBabSection,
    LegacyPresentationDeck,
    LegacyScientificDocument,
    LegacyScientificEvidence,
    LegacyScientificSubsection,
    LegacyWorksheetActivity,
    LegacyWorksheetDocument,
    LegacyWorksheetSection,
    SlideBlueprint,
)
from app.integration.renderer_adapters.grouping_validator import (
    SemanticGroupingQualityValidator,
)

FIXTURE_PATH = Path(__file__).parent.parent.parent / "fixtures" / "oobleck_experiment.md"


def make_mock_artifact(artifact_type: str, title: str = "Test", units=(), sections=()) -> RenderArtifact:
    return RenderArtifact(
        artifact_id=f"art_{artifact_type.lower()}",
        artifact_type=artifact_type,
        document_title=title,
        source_blueprint_id="bp_mock",
        source_manifest_id="man_mock",
        metadata=RenderMetadata(
            artifact_type=artifact_type,
            document_title=title,
            domain="physics",
            audience_level="HIGH_SCHOOL",
            total_units=len(units),
            total_sections=len(sections),
        ),
        units=tuple(units),
        sections=tuple(sections),
    )


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


@pytest.fixture
def validator() -> SemanticGroupingQualityValidator:
    return SemanticGroupingQualityValidator()


# ============================================================================
# 1. PRESENTATION GROUPING QUALITY (Tests 1 - 5)
# ============================================================================

def test_01_presentation_narrative_function_coherence(pres_render_artifact, validator):
    """1. Grouped presentation slides must share identical narrative function."""
    adapter = PresentationContractAdapter()
    deck = adapter.adapt(pres_render_artifact, grouping_mode="capacity_constraint")
    report = validator.validate_presentation_grouping(deck, pres_render_artifact)

    assert report.is_valid is True
    assert len(report.compatibility_violations) == 0
    assert report.total_groups == len(deck.slides)


def test_02_presentation_narrative_mismatch_detected(pres_render_artifact, validator):
    """2. Validator flags mismatched narrative functions on the same slide."""
    adapter = PresentationContractAdapter()
    deck = adapter.adapt(pres_render_artifact, grouping_mode="1_to_1")

    # Construct invalid grouped slide mixing INTRO and CONCLUSION
    slide_bad = SlideBlueprint(
        slide_id="slide_mismatch",
        slide_number=99,
        title="Invalid Grouping",
        source_element_ids=(
            pres_render_artifact.units[0].traceability_refs.blueprint_element_id,
            pres_render_artifact.units[-1].traceability_refs.blueprint_element_id,
        ),
    )
    bad_deck = LegacyPresentationDeck(
        deck_title="Corrupt Deck",
        total_slides=1,
        slides=(slide_bad,),
    )

    report = validator.validate_presentation_grouping(bad_deck, pres_render_artifact)
    assert report.is_valid is False
    assert len(report.compatibility_violations) >= 1
    assert "Incompatible narrative grouping" in report.compatibility_violations[0]


def test_03_presentation_sequence_continuity_break_detected(pres_render_artifact, validator):
    """3. Validator flags non-contiguous sequence jump within a single slide."""
    unit_a = pres_render_artifact.units[0]
    unit_c = pres_render_artifact.units[2]  # Skips unit index 1

    slide_jump = SlideBlueprint(
        slide_id="slide_jump",
        slide_number=1,
        title="Sequence Jump Slide",
        source_element_ids=(
            unit_a.traceability_refs.blueprint_element_id,
            unit_c.traceability_refs.blueprint_element_id,
        ),
    )
    deck_jump = LegacyPresentationDeck(
        deck_title="Jump Deck",
        total_slides=1,
        slides=(slide_jump,),
    )

    report = validator.validate_presentation_grouping(deck_jump, pres_render_artifact)
    assert report.is_valid is False
    assert len(report.continuity_violations) >= 1
    assert "Sequence break" in report.continuity_violations[0]


def test_04_presentation_cognitive_overload_detected(validator):
    """4. Validator flags cumulative cognitive load exceeding capacity constraint (1.8)."""
    tref_a = RenderTraceabilityRef(source_manifest_id="m", unit_id="u1", blueprint_element_id="bp1")
    tref_b = RenderTraceabilityRef(source_manifest_id="m", unit_id="u2", blueprint_element_id="bp2")

    u1 = RenderUnit(
        unit_id="u1",
        title="Beat 1",
        content="Heavy content 1",
        role="CONCEPTUAL_BEAT",
        sequence_index=1,
        semantic_metadata={"narrative_function": "EXPLANATION", "cognitive_load_target": 1.0},
        traceability_refs=tref_a,
    )
    u2 = RenderUnit(
        unit_id="u2",
        title="Beat 2",
        content="Heavy content 2",
        role="CONCEPTUAL_BEAT",
        sequence_index=2,
        semantic_metadata={"narrative_function": "EXPLANATION", "cognitive_load_target": 1.0},
        traceability_refs=tref_b,
    )
    art = make_mock_artifact("PRESENTATION", "Heavy Deck", units=[u1, u2])

    slide_heavy = SlideBlueprint(
        slide_id="slide_heavy",
        slide_number=1,
        title="Overloaded Slide",
        source_element_ids=("bp1", "bp2"),
    )
    deck = LegacyPresentationDeck(
        deck_title="Heavy Deck",
        total_slides=1,
        slides=(slide_heavy,),
    )

    report = validator.validate_presentation_grouping(deck, art)
    assert report.is_valid is False
    assert len(report.capacity_violations) >= 1
    assert "Cognitive overload" in report.capacity_violations[0]


def test_05_presentation_decision_traces_audit(pres_render_artifact):
    """5. Grouping decision traces must explain reasons and rejected candidates."""
    adapter = PresentationContractAdapter()
    deck = adapter.adapt(pres_render_artifact, grouping_mode="capacity_constraint", max_beats_per_slide=2)

    assert len(deck.grouping_decision_traces) == len(deck.slides)
    for trace in deck.grouping_decision_traces:
        assert isinstance(trace, GroupingDecisionTrace)
        assert trace.group_id != ""
        assert len(trace.source_element_ids) >= 1
        assert trace.grouping_reason != ""


# ============================================================================
# 2. WORKSHEET GROUPING QUALITY (Tests 6 - 10)
# ============================================================================

def test_06_worksheet_compatibility_grouping_valid(worksheet_render_artifact, validator):
    """6. Worksheet compatibility grouping produces valid progression without regressions."""
    adapter = WorksheetContractAdapter()
    doc = adapter.adapt(worksheet_render_artifact, grouping_mode="compatibility")
    report = validator.validate_worksheet_grouping(doc, worksheet_render_artifact)

    assert report.is_valid is True
    assert len(report.continuity_violations) == 0
    assert len(report.compatibility_violations) == 0
    assert report.arbitrary_grouping_detected is False


def test_07_worksheet_inquiry_regression_detected(validator):
    """7. Validator flags inquiry regression when REFLECTION is grouped before PHENOMENON."""
    act_reflection = LegacyWorksheetActivity(
        activity_id="act_01",
        activity_type="REFLECTION",
        title="Reflection Activity",
        prompt_text="Reflect on this",
        sequence_index=1,
        withhold_explanation=True,
    )
    act_phenomenon = LegacyWorksheetActivity(
        activity_id="act_02",
        activity_type="PHENOMENON",
        title="Phenomenon Activity",
        prompt_text="Observe phenomenon",
        sequence_index=2,
        withhold_explanation=True,
    )
    sec_corrupt = LegacyWorksheetSection(
        section_id="sec_regress",
        title="Corrupted Inquiry Section",
        activities=(act_reflection, act_phenomenon),
    )
    doc = LegacyWorksheetDocument(
        document_id="doc_corrupt",
        title="Corrupted Worksheet",
        sections=(sec_corrupt,),
        total_activities=2,
    )
    art = make_mock_artifact("WORKSHEET", "W")

    report = validator.validate_worksheet_grouping(doc, art)
    assert report.is_valid is False
    assert len(report.continuity_violations) >= 1
    assert "Inquiry order regression" in report.continuity_violations[0]


def test_08_worksheet_withholding_violation_detected(validator):
    """8. Validator flags activities with withhold_explanation set to False."""
    act_leaked = LegacyWorksheetActivity(
        activity_id="act_leaked",
        activity_type="INVESTIGATION",
        title="Investigation Activity",
        prompt_text="Investigate",
        sequence_index=1,
        withhold_explanation=False,  # Leaked answer!
    )
    act_ok = LegacyWorksheetActivity(
        activity_id="act_ok",
        activity_type="DATA_ANALYSIS",
        title="Analysis Activity",
        prompt_text="Analyze",
        sequence_index=2,
        withhold_explanation=True,
    )
    sec = LegacyWorksheetSection(
        section_id="sec_leaked",
        title="Leaked Section",
        activities=(act_leaked, act_ok),
    )
    doc = LegacyWorksheetDocument(
        document_id="doc_leaked",
        title="Leaked Worksheet",
        sections=(sec,),
        total_activities=2,
    )
    art = make_mock_artifact("WORKSHEET", "W")

    report = validator.validate_worksheet_grouping(doc, art)
    assert report.is_valid is False
    assert len(report.compatibility_violations) >= 1
    assert "Withhold explanation violated" in report.compatibility_violations[0]


def test_09_worksheet_excessive_density_detected(validator):
    """9. Validator flags sections containing more than 4 learning activities."""
    acts = tuple(
        LegacyWorksheetActivity(
            activity_id=f"act_{i}",
            activity_type="INVESTIGATION",
            title=f"Activity {i}",
            prompt_text=f"Task {i}",
            sequence_index=i,
            withhold_explanation=True,
        )
        for i in range(1, 6)  # 5 activities > 4
    )
    sec = LegacyWorksheetSection(
        section_id="sec_dense",
        title="Dense Section",
        activities=acts,
    )
    doc = LegacyWorksheetDocument(
        document_id="doc_dense",
        title="Dense Worksheet",
        sections=(sec,),
        total_activities=5,
    )
    art = make_mock_artifact("WORKSHEET", "W")

    report = validator.validate_worksheet_grouping(doc, art)
    assert report.is_valid is False
    assert len(report.capacity_violations) >= 1
    assert "Excessive activity density" in report.capacity_violations[0]


def test_10_worksheet_decision_trace_generation(worksheet_render_artifact):
    """10. Worksheet adapter generates decision traces across all grouping modes."""
    adapter = WorksheetContractAdapter()
    doc_chunk = adapter.adapt(worksheet_render_artifact, activities_per_section=3, grouping_mode="chunk")
    doc_compat = adapter.adapt(worksheet_render_artifact, grouping_mode="compatibility")
    doc_1to1 = adapter.adapt(worksheet_render_artifact, activities_per_section=1)

    assert len(doc_chunk.grouping_decision_traces) == len(doc_chunk.sections)
    assert len(doc_compat.grouping_decision_traces) == len(doc_compat.sections)
    assert len(doc_1to1.grouping_decision_traces) == 45


# ============================================================================
# 3. SCIENTIFIC DOCUMENT GROUPING QUALITY (Tests 11 - 15)
# ============================================================================

def test_11_scientific_document_grouping_valid(scientific_render_artifact, validator):
    """11. Scientific document adapter produces valid, trace-audited KTI subsections."""
    adapter = ScientificDocumentContractAdapter()
    doc = adapter.adapt(scientific_render_artifact, arguments_per_subsection=3)
    report = validator.validate_scientific_grouping(doc, scientific_render_artifact)

    assert report.is_valid is True
    assert len(report.violations) == 0
    assert report.arbitrary_grouping_detected is False


def test_12_scientific_ungrounded_claim_mixing_detected(validator):
    """12. Validator flags ungrounded claims mixed with empirical evidence without limitation."""
    ev = LegacyScientificEvidence(evidence_id="ev_01", evidence_text="Data")
    sub_corrupt = LegacyScientificSubsection(
        subsection_id="sub_corrupt",
        title="Mixed Subsection",
        argument_ids=("arg_01", "arg_02"),
        claims=("Claim 1", "Claim 2"),
        evidence_items=(ev,),
        evidence_ids=("ev_01",),
        unsupported_claims=("Claim without evidence",),  # Mixed!
        limitations=tuple(),  # No limitation demarcation!
    )
    bab = LegacyKtiBabSection(
        bab="BAB_4",
        title="BAB IV: HASIL DAN PEMBAHASAN",
        subsections=(sub_corrupt,),
    )
    doc = LegacyScientificDocument(
        document_id="doc_sci",
        title="Corrupted KTI",
        babs=(bab,),
        total_arguments=2,
    )
    art = make_mock_artifact("SCIENTIFIC_DOCUMENT", "KTI")

    report = validator.validate_scientific_grouping(doc, art)
    assert report.is_valid is False
    assert len(report.compatibility_violations) >= 1
    assert "Integrity violation" in report.compatibility_violations[0]


def test_13_scientific_subsection_capacity_limit_detected(validator):
    """13. Validator flags subsections exceeding 5 arguments."""
    sub_dense = LegacyScientificSubsection(
        subsection_id="sub_dense",
        title="Dense Subbab",
        argument_ids=tuple(f"arg_{i}" for i in range(1, 7)),  # 6 arguments > 5
        claims=tuple(f"Claim {i}" for i in range(1, 7)),
    )
    bab = LegacyKtiBabSection(
        bab="BAB_1",
        title="BAB I: PENDAHULUAN",
        subsections=(sub_dense,),
    )
    doc = LegacyScientificDocument(
        document_id="doc_sci",
        title="Dense KTI",
        babs=(bab,),
        total_arguments=6,
    )
    art = make_mock_artifact("SCIENTIFIC_DOCUMENT", "KTI")

    report = validator.validate_scientific_grouping(doc, art)
    assert report.is_valid is False
    assert len(report.capacity_violations) >= 1
    assert "exceeds capacity" in report.capacity_violations[0]


def test_14_scientific_decision_traces_recorded(scientific_render_artifact):
    """14. Scientific adapter records decision traces on all subsections."""
    adapter = ScientificDocumentContractAdapter()
    doc = adapter.adapt(scientific_render_artifact, arguments_per_subsection=3)

    total_subsections = sum(len(b.subsections) for b in doc.babs)
    assert len(doc.grouping_decision_traces) == total_subsections
    for trace in doc.grouping_decision_traces:
        assert trace.group_id.startswith("sub_")
        assert len(trace.source_element_ids) >= 1
        assert "thematic grouping" in trace.grouping_reason


def test_15_scientific_arbitrary_chunking_detected_without_traces(validator):
    """15. Validator detects fixed-size chunking when decision traces are omitted."""
    sub1 = LegacyScientificSubsection(
        subsection_id="sub_01",
        title="Sub 1",
        argument_ids=("arg_1", "arg_2", "arg_3"),
    )
    sub2 = LegacyScientificSubsection(
        subsection_id="sub_02",
        title="Sub 2",
        argument_ids=("arg_4", "arg_5", "arg_6"),
    )
    bab = LegacyKtiBabSection(
        bab="BAB_1",
        title="BAB I: PENDAHULUAN",
        subsections=(sub1, sub2),
    )
    doc_untraced = LegacyScientificDocument(
        document_id="doc_untraced",
        title="Untraced KTI",
        babs=(bab,),
        total_arguments=6,
        grouping_decision_traces=tuple(),  # Traces omitted!
    )
    art = make_mock_artifact("SCIENTIFIC_DOCUMENT", "KTI")

    report = validator.validate_scientific_grouping(doc_untraced, art)
    assert report.is_valid is False
    assert report.arbitrary_grouping_detected is True
    assert "Arbitrary argument chunking detected" in report.violations[0]


# ============================================================================
# 4. HANDOUT GROUPING QUALITY (Tests 16 - 19)
# ============================================================================

def test_16_handout_heading_hierarchy_inversion_detected(validator):
    """16. Validator flags unnatural heading level jumps (e.g. level 1 to level 3)."""
    sec1 = DocumentContentSection(
        section_id="sec_01",
        title="Introduction",
        level=1,
        content="Intro text",
    )
    sec2 = DocumentContentSection(
        section_id="sec_02",
        title="Sub-sub section",
        level=3,  # Jumped from 1 to 3!
        content="Deep text",
    )
    doc = DocumentContent(
        document_id="doc_handout",
        title="Handout",
        outline=DocumentOutline(outline_id="out", title="H", items=tuple()),
        sections=(sec1, sec2),
        total_sections=2,
    )
    art = make_mock_artifact("HANDOUT", "H")

    report = validator.validate_handout_grouping(doc, art)
    assert report.is_valid is False
    assert len(report.continuity_violations) >= 1
    assert "Heading hierarchy inversion" in report.continuity_violations[0]


def test_17_handout_empty_section_detected(validator):
    """17. Validator flags completely empty reading sections."""
    sec_empty = DocumentContentSection(
        section_id="sec_empty",
        title="Empty Section",
        level=1,
        content="",
        definitions=tuple(),
        examples=tuple(),
    )
    doc = DocumentContent(
        document_id="doc_empty",
        title="Empty Handout",
        outline=DocumentOutline(outline_id="out", title="H", items=tuple()),
        sections=(sec_empty,),
        total_sections=1,
    )
    art = make_mock_artifact("HANDOUT", "H")

    report = validator.validate_handout_grouping(doc, art)
    assert report.is_valid is False
    assert len(report.compatibility_violations) >= 1
    assert "Empty reading section detected" in report.compatibility_violations[0]


def test_18_handout_decision_traces_recorded(handout_render_artifact):
    """18. Handout adapter records decision traces on all adapted sections."""
    adapter = HandoutContractAdapter()
    doc_sections = adapter.adapt(handout_render_artifact, group_by_section=True)
    doc_units = adapter.adapt(handout_render_artifact, group_by_section=False)

    assert len(doc_sections.grouping_decision_traces) == len(doc_sections.sections)
    assert len(doc_units.grouping_decision_traces) == len(doc_units.sections)
    for trace in doc_sections.grouping_decision_traces:
        assert trace.grouping_reason.startswith("Structural section grouping")


def test_19_handout_golden_fixture_validation(handout_render_artifact, validator):
    """19. Golden fixture handout passes all grouping quality checks."""
    adapter = HandoutContractAdapter()
    doc = adapter.adapt(handout_render_artifact, group_by_section=True)
    report = validator.validate_handout_grouping(doc, handout_render_artifact)

    assert report.is_valid is True
    assert len(report.violations) == 0


# ============================================================================
# 5. CROSS-ARTIFACT & AUDIT INTEGRITY (Tests 20 - 22)
# ============================================================================

def test_20_all_golden_artifacts_pass_quality_validation(
    pres_render_artifact,
    handout_render_artifact,
    worksheet_render_artifact,
    scientific_render_artifact,
    validator,
):
    """20. All four adapted golden artifacts pass semantic grouping quality validation."""
    pres_doc = PresentationContractAdapter().adapt(pres_render_artifact)
    handout_doc = HandoutContractAdapter().adapt(handout_render_artifact)
    worksheet_doc = WorksheetContractAdapter().adapt(worksheet_render_artifact, grouping_mode="compatibility")
    scientific_doc = ScientificDocumentContractAdapter().adapt(scientific_render_artifact)

    pres_report = validator.validate_presentation_grouping(pres_doc, pres_render_artifact)
    handout_report = validator.validate_handout_grouping(handout_doc, handout_render_artifact)
    worksheet_report = validator.validate_worksheet_grouping(worksheet_doc, worksheet_render_artifact)
    scientific_report = validator.validate_scientific_grouping(scientific_doc, scientific_render_artifact)

    assert pres_report.is_valid is True, f"Pres violations: {pres_report.violations}"
    assert handout_report.is_valid is True, f"Handout violations: {handout_report.violations}"
    assert worksheet_report.is_valid is True, f"Worksheet violations: {worksheet_report.violations}"
    assert scientific_report.is_valid is True, f"Sci violations: {scientific_report.violations}"


def test_21_traceability_from_decision_traces_to_blueprint_ids(
    pres_render_artifact,
    worksheet_render_artifact,
    scientific_render_artifact,
):
    """21. Every decision trace contains existing blueprint element IDs."""
    pres_doc = PresentationContractAdapter().adapt(pres_render_artifact)
    worksheet_doc = WorksheetContractAdapter().adapt(worksheet_render_artifact, grouping_mode="compatibility")
    scientific_doc = ScientificDocumentContractAdapter().adapt(scientific_render_artifact)

    pres_bps = {u.traceability_refs.blueprint_element_id for u in pres_render_artifact.units}
    for trace in pres_doc.grouping_decision_traces:
        for bid in trace.source_element_ids:
            assert bid in pres_bps

    ws_bps = {u.traceability_refs.blueprint_element_id for u in worksheet_render_artifact.units}
    for trace in worksheet_doc.grouping_decision_traces:
        for bid in trace.source_element_ids:
            assert bid in ws_bps

    sci_bps = {u.traceability_refs.blueprint_element_id for u in scientific_render_artifact.units}
    for trace in scientific_doc.grouping_decision_traces:
        for bid in trace.source_element_ids:
            assert bid in sci_bps


def test_22_trace_serialization_roundtrip(pres_render_artifact):
    """22. GroupingDecisionTrace model is fully JSON-serializable."""
    adapter = PresentationContractAdapter()
    deck = adapter.adapt(pres_render_artifact)

    for trace in deck.grouping_decision_traces:
        data = trace.model_dump()
        restored = GroupingDecisionTrace.model_validate(data)
        assert restored == trace
