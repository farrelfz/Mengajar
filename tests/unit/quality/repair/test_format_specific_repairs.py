"""
Unit tests for concrete format-specific repair strategies across all 4 artifact types.
"""

from app.intelligence.markdown_tree_parser import ContentBlock, SemanticBlockType
from app.intelligence.transformation.blueprints import (
    ExplanatorySection,
    HandoutBlueprint,
    LearningActivity,
    LearningActivityType,
    ScientificArgumentRole,
    ScientificArgumentUnit,
    ScientificDocumentBlueprint,
    WorksheetBlueprint,
)
from app.intelligence.transformation.intent import ArtifactType, get_default_intent
from app.presentation.slide_architect import PlannedSlide, SlidePlan
from app.quality.repair.contracts import RepairTarget
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType
from app.quality.repair.strategies.handout import HandoutHierarchyRepairStrategy, HandoutPaginationStrategy
from app.quality.repair.strategies.presentation import PresentationDensitySplitStrategy, PresentationLayoutRemapStrategy
from app.quality.repair.strategies.scientific import (
    ScientificClaimDowngradeStrategy,
    ScientificEvidenceMappingStrategy,
    ScientificMethodologyOrderStrategy,
)
from app.quality.repair.strategies.worksheet import (
    WorksheetAntiSpoilingRepairStrategy,
    WorksheetInquirySequenceStrategy,
)


# ============================================================================
# 1. PRESENTATION REPAIR TESTS
# ============================================================================

def test_presentation_density_split_strategy():
    slide1 = PlannedSlide(
        slide_id="s1",
        slide_number=1,
        act_name="Act 1",
        title="Oobleck Viscosity Mechanism",
        layout="concept_card",
        key_blocks=[
            ContentBlock(id="b1", type=SemanticBlockType.PARAGRAPH, content="Cornstarch particles suspended in water."),
            ContentBlock(id="b2", type=SemanticBlockType.PARAGRAPH, content="High shear rate forces particles to lock together."),
            ContentBlock(id="b3", type=SemanticBlockType.PARAGRAPH, content="Viscosity increases under applied stress."),
            ContentBlock(id="b4", type=SemanticBlockType.PARAGRAPH, content="Particles unlock when shear stress is removed."),
        ],
        source_refs=["ku_oobleck_1", "ku_oobleck_2"],
    )
    plan = SlidePlan(
        deck_title="Oobleck Deck",
        theme="clean_slate",
        total_slides=1,
        learning_objectives=["Understand shear thickening"],
        slides=[slide1],
    )

    target = RepairTarget(artifact_type="PRESENTATION", slide_index=1)
    hyp = RootCauseHypothesis(
        cause_type=RootCauseType.CONTENT_DENSITY,
        affected_targets=(target,),
    )

    strat = PresentationDensitySplitStrategy()
    assert strat.check_preconditions(plan, target, hyp) is True

    repair_plan = strat.plan_repair(plan, target, hyp)
    mutated_plan, actions = strat.apply_repair(plan, repair_plan)

    assert len(actions) == 1
    assert len(mutated_plan.slides) == 2
    assert mutated_plan.slides[0].title == "Oobleck Viscosity Mechanism (Bagian 1)"
    assert mutated_plan.slides[1].title == "Oobleck Viscosity Mechanism (Bagian 2)"
    assert mutated_plan.slides[0].slide_number == 1
    assert mutated_plan.slides[1].slide_number == 2
    # Traceability preserved
    assert "ku_oobleck_1" in mutated_plan.slides[0].source_refs
    assert "ku_oobleck_1" in mutated_plan.slides[1].source_refs


def test_presentation_layout_remap_strategy():
    slide1 = PlannedSlide(
        slide_id="s1",
        slide_number=1,
        act_name="Act 1",
        title="Overview",
        layout="concept_card",
        key_blocks=[],
    )
    plan = SlidePlan(
        deck_title="Oobleck Deck",
        theme="clean_slate",
        total_slides=1,
        learning_objectives=["Overview"],
        slides=[slide1],
    )
    target = RepairTarget(artifact_type="PRESENTATION", slide_index=1)
    hyp = RootCauseHypothesis(cause_type=RootCauseType.SEMANTIC_LAYOUT_MAPPING, affected_targets=(target,))

    strat = PresentationLayoutRemapStrategy()
    repair_plan = strat.plan_repair(plan, target, hyp)
    mutated_plan, actions = strat.apply_repair(plan, repair_plan)

    assert len(actions) == 1
    assert mutated_plan.slides[0].layout == "two_column"


# ============================================================================
# 2. HANDOUT REPAIR TESTS
# ============================================================================

def test_handout_pagination_consolidation():
    s1 = ExplanatorySection(
        section_id="sec_1", sequence_index=1, topic="Fluida Non-Newtonian",
        heading_level=1, core_unit_ids=("ku_1",), reading_depth="deep"
    )
    s2 = ExplanatorySection(
        section_id="sec_2", sequence_index=2, topic="Catatan Tambahan",
        heading_level=2, core_unit_ids=("ku_2",), reading_depth="brief"
    )
    bp = HandoutBlueprint(
        blueprint_id="bp_h1", artifact_type=ArtifactType.HANDOUT,
        source_manifest_id="sm_1", document_title="Handout Fluida",
        intent=get_default_intent(ArtifactType.HANDOUT), sections=(s1, s2)
    )

    target = RepairTarget(artifact_type="HANDOUT", page_index=2)
    hyp = RootCauseHypothesis(cause_type=RootCauseType.PAGE_BREAK, affected_targets=(target,))

    strat = HandoutPaginationStrategy()
    repair_plan = strat.plan_repair(bp, target, hyp)
    mutated_bp, actions = strat.apply_repair(bp, repair_plan)

    assert len(actions) == 1
    assert len(mutated_bp.sections) == 1
    assert "ku_1" in mutated_bp.sections[0].core_unit_ids
    assert "ku_2" in mutated_bp.sections[0].core_unit_ids


def test_handout_hierarchy_monotonicity_repair():
    s1 = ExplanatorySection(
        section_id="sec_1", sequence_index=1, topic="Bab I Pendahuluan",
        heading_level=1, reading_depth="standard"
    )
    s2 = ExplanatorySection(
        section_id="sec_2", sequence_index=2, topic="Sub-sub judul yang melompat",
        heading_level=3, reading_depth="standard"
    )
    bp = HandoutBlueprint(
        blueprint_id="bp_h2", artifact_type=ArtifactType.HANDOUT,
        source_manifest_id="sm_1", document_title="Handout",
        intent=get_default_intent(ArtifactType.HANDOUT), sections=(s1, s2)
    )

    strat = HandoutHierarchyRepairStrategy()
    repair_plan = strat.plan_repair(bp, RepairTarget(artifact_type="HANDOUT"), RootCauseHypothesis(cause_type=RootCauseType.NARRATIVE_ORDER))
    mutated_bp, actions = strat.apply_repair(bp, repair_plan)

    assert mutated_bp.sections[0].heading_level == 1
    assert mutated_bp.sections[1].heading_level == 2  # Corrected from 3 to 2!


# ============================================================================
# 3. WORKSHEET REPAIR TESTS
# ============================================================================

def test_worksheet_anti_spoiling_repair():
    a1 = LearningActivity(
        activity_id="act_1", sequence_index=1, activity_type=LearningActivityType.PREDICTION,
        title="Prediksi Perilaku",
        prompt_text="Prediksikan apa yang terjadi, karena cairan akan mengeras ketika dipukul cepat.",
        scaffolding_level="MEDIUM",
        withhold_explanation=False,  # Spoiled!
        expected_reasoning_type="PREDICTION",
    )
    bp = WorksheetBlueprint(
        blueprint_id="bp_w1", artifact_type=ArtifactType.WORKSHEET,
        source_manifest_id="sm_1", document_title="LKS Oobleck",
        intent=get_default_intent(ArtifactType.WORKSHEET), activities=(a1,)
    )

    strat = WorksheetAntiSpoilingRepairStrategy()
    repair_plan = strat.plan_repair(bp, RepairTarget(artifact_type="WORKSHEET"), RootCauseHypothesis(cause_type=RootCauseType.INQUIRY_STRUCTURE))
    mutated_bp, actions = strat.apply_repair(bp, repair_plan)

    act_repaired = mutated_bp.activities[0]
    assert act_repaired.withhold_explanation is True
    assert "karena cairan akan mengeras" not in act_repaired.prompt_text


def test_worksheet_inquiry_arc_restoration():
    # Inverted sequence: Observation before Prediction!
    a_obs = LearningActivity(
        activity_id="a_obs", sequence_index=1, activity_type=LearningActivityType.OBSERVATION,
        title="Catat Hasil", prompt_text="Catat kekentalan", scaffolding_level="MEDIUM", expected_reasoning_type="OBSERVATION"
    )
    a_pred = LearningActivity(
        activity_id="a_pred", sequence_index=2, activity_type=LearningActivityType.PREDICTION,
        title="Prediksi", prompt_text="Prediksikan reaksi", scaffolding_level="MEDIUM", expected_reasoning_type="PREDICTION"
    )
    bp = WorksheetBlueprint(
        blueprint_id="bp_w2", artifact_type=ArtifactType.WORKSHEET,
        source_manifest_id="sm_1", document_title="LKS",
        intent=get_default_intent(ArtifactType.WORKSHEET), activities=(a_obs, a_pred)
    )

    strat = WorksheetInquirySequenceStrategy()
    repair_plan = strat.plan_repair(bp, RepairTarget(artifact_type="WORKSHEET"), RootCauseHypothesis(cause_type=RootCauseType.INQUIRY_STRUCTURE))
    mutated_bp, actions = strat.apply_repair(bp, repair_plan)

    assert mutated_bp.activities[0].activity_type == LearningActivityType.PREDICTION
    assert mutated_bp.activities[1].activity_type == LearningActivityType.OBSERVATION


# ============================================================================
# 4. SCIENTIFIC DOCUMENT REPAIR TESTS
# ============================================================================

def test_scientific_claim_downgrade_zero_fabrication():
    arg = ScientificArgumentUnit(
        argument_id="arg_1", sequence_index=1, claim_unit_id="c_1",
        argument_role=ScientificArgumentRole.BACKGROUND_CLAIM,
        claim_statement="Fluida Oobleck secara mutlak membuktikan bahwa hukum Newton salah tanpa pengecualian.",
        supporting_evidence_unit_ids=(),  # Unsupported!
        confidence=1.0,
    )
    bp = ScientificDocumentBlueprint(
        blueprint_id="bp_sci", artifact_type=ArtifactType.SCIENTIFIC_DOCUMENT,
        source_manifest_id="sm_1", document_title="KTI Fluida",
        intent=get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT), arguments=(arg,)
    )

    strat = ScientificClaimDowngradeStrategy()
    repair_plan = strat.plan_repair(bp, RepairTarget(artifact_type="SCIENTIFIC_DOCUMENT", element_id="c_1"), RootCauseHypothesis(cause_type=RootCauseType.SOURCE_INSUFFICIENCY))
    mutated_bp, actions = strat.apply_repair(bp, repair_plan)

    repaired_arg = mutated_bp.arguments[0]
    assert repaired_arg.argument_role == ScientificArgumentRole.HYPOTHESIS
    assert repaired_arg.confidence <= 0.60
    assert "secara mutlak membuktikan bahwa" not in repaired_arg.claim_statement
    assert "berdasarkan pengamatan awal terindikasi bahwa" in repaired_arg.claim_statement
    # Zero fabrication assertion: evidence was NOT made up
    assert len(repaired_arg.supporting_evidence_unit_ids) == 0


def test_scientific_methodology_reordering():
    arg_res = ScientificArgumentUnit(
        argument_id="a_res", sequence_index=1, claim_unit_id="c_res",
        argument_role=ScientificArgumentRole.EMPIRICAL_EVIDENCE,
        claim_statement="Data hasil pengujian viskositas", confidence=0.9
    )
    arg_hyp = ScientificArgumentUnit(
        argument_id="a_hyp", sequence_index=2, claim_unit_id="c_hyp",
        argument_role=ScientificArgumentRole.HYPOTHESIS,
        claim_statement="Hipotesis pergeseran shear rate", confidence=0.8
    )
    bp = ScientificDocumentBlueprint(
        blueprint_id="bp_sci2", artifact_type=ArtifactType.SCIENTIFIC_DOCUMENT,
        source_manifest_id="sm_1", document_title="KTI",
        intent=get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT), arguments=(arg_res, arg_hyp)
    )

    strat = ScientificMethodologyOrderStrategy()
    repair_plan = strat.plan_repair(bp, RepairTarget(artifact_type="SCIENTIFIC_DOCUMENT"), RootCauseHypothesis(cause_type=RootCauseType.NARRATIVE_ORDER))
    mutated_bp, actions = strat.apply_repair(bp, repair_plan)

    assert mutated_bp.arguments[0].argument_role == ScientificArgumentRole.HYPOTHESIS
    assert mutated_bp.arguments[1].argument_role == ScientificArgumentRole.EMPIRICAL_EVIDENCE
