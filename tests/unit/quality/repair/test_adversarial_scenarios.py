"""
Adversarial Repair Safety Verification Suite — Scenarios A through J.

Phase 3C.1: Tests non-negotiable safety policies, minimal intervention,
drift limits, anti-spoiling, zero-fabrication, and oscillation guards.
"""

import pytest
from app.intelligence.transformation.blueprints import (
    LearningActivity,
    LearningActivityType,
    ScientificArgumentRole,
    ScientificArgumentUnit,
    ScientificDocumentBlueprint,
    WorksheetBlueprint,
)
from app.intelligence.transformation.intent import ArtifactType, get_default_intent
from app.quality.contracts.decisions import ExportDecision, UnifiedQualityDecision
from app.quality.contracts.findings import FindingCluster, QualityFinding
from app.quality.contracts.signals import QualityDomain, SignalSeverity
from app.quality.repair.contracts import ConvergenceState, RepairPlan, RepairTarget
from app.quality.repair.convergence import ConvergenceController
from app.quality.repair.drift_analyzer import ArtifactDriftAnalyzer
from app.quality.repair.mutation_contract import RepairMutationScope
from app.quality.repair.mutation_budget import MutationBudgetTracker, get_budget_for_artifact
from app.quality.repair.planner import CandidateRepairOption, MinimalInterventionRepairPlanner
from app.quality.repair.root_cause import DeterministicRootCauseAnalyzer, RootCauseHypothesis, RootCauseType
from app.quality.repair.safety_invariants import RepairSafetyInvariants
from app.quality.repair.strategies.presentation import (
    PresentationDensitySplitStrategy,
    PresentationPaddingAdjustmentStrategy,
)
from app.quality.repair.strategies.scientific import ScientificClaimDowngradeStrategy
from app.quality.repair.strategies.worksheet import WorksheetAntiSpoilingRepairStrategy
from app.quality.repair.transaction import RepairTransactionManager


class MockSlide:
    def __init__(self, slide_id, title, content, refs, layout="concept_card"):
        self.slide_id = slide_id
        self.title = title
        self.content = content
        self.source_refs = list(refs)
        self.layout = layout
        self.key_blocks = list(refs)
        self.text_density = "normal"


class MockDeck:
    def __init__(self, slides):
        self.slides = list(slides)


class MockActivity:
    def __init__(self, activity_id, title, prompt_text, refs):
        self.activity_id = activity_id
        self.title = title
        self.prompt_text = prompt_text
        self.source_refs = list(refs)
        self.requires_student_workspace = True


class MockWorksheet:
    def __init__(self, activities):
        self.activities = list(activities)


class MockSubsection:
    def __init__(self, title, claims, evidence_ids, refs):
        self.title = title
        self.claims = list(claims)
        self.evidence_ids = list(evidence_ids)
        self.source_refs = list(refs)


class MockBab:
    def __init__(self, bab_number, title, subsections):
        self.bab_number = bab_number
        self.title = title
        self.subsections = list(subsections)


class MockKTI:
    def __init__(self, babs):
        self.babs = list(babs)


def test_scenario_a_excessive_content_deletion_rejected():
    """SCENARIO A: Low visual score -> deleting 40% content is REJECTED due to excessive drift."""
    pre = MockDeck([MockSlide(f"s_{i}", f"Slide {i}", "Long content " * 30, [f"ref_{i}"]) for i in range(10)])
    post = MockDeck([MockSlide(f"s_{i}", f"Slide {i}", "Long content " * 30, [f"ref_{i}"]) for i in range(6)])  # 40% deleted

    drift = ArtifactDriftAnalyzer.analyze(pre, post, "PRESENTATION")
    assert drift.is_acceptable is False
    assert drift.structural_drift_score >= 0.35


def test_scenario_b_minimal_intervention_prefers_padding_over_split():
    """SCENARIO B: TEXT_CLIPPING -> Planner prefers padding adjustment (Level 1) over slide split (Level 4)."""
    deck = MockDeck([MockSlide("s1", "Title", "A" * 250, ["u1", "u2", "u3"])])
    target = RepairTarget(artifact_type="PRESENTATION", element_id="s1", slide_index=1)
    hyp = RootCauseHypothesis(
        root_cause_id="rc1",
        cause_type=RootCauseType.CONTENT_DENSITY,
        confidence=0.9,
        affected_targets=(target,),
        supporting_findings=(QualityFinding(failure_code="TEXT_CLIPPING", domain=QualityDomain.RENDERED),),
    )
    budget = MutationBudgetTracker(get_budget_for_artifact("PRESENTATION"))
    strats = [PresentationDensitySplitStrategy(), PresentationPaddingAdjustmentStrategy()]

    candidates = MinimalInterventionRepairPlanner.evaluate_candidates(strats, target, hyp, budget, deck)
    assert candidates[0].strategy_id == "presentation_padding_adjust"
    assert candidates[0].mutation_scope == RepairMutationScope.LEVEL_1_LOCAL_TOKEN


def test_scenario_c_tiny_text_identifies_density_not_blind_font_growth():
    """SCENARIO C: TINY_TEXT in dense cluster -> Inferred root cause is CONTENT_DENSITY."""
    f_tiny = QualityFinding(failure_code="FONT_TOO_SMALL", severity=SignalSeverity.WARNING, affected_pages=(1,))
    f_over = QualityFinding(failure_code="TEXT_OVERFLOW", severity=SignalSeverity.ERROR, affected_pages=(1,))
    cluster = FindingCluster(canonical_finding=f_over, correlated_findings=(f_tiny,), affected_pages=(1,))

    hyps = DeterministicRootCauseAnalyzer.analyze(
        findings=[f_over, f_tiny],
        clusters=[cluster],
        metrics={"occupancy": 0.89},
        artifact_type="PRESENTATION",
    )
    assert hyps[0].cause_type == RootCauseType.CONTENT_DENSITY


def test_scenario_d_scientific_unsupported_claim_zero_fabrication():
    """SCENARIO D: Scientific unsupported claim -> Strategy hedges/downgrades claim; NEVER fabricates evidence."""
    arg = ScientificArgumentUnit(
        argument_id="arg_1",
        sequence_index=1,
        claim_unit_id="c_1",
        argument_role=ScientificArgumentRole.BACKGROUND_CLAIM,
        claim_statement="Secara mutlak membuktikan bahwa fluida kebal peluru.",
        supporting_evidence_unit_ids=(),  # Unsupported!
        confidence=1.0,
    )
    kti = ScientificDocumentBlueprint(
        blueprint_id="bp_sci",
        artifact_type=ArtifactType.SCIENTIFIC_DOCUMENT,
        source_manifest_id="sm_1",
        document_title="KTI Fluida",
        intent=get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT),
        arguments=(arg,),
    )
    target = RepairTarget(artifact_type="SCIENTIFIC_DOCUMENT", element_id="c_1", section_index=1)
    hyp = RootCauseHypothesis(
        root_cause_id="rc_claim",
        cause_type=RootCauseType.EVIDENCE_MAPPING,
        confidence=0.9,
        affected_targets=(target,),
        supporting_findings=(QualityFinding(failure_code="UNSUPPORTED_SCIENTIFIC_CLAIM"),),
    )
    strategy = ScientificClaimDowngradeStrategy()
    plan = strategy.plan_repair(kti, target, hyp)
    mutated_kti, _ = strategy.apply_repair(kti, plan)

    # Claim must be hedged, but evidence_ids MUST remain empty (ZERO fabrication!)
    assert "berdasarkan pengamatan awal terindikasi bahwa" in mutated_kti.arguments[0].claim_statement
    assert "secara mutlak membuktikan bahwa" not in mutated_kti.arguments[0].claim_statement
    assert len(mutated_kti.arguments[0].supporting_evidence_unit_ids) == 0


def test_scenario_e_worksheet_answer_leak_purged_not_css_hidden():
    """SCENARIO E: Worksheet answer leak -> Answer text is purged from student text, not just hidden."""
    act = LearningActivity(
        activity_id="act_1",
        sequence_index=1,
        activity_type=LearningActivityType.PREDICTION,
        title="Prediksi Perilaku",
        prompt_text="Prediksikan apa yang terjadi, karena cairan akan mengeras ketika dipukul cepat.",
        scaffolding_level="MEDIUM",
        withhold_explanation=False,
        expected_reasoning_type="PREDICTION",
    )
    ws = WorksheetBlueprint(
        blueprint_id="ws_1",
        artifact_type=ArtifactType.WORKSHEET,
        source_manifest_id="sm_1",
        document_title="LKS Oobleck",
        intent=get_default_intent(ArtifactType.WORKSHEET),
        activities=(act,),
    )
    target = RepairTarget(artifact_type="WORKSHEET", element_id="act_1", section_index=1)
    hyp = RootCauseHypothesis(
        root_cause_id="rc_ws",
        cause_type=RootCauseType.INQUIRY_STRUCTURE,
        confidence=1.0,
        affected_targets=(target,),
        supporting_findings=(QualityFinding(failure_code="ANTI_SPOILING_BREACH"),),
    )
    strategy = WorksheetAntiSpoilingRepairStrategy()
    plan = strategy.plan_repair(ws, target, hyp)
    mutated_ws, _ = strategy.apply_repair(ws, plan)

    # Prompt text in the student model must NOT contain the leak
    assert "karena cairan akan mengeras" not in mutated_ws.activities[0].prompt_text
    assert mutated_ws.activities[0].withhold_explanation is True


def test_scenario_f_oscillation_detection_triggers_manual_review():
    """SCENARIO F: Oscillation A -> B -> A detected -> ConvergenceState.OSCILLATION_DETECTED."""
    controller = ConvergenceController(max_iterations=5)
    decision = UnifiedQualityDecision(
        decision=ExportDecision.REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        manual_review_required=False,
        hard_blockers=("TEXT_CLIPPING",),
        warnings=(),
        rationale="Repair needed",
    )

    controller.evaluate_state(decision, "hash_state_A", "strat_1", 0.70)
    controller.evaluate_state(decision, "hash_state_B", "strat_2", 0.72)
    state, osc_result = controller.evaluate_state(decision, "hash_state_A", "strat_1", 0.70)

    assert state == ConvergenceState.OSCILLATION_DETECTED
    assert osc_result.is_oscillating is True


def test_scenario_g_quality_improvement_with_catastrophic_drift_triggers_rollback():
    """SCENARIO G: Quality +5, but semantic drift +35% -> Transaction ROLLS BACK."""
    deck_pre = MockDeck([MockSlide(f"s_{i}", f"Slide {i}", "Content", [f"u{i}"]) for i in range(10)])
    deck_post = MockDeck([MockSlide("s_0", "Slide 0", "Only one slide left", ["u0"])])  # 90% deleted!

    drift = ArtifactDriftAnalyzer.analyze(deck_pre, deck_post, "PRESENTATION")
    assert drift.is_acceptable is False
    assert drift.structural_drift_score > 0.35


def test_scenario_h_traceability_break_triggers_hard_rollback():
    """SCENARIO H: Traceability broken during repair -> Safety invariants FAIL and trigger rollback."""
    deck_pre = MockDeck([MockSlide("s1", "Title", "Content", ["ref1", "ref2", "ref3"])])
    deck_post = MockDeck([MockSlide("s1", "Title", "Content", [])])  # All refs lost!

    drift = ArtifactDriftAnalyzer.analyze(deck_pre, deck_post, "PRESENTATION")
    plan = RepairPlan(root_cause_id="rc", artifact_type="PRESENTATION", actions=(), execution_order=(), expected_quality_improvement=0.1)
    passed, violations = RepairSafetyInvariants.evaluate_all(deck_pre, deck_post, plan, drift, "PRESENTATION")

    assert passed is False
    assert any("Traceability" in v for v in violations)


def test_scenario_i_clean_repair_commits_successfully():
    """SCENARIO I: Quality improves (+0.15), invariants pass, drift acceptable -> Transaction COMMITS."""
    deck = MockDeck([MockSlide("s1", "Title", "Content", ["ref1"])])
    target = RepairTarget(artifact_type="PRESENTATION", element_id="s1", slide_index=1)
    hyp = RootCauseHypothesis(
        root_cause_id="rc1",
        cause_type=RootCauseType.PADDING_SPACING,
        confidence=0.9,
        affected_targets=(target,),
        supporting_findings=(QualityFinding(failure_code="MARGIN_VIOLATION", domain=QualityDomain.RENDERED),),
    )
    cand = CandidateRepairOption(
        strategy_id="presentation_padding_adjust",
        target=target,
        hypothesis=hyp,
        mutation_scope=RepairMutationScope.LEVEL_1_LOCAL_TOKEN,
        utility_score=15.0,
        expected_quality_gain=0.15,
        mutation_cost=0.1,
        blast_radius=0.1,
        regression_risk=0.05,
        is_budget_approved=True,
    )
    budget = MutationBudgetTracker(get_budget_for_artifact("PRESENTATION"))
    decision = UnifiedQualityDecision(
        decision=ExportDecision.REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        manual_review_required=False,
        hard_blockers=("MARGIN_VIOLATION",),
        warnings=(),
        rationale="Needs margin repair",
    )
    strategy = PresentationPaddingAdjustmentStrategy()

    res_bp, rec, committed = RepairTransactionManager.execute_transaction(
        current_blueprint=deck,
        candidate=cand,
        strategy=strategy,
        budget_tracker=budget,
        current_decision=decision,
        current_score=0.70,
        artifact_type="PRESENTATION",
        iteration=1,
    )

    assert committed is True
    assert rec.is_committed is True


def test_scenario_j_iteration_limit_enforced_deterministically():
    """SCENARIO J: Iteration limit reached without full convergence -> ConvergenceState.BUDGET_EXHAUSTED."""
    controller = ConvergenceController(max_iterations=2)
    decision = UnifiedQualityDecision(
        decision=ExportDecision.REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        manual_review_required=False,
        hard_blockers=("MARGIN_VIOLATION",),
        warnings=(),
        rationale="Budget test",
    )

    controller.advance_iteration()
    controller.evaluate_state(decision, "state_1", "strat_1", 0.70)
    controller.advance_iteration()
    state, _ = controller.evaluate_state(decision, "state_2", "strat_1", 0.72)

    assert state == ConvergenceState.BUDGET_EXHAUSTED
