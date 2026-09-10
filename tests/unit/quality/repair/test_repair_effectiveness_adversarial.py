"""
Universal Document Intelligence System V5 — Phase 3D.1 Adversarial Test Suite.

Exhaustive verification of repair effectiveness, compatibility firewalls,
self-disqualification, causal reach, zero-effect mutation detection,
and forensic decomposition across Scenarios A through O.
"""

from pathlib import Path
import pytest

from app.orchestration.convergence_controller import (
    ProductionConvergenceController,
    ProductionConvergenceOutcome,
    StagnationReason,
)
from app.orchestration.forensics_exporter import RepairForensicsExporter
from app.orchestration.production_context import ArtifactProductionContext
from app.quality.contracts.authority import UnifiedQualityReport
from app.quality.contracts.decisions import ExportDecision
from app.quality.contracts.findings import QualityFinding
from app.quality.contracts.signals import QualityDomain
from app.quality.repair.effectiveness.causal_reach import CausalReach, CausalReachModel
from app.quality.repair.effectiveness.contracts import (
    EffectivenessStatus,
    RepairAttempt,
    RepairEffectivenessResult,
    RepairExecutionStatus,
)
from app.quality.repair.effectiveness.coverage_matrix import (
    CitationInvisibleSubtype,
    RootCauseCoverageMatrix,
)
from app.quality.repair.effectiveness.escalation import (
    CausalEscalationEngine,
    RepairEscalationReason,
)
from app.quality.repair.effectiveness.firewall import (
    RepairStrategyCompatibilityFirewall,
)
from app.quality.repair.effectiveness.strategy_memory import (
    SelfDisqualifyingStrategyMemory,
    StrategyHistoryKey,
)
from app.quality.repair.effectiveness.zero_effect_detector import (
    DomainFingerprinter,
    ZeroEffectMutationDetector,
)
from app.quality.repair.mutation_contract import RepairMutationScope
from app.quality.repair.planner import MinimalInterventionRepairPlanner
from app.quality.repair.portfolio import RepairCandidatePortfolio
from app.quality.repair.registry import DEFAULT_STRATEGY_REGISTRY
from app.quality.repair.root_cause import (
    DeterministicRootCauseAnalyzer,
    RootCauseHypothesis,
    RootCauseType,
)
from app.quality.repair.strategies.presentation import (
    PresentationComponentReflowStrategy,
    PresentationPaddingAdjustmentStrategy,
)
from app.quality.repair.strategies.worksheet import (
    WorksheetAntiSpoilingRepairStrategy,
    WorksheetLayoutAlternationStrategy,
)
from app.quality.repair.strategies.scientific import (
    ScientificCitationLinkingStrategy,
)
from app.intelligence.transformation.blueprints import (
    LearningActivity,
    LearningActivityType,
    WorksheetBlueprint,
)
from app.intelligence.transformation.intent import ArtifactType, get_default_intent


# ── Scenario A: Same ineffective strategy repeated twice -> disqualified ──
def test_scenario_a_disqualification_after_two_ineffective_attempts():
    memory = SelfDisqualifyingStrategyMemory()
    key = StrategyHistoryKey(
        artifact_type="PRESENTATION",
        artifact_id="pres_1",
        root_cause_cluster="GRID_GEOMETRY",
        strategy_id="presentation_padding_adjust",
    )

    attempt1 = RepairAttempt(
        attempt_id="att_1",
        artifact_type="PRESENTATION",
        iteration=1,
        strategy_id="presentation_padding_adjust",
        mutation_scope=RepairMutationScope.LEVEL_1_LOCAL_TOKEN,
        owning_layer="R0",
        pre_state_hash="hash_0",
        post_state_hash="hash_1",
    )
    res1 = RepairEffectivenessResult.evaluate(
        attempt=attempt1,
        pre_blockers=["ELEMENT_COLLISION"],
        post_blockers=["ELEMENT_COLLISION"],
        pre_findings=["ELEMENT_COLLISION"],
        post_findings=["ELEMENT_COLLISION"],
        pre_score=0.80,
        post_score=0.80,
    )
    assert res1.overall_status == EffectivenessStatus.INEFFECTIVE

    entry1 = memory.record_attempt_result(key, res1, "ELEMENT_COLLISION", "hash_1")
    assert entry1.consecutive_ineffective_count == 1
    assert entry1.is_disqualified is False

    # Second consecutive ineffective attempt
    attempt2 = attempt1.model_copy(update={"attempt_id": "att_2", "iteration": 2, "pre_state_hash": "hash_1", "post_state_hash": "hash_2"})
    res2 = RepairEffectivenessResult.evaluate(
        attempt=attempt2,
        pre_blockers=["ELEMENT_COLLISION"],
        post_blockers=["ELEMENT_COLLISION"],
        pre_findings=["ELEMENT_COLLISION"],
        post_findings=["ELEMENT_COLLISION"],
        pre_score=0.80,
        post_score=0.80,
    )
    entry2 = memory.record_attempt_result(key, res2, "ELEMENT_COLLISION", "hash_2")
    assert entry2.consecutive_ineffective_count == 2
    assert entry2.is_disqualified is True
    assert "Disqualified after 2 consecutive ineffective attempts" in entry2.disqualification_reason

    # Query memory
    is_disqual, reason = memory.is_strategy_disqualified(
        artifact_type="PRESENTATION",
        artifact_id="pres_1",
        root_cause_cluster="GRID_GEOMETRY",
        strategy_id="presentation_padding_adjust",
        current_defect_signature="ELEMENT_COLLISION",
    )
    assert is_disqual is True
    assert "Disqualified" in reason


# ── Scenario B: Presentation strategy proposed for Worksheet -> rejected before scoring ──
def test_scenario_b_worksheet_rejects_presentation_strategy_before_scoring():
    pres_strat = PresentationPaddingAdjustmentStrategy()
    eligible, rejections = RepairStrategyCompatibilityFirewall.filter_eligible_strategies(
        strategies=[pres_strat],
        artifact_type="WORKSHEET",
    )
    assert len(eligible) == 0
    assert len(rejections) == 1
    assert rejections[0].strategy_id == "presentation_padding_adjust"
    assert rejections[0].filter_stage == "ARTIFACT_COMPATIBILITY"
    assert "incompatible with 'WORKSHEET'" in rejections[0].reason


# ── Scenario C: Unknown finding without repair coverage -> MANUAL_REVIEW_REQUIRED, not generic fallback ──
def test_scenario_c_unknown_finding_has_zero_generic_fallback():
    finding = QualityFinding(
        failure_code="COMPLETELY_UNHEARD_OF_DEFECT_999",
        domain=QualityDomain.RENDERED,
        message="An unrecognized failure occurred.",
    )
    hyps = DeterministicRootCauseAnalyzer.analyze(
        findings=[finding],
        clusters=[],
        artifact_type="PRESENTATION",
    )
    assert len(hyps) == 1
    assert hyps[0].cause_type == RootCauseType.UNKNOWN
    assert hyps[0].repairability is False  # Must be explicitly non-repairable
    assert "no verified automated repair" in hyps[0].rationale


# ── Scenario D: Mutation changes artifact but not targeted finding -> ZERO_EFFECT_MUTATION ──
def test_scenario_d_zero_effect_mutation_detection():
    act = LearningActivity(
        activity_id="act_1",
        sequence_index=1,
        activity_type=LearningActivityType.OBSERVATION,
        title="Amati",
        prompt_text="Tuliskan hasil pengamatan Anda.",
        target_knowledge_unit_ids=("u1",),
        scaffolding_level="MEDIUM",
        expected_reasoning_type="OBSERVATION",
    )
    bp = WorksheetBlueprint(
        blueprint_id="ws_1",
        artifact_type=ArtifactType.WORKSHEET,
        source_manifest_id="sm_1",
        document_title="Lembar Kerja",
        intent=get_default_intent(ArtifactType.WORKSHEET),
        activities=(act,),
    )
    pre_fp = DomainFingerprinter.fingerprint("WORKSHEET", bp)
    post_fp = DomainFingerprinter.fingerprint("WORKSHEET", bp)  # unchanged blueprint

    is_zero, reason = ZeroEffectMutationDetector.detect_zero_effect(
        pre_fingerprint=pre_fp,
        post_fingerprint=post_fp,
        pre_state_hash="hash_a",
        post_state_hash="hash_b",  # CSS changed but domain fingerprint identical
        pre_findings=["REPETITION_STREAK"],
        post_findings=["REPETITION_STREAK"],
        targeted_finding_codes=["REPETITION_STREAK"],
    )
    assert is_zero is True
    assert "targeted domain fingerprint (WORKSHEET) remained unchanged" in reason


# ── Scenario E: Local repair cannot resolve structural root cause -> causal escalation ──
def test_scenario_e_causal_reach_escalation():
    # PADDING_SPACING requires LOCAL_RENDER_GEOMETRY (Depth 1)
    # GRID_GEOMETRY requires COMPONENT_SPATIAL_STRUCTURE (Depth 2)
    assert CausalReachModel.is_reach_sufficient(CausalReach.LOCAL_RENDER_GEOMETRY, RootCauseType.PADDING_SPACING) is True
    assert CausalReachModel.is_reach_sufficient(CausalReach.LOCAL_RENDER_GEOMETRY, RootCauseType.GRID_GEOMETRY) is False
    assert CausalReachModel.is_reach_sufficient(CausalReach.COMPONENT_SPATIAL_STRUCTURE, RootCauseType.GRID_GEOMETRY) is True

    # When padding adjustment fails against ELEMENT_COLLISION, escalation routes to reflow/remap
    memory = SelfDisqualifyingStrategyMemory()
    key = StrategyHistoryKey(
        artifact_type="PRESENTATION",
        artifact_id="default",
        root_cause_cluster="GRID_GEOMETRY",
        strategy_id="presentation_padding_adjust",
    )
    # Mark padding adjust disqualified
    att = RepairAttempt(attempt_id="a1", artifact_type="PRESENTATION", iteration=1, strategy_id="presentation_padding_adjust", mutation_scope=RepairMutationScope.LEVEL_1_LOCAL_TOKEN, owning_layer="R0", pre_state_hash="h1", post_state_hash="h2")
    res = RepairEffectivenessResult(attempt_id="a1", strategy_id="presentation_padding_adjust", artifact_type="PRESENTATION", overall_status=EffectivenessStatus.INEFFECTIVE)
    memory.record_attempt_result(key, res, "ELEMENT_COLLISION", "h2")
    memory.record_attempt_result(key, res, "ELEMENT_COLLISION", "h3")

    decision = CausalEscalationEngine.resolve_escalation(
        artifact_type="PRESENTATION",
        finding_code="ELEMENT_COLLISION",
        root_cause=RootCauseType.GRID_GEOMETRY,
        previous_result=res,
        memory=memory,
        available_strategies=[PresentationPaddingAdjustmentStrategy(), PresentationComponentReflowStrategy()],
        current_scope=RepairMutationScope.LEVEL_1_LOCAL_TOKEN,
    )
    assert decision.escalated_strategy_id == "presentation_component_reflow"
    assert decision.target_owning_layer == "R1"
    assert decision.is_terminal_manual_review is False


# ── Scenario F: Aggregate score improves but hard blocker persists -> not converged ──
def test_scenario_f_score_improves_but_blocker_persists_not_converged():
    controller = ProductionConvergenceController(max_iterations=5)
    
    rep1 = UnifiedQualityReport(
        artifact_type="PRESENTATION",
        decision=ExportDecision.REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        overall_quality_score=0.75,
        hard_blockers=("ELEMENT_COLLISION",),
    )
    controller.advance_iteration()
    res1 = controller.evaluate(rep1, "hash_1")
    assert res1.outcome == ProductionConvergenceOutcome.CONTINUE_REPAIR

    # Score improves to 0.85, but hard blocker remains
    rep2 = UnifiedQualityReport(
        artifact_type="PRESENTATION",
        decision=ExportDecision.REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        overall_quality_score=0.85,
        hard_blockers=("ELEMENT_COLLISION",),
    )
    controller.advance_iteration()
    res2 = controller.evaluate(rep2, "hash_2")
    assert res2.can_export is False
    assert res2.should_terminate is False

    # Score improves to 0.92, but hard blocker still remains
    rep3 = UnifiedQualityReport(
        artifact_type="PRESENTATION",
        decision=ExportDecision.REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        overall_quality_score=0.92,
        hard_blockers=("ELEMENT_COLLISION",),
    )
    controller.advance_iteration()
    res3 = controller.evaluate(rep3, "hash_3")
    assert res3.outcome == ProductionConvergenceOutcome.FALSE_PROGRESS
    assert res3.can_export is False
    assert res3.stagnation_reason == StagnationReason.NO_FINDING_REDUCTION


# ── Scenario G: Scientific citation invisible -> subtype diagnosis, not padding fallback ──
def test_scenario_g_scientific_citation_invisible_subtype_decomposition():
    # 1. Zero size
    st1 = RootCauseCoverageMatrix.classify_citation_invisible_subtype({"font_size": 0.0, "anchor_exists": True})
    assert st1 == CitationInvisibleSubtype.CITATION_ZERO_SIZE
    cause1, layer1, strats1 = RootCauseCoverageMatrix.resolve_citation_subtype_strategy(st1)
    assert cause1 == RootCauseType.TYPOGRAPHY
    assert layer1 == "R0"

    # 2. Low contrast
    st2 = RootCauseCoverageMatrix.classify_citation_invisible_subtype({"contrast_ratio": 1.2, "anchor_exists": True})
    assert st2 == CitationInvisibleSubtype.CITATION_LOW_CONTRAST
    cause2, layer2, _ = RootCauseCoverageMatrix.resolve_citation_subtype_strategy(st2)
    assert cause2 == RootCauseType.PADDING_SPACING
    assert layer2 == "R0"

    # 3. Outside viewport
    st3 = RootCauseCoverageMatrix.classify_citation_invisible_subtype({"bbox": (10, 900, 200, 950), "page_height": 841.89, "anchor_exists": True})
    assert st3 == CitationInvisibleSubtype.CITATION_OUTSIDE_VIEWPORT
    cause3, layer3, _ = RootCauseCoverageMatrix.resolve_citation_subtype_strategy(st3)
    assert cause3 == RootCauseType.CONTENT_DENSITY
    assert layer3 == "R2"

    # 4. Anchor missing
    st4 = RootCauseCoverageMatrix.classify_citation_invisible_subtype({"anchor_exists": False})
    assert st4 == CitationInvisibleSubtype.CITATION_ANCHOR_MISSING
    cause4, layer4, strats4 = RootCauseCoverageMatrix.resolve_citation_subtype_strategy(st4)
    assert cause4 == RootCauseType.EVIDENCE_MAPPING
    assert layer4 == "R3"
    assert "scientific_citation_linking" in strats4


# ── Scenario H: Worksheet repetition streak -> worksheet-specific strategy only ──
def test_scenario_h_worksheet_repetition_streak_isolated_to_worksheet_strategies():
    all_strats = list(DEFAULT_STRATEGY_REGISTRY.all_strategies())
    eligible, rejections = RepairStrategyCompatibilityFirewall.filter_eligible_strategies(
        strategies=all_strats,
        artifact_type="WORKSHEET",
        root_cause=RootCauseType.SEMANTIC_LAYOUT_MAPPING,
    )
    # Must only contain worksheet strategies
    assert len(eligible) > 0
    for s in eligible:
        assert "WORKSHEET" in [t.upper() for t in s.supported_artifact_types]
        assert "PRESENTATION" not in [t.upper() for t in s.supported_artifact_types]


# ── Scenario I: Repeated mutation causes same state hash -> strategy stagnation ──
def test_scenario_i_repeated_state_hash_stagnation():
    controller = ProductionConvergenceController(max_iterations=5)
    rep = UnifiedQualityReport(
        artifact_type="PRESENTATION",
        decision=ExportDecision.REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        overall_quality_score=0.70,
    )
    controller.advance_iteration()
    controller.evaluate(rep, "state_alpha")
    controller.advance_iteration()
    controller.evaluate(rep, "state_beta")
    controller.advance_iteration()
    res = controller.evaluate(rep, "state_alpha")

    assert res.outcome == ProductionConvergenceOutcome.OSCILLATION_DETECTED
    assert res.should_terminate is True
    assert res.stagnation_reason == StagnationReason.STRATEGY_LOOP


# ── Scenario J: Strategy fixes target finding but creates new hard blocker -> rollback ──
def test_scenario_j_strategy_fixes_finding_but_creates_new_blocker_marked_regressive():
    attempt = RepairAttempt(
        attempt_id="att_reg",
        artifact_type="PRESENTATION",
        iteration=1,
        finding_ids=("TEXT_OVERFLOW",),
        strategy_id="presentation_density_split",
        mutation_scope=RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING,
        owning_layer="R2",
        pre_state_hash="h0",
        post_state_hash="h1",
    )
    res = RepairEffectivenessResult.evaluate(
        attempt=attempt,
        pre_blockers=["TEXT_OVERFLOW"],
        post_blockers=["UNSUPPORTED_SCIENTIFIC_CLAIM"],  # New blocker created!
        pre_findings=["TEXT_OVERFLOW"],
        post_findings=["UNSUPPORTED_SCIENTIFIC_CLAIM"],
        pre_score=0.75,
        post_score=0.60,
    )
    assert res.regression_introduced is True
    assert res.overall_status == EffectivenessStatus.REGRESSIVE
    assert res.new_hard_blocker_count == 1
    assert "introduced 1 new blockers" in res.rationale


# ── Scenario K: Root cause fingerprint changes -> previously disqualified strategy reconsidered ──
def test_scenario_k_defect_signature_change_reconsiders_disqualified_strategy():
    memory = SelfDisqualifyingStrategyMemory()
    key = StrategyHistoryKey(
        artifact_type="PRESENTATION",
        artifact_id="p1",
        root_cause_cluster="GRID_GEOMETRY",
        strategy_id="presentation_padding_adjust",
    )
    att = RepairAttempt(attempt_id="a1", artifact_type="PRESENTATION", iteration=1, strategy_id="presentation_padding_adjust", mutation_scope=RepairMutationScope.LEVEL_1_LOCAL_TOKEN, owning_layer="R0", pre_state_hash="h1", post_state_hash="h2")
    res = RepairEffectivenessResult(attempt_id="a1", strategy_id="presentation_padding_adjust", artifact_type="PRESENTATION", overall_status=EffectivenessStatus.INEFFECTIVE)
    # Disqualify for signature "ELEMENT_COLLISION"
    memory.record_attempt_result(key, res, "ELEMENT_COLLISION", "h2")
    memory.record_attempt_result(key, res, "ELEMENT_COLLISION", "h3")

    # Under same signature -> disqualified
    is_dis, _ = memory.is_strategy_disqualified("PRESENTATION", "p1", "GRID_GEOMETRY", "presentation_padding_adjust", current_defect_signature="ELEMENT_COLLISION")
    assert is_dis is True

    # Under materially altered signature (e.g. now only MARGIN_VIOLATION) -> unblocked!
    is_dis_new, _ = memory.is_strategy_disqualified("PRESENTATION", "p1", "GRID_GEOMETRY", "presentation_padding_adjust", current_defect_signature="MARGIN_VIOLATION")
    assert is_dis_new is False


# ── Scenario L: Budget exhaustion report contains causal explanation ──
def test_scenario_l_budget_exhaustion_contains_causal_explanation():
    controller = ProductionConvergenceController(max_iterations=2)
    rep = UnifiedQualityReport(
        artifact_type="PRESENTATION",
        decision=ExportDecision.REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        overall_quality_score=0.70,
        hard_blockers=("ELEMENT_COLLISION",),
    )
    controller.advance_iteration()
    controller.evaluate(rep, "h1")
    controller.advance_iteration()
    res = controller.evaluate(rep, "h2")

    assert res.outcome == ProductionConvergenceOutcome.BUDGET_EXHAUSTED
    assert res.stagnation_reason == StagnationReason.BUDGET_EXHAUSTED
    assert "Maximum allowed repair iterations (2) exhausted without convergence" in res.rationale


# ── Scenario M: Manual review includes complete repair forensic chain (16 sections) ──
def test_scenario_m_manual_review_produces_16_section_forensics(tmp_path: Path):
    context = ArtifactProductionContext(
        job_id="job_forensic_test",
        artifact_type="PRESENTATION",
        source_input="test",
        output_dir=tmp_path,
    )
    context.quality_authority_result = UnifiedQualityReport(
        artifact_type="PRESENTATION",
        decision=ExportDecision.MANUAL_REVIEW_REQUIRED,
        can_export=False,
        repair_required=False,
        overall_quality_score=0.88,
        hard_blockers=("ELEMENT_COLLISION",),
        findings=(QualityFinding(failure_code="ELEMENT_COLLISION", message="Cards collided"),),
    )

    attempt = RepairAttempt(
        attempt_id="att_m",
        artifact_type="PRESENTATION",
        iteration=1,
        finding_ids=("ELEMENT_COLLISION",),
        root_cause_ids=("GRID_GEOMETRY",),
        strategy_id="presentation_component_reflow",
        mutation_scope=RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
        owning_layer="R1",
        pre_state_hash="h0",
        post_state_hash="h1",
    )
    eff = RepairEffectivenessResult(
        attempt_id="att_m",
        strategy_id="presentation_component_reflow",
        artifact_type="PRESENTATION",
        overall_status=EffectivenessStatus.INEFFECTIVE,
        rationale="Component reflow attempted but collision remained.",
    )

    json_p, md_p = RepairForensicsExporter.export_forensics(
        context=context,
        output_dir=tmp_path,
        attempts=[attempt],
        effectiveness_results=[eff],
        final_failure_reason="Persistent collision on slide 2.",
        recommended_owning_layer="R1",
    )

    assert json_p.exists()
    assert md_p.exists()

    md_content = md_p.read_text(encoding="utf-8")
    for sec_num in range(1, 17):
        assert f"## {sec_num}." in md_content


# ── Scenario N: No eligible safe strategy -> explicit NON_AUTOMATABLE route ──
def test_scenario_n_no_eligible_safe_strategy_routes_to_manual_review():
    decision = CausalEscalationEngine.resolve_escalation(
        artifact_type="SCIENTIFIC_DOCUMENT",
        finding_code="SOURCE_CONTRADICTION",
        root_cause=RootCauseType.SOURCE_INSUFFICIENCY,
        previous_result=None,
        memory=SelfDisqualifyingStrategyMemory(),
        available_strategies=[],
        current_scope=RepairMutationScope.LEVEL_5_ARTIFACT_STRUCTURE,
    )
    assert decision.escalation_reason == RepairEscalationReason.NON_AUTOMATABLE_DEFECT
    assert decision.is_terminal_manual_review is True
    assert "non-automatable; escalating to manual review" in decision.rationale


# ── Scenario O: Cross-artifact strategy registry mutation test ──
def test_scenario_o_cross_artifact_strategy_registry_isolation():
    # Attempting to query worksheet strategies with Presentation type should never return presentation strategies
    eligible_worksheet, _ = RepairStrategyCompatibilityFirewall.filter_eligible_strategies(
        strategies=DEFAULT_STRATEGY_REGISTRY.all_strategies(),
        artifact_type="WORKSHEET",
    )
    eligible_presentation, _ = RepairStrategyCompatibilityFirewall.filter_eligible_strategies(
        strategies=DEFAULT_STRATEGY_REGISTRY.all_strategies(),
        artifact_type="PRESENTATION",
    )

    ws_ids = {s.strategy_id for s in eligible_worksheet}
    pres_ids = {s.strategy_id for s in eligible_presentation}

    # Intersections of format-exclusive strategies must be completely disjoint
    assert "presentation_padding_adjust" in pres_ids
    assert "presentation_padding_adjust" not in ws_ids

    assert "worksheet_anti_spoiling_repair" in ws_ids
    assert "worksheet_anti_spoiling_repair" not in pres_ids

    assert "scientific_citation_linking" not in ws_ids
    assert "scientific_citation_linking" not in pres_ids
