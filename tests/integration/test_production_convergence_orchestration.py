"""
Universal Document Intelligence System V5 — Phase 3D Production Orchestration Test Suite.

Validates end-to-end production convergence orchestration, state machine transitions,
closed-loop repair convergence, export governance, and adversarial safety across all 4 artifact types.
Scenarios 1 through 25.
"""

from pathlib import Path
import pytest
import time

from app.orchestration.production_state import (
    IllegalStateTransitionError,
    ProductionState,
    ProductionStateMachine,
)
from app.orchestration.production_context import ArtifactProductionContext
from app.orchestration.execution_profiles import ArtifactExecutionProfileRegistry
from app.orchestration.decision_router import DecisionRouteAction, QualityDecisionRouter
from app.orchestration.escalation_router import RepairEscalationLayer, RepairEscalationRouter
from app.orchestration.convergence_controller import (
    ProductionConvergenceController,
    ProductionConvergenceOutcome,
)
from app.orchestration.versioning import ProductionVersionManager
from app.orchestration.export_gate import AuthorizedExportGate, UnauthorizedExportError
from app.orchestration.failures import ProductionFailureRecord, ProductionFailureType
from app.orchestration.production_orchestrator import (
    ProductionOrchestrator,
    ProductionRequest,
)
from app.orchestration.stage_registry import (
    PIPELINE_STAGES,
    TOTAL_PIPELINE_STAGES,
    PipelineProgressReporter,
    PipelineStage,
    PipelineStageRegistry,
)
from app.quality.contracts.authority import UnifiedQualityReport
from app.quality.contracts.decisions import ExportDecision
from app.quality.contracts.findings import FindingCluster, QualityFinding
from app.quality.contracts.signals import QualityDomain, SignalSeverity
from app.quality.repair.contracts import ConvergenceState, RepairPlan, RepairTarget
from app.quality.repair.mutation_contract import RepairMutationScope
from app.quality.repair.mutation_budget import MutationBudgetTracker, get_budget_for_artifact
from app.quality.repair.planner import CandidateRepairOption, MinimalInterventionRepairPlanner
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType
from app.quality.repair.safety_invariants import RepairSafetyInvariants
from app.quality.repair.strategies.presentation import (
    PresentationDensitySplitStrategy,
    PresentationPaddingAdjustmentStrategy,
)
from app.quality.repair.strategies.scientific import ScientificClaimDowngradeStrategy
from app.quality.repair.strategies.worksheet import WorksheetAntiSpoilingRepairStrategy
from app.quality.repair.transaction import RepairTransactionManager
from app.intelligence.transformation.blueprints import (
    LearningActivity,
    LearningActivityType,
    ScientificArgumentRole,
    ScientificArgumentUnit,
    ScientificDocumentBlueprint,
    WorksheetBlueprint,
)
from app.intelligence.transformation.intent import ArtifactType, get_default_intent


# ============================================================================
# 1. State Machine & Governance Tests (Scenarios 15, 16, 17, 18)
# ============================================================================

def test_01_illegal_state_transition_rendered_to_exported_rejected():
    """Scenario 15: RENDERED -> EXPORTED without Quality Authority is strictly rejected."""
    sm = ProductionStateMachine(initial_state=ProductionState.CREATED)
    sm.transition(ProductionState.SOURCE_VALIDATING)
    sm.transition(ProductionState.SOURCE_PARSED)
    sm.transition(ProductionState.KNOWLEDGE_PROCESSING)
    sm.transition(ProductionState.KNOWLEDGE_READY)
    sm.transition(ProductionState.INTENT_RESOLUTION)
    sm.transition(ProductionState.INTENT_READY)
    sm.transition(ProductionState.TRANSFORMATION)
    sm.transition(ProductionState.BLUEPRINT_READY)
    sm.transition(ProductionState.GROUPING)
    sm.transition(ProductionState.COMPOSITION_READY)
    sm.transition(ProductionState.RENDERING)
    sm.transition(ProductionState.RENDERED)

    with pytest.raises(IllegalStateTransitionError) as exc_info:
        sm.transition(ProductionState.EXPORTED)
    assert "cannot bypass Quality Authority" in str(exc_info.value)


def test_02_export_without_authority_rejected(tmp_path: Path):
    """Scenario 16: Exporting without Quality Authority evaluation raises UnauthorizedExportError."""
    context = ArtifactProductionContext(
        job_id="job_unauth",
        artifact_type="PRESENTATION",
        source_input="test",
        output_dir=tmp_path,
    )
    vm = ProductionVersionManager(base_output_dir=tmp_path, artifact_name="test")

    with pytest.raises(UnauthorizedExportError) as exc:
        AuthorizedExportGate.verify_and_export(context, vm)
    assert "was never performed" in str(exc.value)


def test_03_blocked_artifact_cannot_export(tmp_path: Path):
    """Scenario 17: Blocked artifact cannot export even if state is forced."""
    context = ArtifactProductionContext(
        job_id="job_blocked",
        artifact_type="PRESENTATION",
        source_input="test",
        output_dir=tmp_path,
    )
    vm = ProductionVersionManager(base_output_dir=tmp_path, artifact_name="test")

    report = UnifiedQualityReport(
        artifact_type="PRESENTATION",
        decision=ExportDecision.BLOCKED,
        can_export=False,
        repair_required=False,
        overall_quality_score=0.40,
        hard_blockers=("UNRECOVERABLE_DEFECT",),
    )
    context.quality_authority_result = report

    with pytest.raises(UnauthorizedExportError) as exc:
        AuthorizedExportGate.verify_and_export(context, vm)
    assert "Export rejected by Quality Authority: Decision=BLOCKED" in str(exc.value)


def test_04_manual_review_artifact_cannot_auto_export(tmp_path: Path):
    """Scenario 18: Manual review artifact cannot auto-export."""
    context = ArtifactProductionContext(
        job_id="job_mr",
        artifact_type="PRESENTATION",
        source_input="test",
        output_dir=tmp_path,
    )
    vm = ProductionVersionManager(base_output_dir=tmp_path, artifact_name="test")

    report = UnifiedQualityReport(
        artifact_type="PRESENTATION",
        decision=ExportDecision.MANUAL_REVIEW_REQUIRED,
        can_export=False,
        repair_required=False,
        overall_quality_score=0.65,
        hard_blockers=("SOURCE_CONTRADICTION",),
    )
    context.quality_authority_result = report

    with pytest.raises(UnauthorizedExportError):
        AuthorizedExportGate.verify_and_export(context, vm)


# ============================================================================
# 2. Decision Routing & Escalation Tests (Scenarios 1, 2, 3, 4)
# ============================================================================

def test_05_approved_artifact_routes_directly_to_export():
    """Scenario 1: EXPORT_APPROVED routes to PROCEED_TO_EXPORT."""
    rep = UnifiedQualityReport(
        artifact_type="PRESENTATION",
        decision=ExportDecision.EXPORT_APPROVED,
        can_export=True,
        repair_required=False,
        overall_quality_score=0.95,
    )
    route = QualityDecisionRouter.route_decision(rep)
    assert route.action == DecisionRouteAction.PROCEED_TO_EXPORT
    assert route.can_export is True
    assert route.is_terminal is True


def test_06_warning_artifact_routes_to_export_with_warnings():
    """Scenario 2: EXPORT_APPROVED_WITH_WARNINGS routes to PROCEED_TO_EXPORT_WITH_WARNINGS."""
    rep = UnifiedQualityReport(
        artifact_type="HANDOUT",
        decision=ExportDecision.EXPORT_APPROVED_WITH_WARNINGS,
        can_export=True,
        repair_required=False,
        overall_quality_score=0.82,
        warnings=("MINOR_MARGIN_TRIM",),
    )
    route = QualityDecisionRouter.route_decision(rep)
    assert route.action == DecisionRouteAction.PROCEED_TO_EXPORT_WITH_WARNINGS
    assert route.can_export is True
    assert len(route.warnings) == 1


def test_07_render_defect_escalates_to_minimal_token_layer():
    """Scenario 3: TEXT_CLIPPING routes to LEVEL_R0_RENDER_TOKEN."""
    finding = QualityFinding(failure_code="TEXT_CLIPPING", domain=QualityDomain.RENDERED)
    plan = RepairEscalationRouter.resolve_escalation(findings=[finding])
    assert plan.layer == RepairEscalationLayer.LEVEL_R0_RENDER_TOKEN
    assert plan.target_scope == RepairMutationScope.LEVEL_1_LOCAL_TOKEN
    assert plan.requires_re_transform is False


def test_08_semantic_defect_escalates_to_transformation_layer():
    """Scenario 4: UNSUPPORTED_SCIENTIFIC_CLAIM escalates to LEVEL_R4."""
    finding = QualityFinding(failure_code="UNSUPPORTED_SCIENTIFIC_CLAIM", domain=QualityDomain.SEMANTIC)
    plan = RepairEscalationRouter.resolve_escalation(findings=[finding])
    assert plan.layer == RepairEscalationLayer.LEVEL_R4_SEMANTIC_TRANSFORMATION
    assert plan.requires_re_transform is True


# ============================================================================
# 3. Convergence & Iteration Protection Tests (Scenarios 5, 6, 7, 8, 9, 24)
# ============================================================================

def test_09_state_oscillation_trapped_by_convergence_controller():
    """Scenarios 9 & 24: Cyclical state alternation (A -> B -> A) triggers OSCILLATION_DETECTED."""
    controller = ProductionConvergenceController(max_iterations=5)
    rep = UnifiedQualityReport(
        artifact_type="PRESENTATION",
        decision=ExportDecision.REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        overall_quality_score=0.72,
    )

    controller.advance_iteration()
    res1 = controller.evaluate(rep, "hash_state_A")
    assert res1.outcome == ProductionConvergenceOutcome.CONTINUE_REPAIR

    controller.advance_iteration()
    res2 = controller.evaluate(rep, "hash_state_B")
    assert res2.outcome == ProductionConvergenceOutcome.CONTINUE_REPAIR

    controller.advance_iteration()
    res3 = controller.evaluate(rep, "hash_state_A")
    assert res3.outcome == ProductionConvergenceOutcome.OSCILLATION_DETECTED
    assert res3.cycle_detected is True
    assert res3.should_terminate is True


def test_10_budget_exhaustion_terminates_safely():
    """Scenario 8: Reaching max iterations terminates with BUDGET_EXHAUSTED."""
    controller = ProductionConvergenceController(max_iterations=2)
    rep = UnifiedQualityReport(
        artifact_type="PRESENTATION",
        decision=ExportDecision.REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        overall_quality_score=0.72,
    )

    controller.advance_iteration()
    controller.evaluate(rep, "hash_1")
    controller.advance_iteration()
    res = controller.evaluate(rep, "hash_2")

    assert res.outcome == ProductionConvergenceOutcome.BUDGET_EXHAUSTED
    assert res.should_terminate is True


# ============================================================================
# 4. Invariant & Adversarial Protection Tests (Scenarios 10, 11, 12, 13, 14)
# ============================================================================

def test_11_worksheet_answer_leak_purged_safely():
    """Scenario 11: Worksheet answer key is purged from student text, not hidden."""
    act = LearningActivity(
        activity_id="act_1",
        sequence_index=1,
        activity_type=LearningActivityType.PREDICTION,
        title="Prediksi",
        prompt_text="Amati oobleck, karena kuncinya adalah cairan mengeras.",
        target_knowledge_unit_ids=("u1",),
        scaffolding_level="guided",
        withhold_explanation=False,
        expected_reasoning_type="PREDICTION",
    )
    ws = WorksheetBlueprint(
        blueprint_id="ws_1",
        artifact_type=ArtifactType.WORKSHEET,
        source_manifest_id="sm_1",
        document_title="LKS",
        intent=get_default_intent(ArtifactType.WORKSHEET),
        activities=(act,),
    )
    target = RepairTarget(artifact_type="WORKSHEET", element_id="act_1")
    hyp = RootCauseHypothesis(
        root_cause_id="rc_ws",
        cause_type=RootCauseType.INQUIRY_STRUCTURE,
        confidence=1.0,
        affected_targets=(target,),
        supporting_findings=(QualityFinding(failure_code="ANTI_SPOILING_BREACH"),),
    )
    strat = WorksheetAntiSpoilingRepairStrategy()
    plan = strat.plan_repair(ws, target, hyp)
    repaired_ws, _ = strat.apply_repair(ws, plan)

    assert "kuncinya adalah" not in repaired_ws.activities[0].prompt_text
    assert repaired_ws.activities[0].withhold_explanation is True


def test_12_scientific_unsupported_claim_never_fabricates_evidence():
    """Scenario 12: Scientific claim is hedged; evidence list remains empty (zero fabrication)."""
    arg = ScientificArgumentUnit(
        argument_id="arg_1",
        sequence_index=1,
        claim_unit_id="c_1",
        argument_role=ScientificArgumentRole.BACKGROUND_CLAIM,
        claim_statement="Secara mutlak membuktikan bahwa materi tidak dapat dihancurkan.",
        supporting_evidence_unit_ids=(),  # Unsupported!
        confidence=1.0,
    )
    kti = ScientificDocumentBlueprint(
        blueprint_id="bp_sci",
        artifact_type=ArtifactType.SCIENTIFIC_DOCUMENT,
        source_manifest_id="sm_1",
        document_title="KTI",
        intent=get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT),
        arguments=(arg,),
    )
    target = RepairTarget(artifact_type="SCIENTIFIC_DOCUMENT", element_id="c_1")
    hyp = RootCauseHypothesis(
        root_cause_id="rc_sci",
        cause_type=RootCauseType.EVIDENCE_MAPPING,
        confidence=0.9,
        affected_targets=(target,),
        supporting_findings=(QualityFinding(failure_code="UNSUPPORTED_SCIENTIFIC_CLAIM"),),
    )
    strat = ScientificClaimDowngradeStrategy()
    plan = strat.plan_repair(kti, target, hyp)
    repaired_kti, _ = strat.apply_repair(kti, plan)

    assert "berdasarkan pengamatan awal terindikasi bahwa" in repaired_kti.arguments[0].claim_statement
    assert len(repaired_kti.arguments[0].supporting_evidence_unit_ids) == 0


def test_13_presentation_clipping_prefers_minimal_intervention():
    """Scenario 13: Presentation clipping selects local padding (Level 1) over slide split (Level 4)."""
    class MockDeck:
        def __init__(self):
            self.slides = []

    target = RepairTarget(artifact_type="PRESENTATION", element_id="s1")
    hyp = RootCauseHypothesis(
        root_cause_id="rc1",
        cause_type=RootCauseType.CONTENT_DENSITY,
        confidence=0.9,
        affected_targets=(target,),
        supporting_findings=(QualityFinding(failure_code="TEXT_CLIPPING", domain=QualityDomain.RENDERED),),
    )
    budget = MutationBudgetTracker(get_budget_for_artifact("PRESENTATION"))
    strats = [PresentationDensitySplitStrategy(), PresentationPaddingAdjustmentStrategy()]

    candidates = MinimalInterventionRepairPlanner.evaluate_candidates(strats, target, hyp, budget, MockDeck())
    assert candidates[0].strategy_id == "presentation_padding_adjust"
    assert candidates[0].mutation_scope == RepairMutationScope.LEVEL_1_LOCAL_TOKEN


# ============================================================================
# 5. Architecture, Versioning & Failure Taxonomy Tests (Scenarios 19, 20, 21, 22, 23)
# ============================================================================

def test_14_iteration_versioning_and_provenance(tmp_path: Path):
    """Scenario 19: All iterations preserved in iteration_n/ and final/ packaging."""
    vm = ProductionVersionManager(base_output_dir=tmp_path, artifact_name="test_doc")

    class MockBP:
        def model_dump_json(self, **kwargs):
            return '{"title": "test"}'

    dummy_pdf = tmp_path / "dummy.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4 dummy")

    snap0 = vm.record_iteration(0, MockBP(), pdf_path=dummy_pdf)
    assert snap0.iteration == 0
    assert (tmp_path / "iteration_0" / "blueprint.json").exists()
    assert (tmp_path / "iteration_0" / "test_doc.pdf").exists()

    final_dir = vm.package_final(
        approved_iteration=0,
        provenance_data={"job": 1},
        quality_markdown="# Quality Pass",
        generation_summary={"status": "ok"},
    )
    assert (final_dir / "test_doc.pdf").exists()
    assert (final_dir / "quality_report.md").exists()
    assert (final_dir / "manifest.json").exists()


def test_15_four_artifact_profiles_registered():
    """Scenario 20: All four artifact types configured in profile registry."""
    for art in ("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"):
        profile = ArtifactExecutionProfileRegistry.get_profile(art)
        assert profile.artifact_type == art
        assert callable(profile.transformer_factory)
        assert callable(profile.bridge_factory)
        assert callable(profile.executor_factory)


def test_16_canonical_progress_denominator_invariant():
    """Scenario 21: Canonical stage registry maintains strictly 10 stages."""
    assert PipelineStageRegistry.total_stages() == 10
    assert TOTAL_PIPELINE_STAGES == 10
    assert len(PIPELINE_STAGES) == 10


def test_17_failure_taxonomy_distinguishes_failure_types():
    """Scenarios 22 & 23: Renderer failure vs Quality failure differentiated."""
    f_render = ProductionFailureRecord(
        failure_type=ProductionFailureType.RENDER_FAILURE,
        owning_layer="RendererExecutor",
        message="Chromium timeout",
        recoverability="RECOVERABLE",
        repair_eligible=False,
        human_action_required=False,
    )
    f_quality = ProductionFailureRecord(
        failure_type=ProductionFailureType.QUALITY_FAILURE,
        owning_layer="UnifiedQualityAuthority",
        message="Text clipping on page 2",
        recoverability="RECOVERABLE",
        repair_eligible=True,
        human_action_required=False,
    )
    assert f_render.failure_type == ProductionFailureType.RENDER_FAILURE
    assert f_quality.failure_type == ProductionFailureType.QUALITY_FAILURE
    assert f_quality.repair_eligible is True
    assert f_render.repair_eligible is False


# ============================================================================
# 6. End-to-End Orchestrator Execution Test (Scenario 25)
# ============================================================================

@pytest.mark.asyncio
async def test_18_production_orchestrator_end_to_end_presentation(tmp_path: Path):
    """Scenario 25: Complete ProductionOrchestrator run on Oobleck fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "oobleck_experiment.md"
    assert fixture_path.exists()
    raw_input = fixture_path.read_text(encoding="utf-8")

    orchestrator = ProductionOrchestrator()
    req = ProductionRequest(
        raw_input=raw_input,
        artifact_type="PRESENTATION",
        output_dir=tmp_path,
        job_id="test_e2e_pres",
        source_filename="oobleck_experiment.md",
    )

    outcome = await orchestrator.produce(req)
    assert outcome.job_id == "test_e2e_pres"
    assert outcome.artifact_type == "PRESENTATION"
    assert outcome.final_state in (
        ProductionState.EXPORTED,
        ProductionState.APPROVED,
        ProductionState.APPROVED_WITH_WARNINGS,
        ProductionState.MANUAL_REVIEW_REQUIRED,
    )
    assert outcome.quality_report is not None
    assert outcome.timing_metrics is not None


@pytest.mark.asyncio
async def test_19_production_orchestrator_end_to_end_handout_export(tmp_path: Path):
    """Scenario 26: Complete ProductionOrchestrator run on Handout producing verified export package."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "oobleck_experiment.md"
    assert fixture_path.exists()
    raw_input = fixture_path.read_text(encoding="utf-8")

    orchestrator = ProductionOrchestrator()
    req = ProductionRequest(
        raw_input=raw_input,
        artifact_type="HANDOUT",
        output_dir=tmp_path,
        job_id="test_e2e_handout",
        source_filename="oobleck_experiment.md",
    )

    outcome = await orchestrator.produce(req)
    assert outcome.job_id == "test_e2e_handout"
    assert outcome.artifact_type == "HANDOUT"
    assert outcome.success is True
    assert outcome.final_state == ProductionState.EXPORTED
    assert outcome.export_package is not None
    assert (tmp_path / "test_e2e_handout" / "final" / "handout_artifact.html").exists()
    assert (tmp_path / "test_e2e_handout" / "final" / "handout_artifact.pdf").exists()
    assert (tmp_path / "test_e2e_handout" / "final" / "manifest.json").exists()
    assert outcome.quality_report is not None
    assert outcome.quality_report.overall_quality_score > 0.85


@pytest.mark.asyncio
@pytest.mark.parametrize("artifact_type", ["PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"])
async def test_20_multi_artifact_production_benchmark_matrix(artifact_type: str, tmp_path: Path):
    """Part 14 Benchmark: Closed-loop multi-artifact convergence verification across all 4 formats."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "oobleck_experiment.md"
    raw_input = fixture_path.read_text(encoding="utf-8")

    orchestrator = ProductionOrchestrator()
    req = ProductionRequest(
        raw_input=raw_input,
        artifact_type=artifact_type,
        output_dir=tmp_path,
        job_id=f"bench_{artifact_type.lower()}",
        source_filename="oobleck_experiment.md",
    )

    outcome = await orchestrator.produce(req)
    assert outcome.artifact_type == artifact_type
    assert outcome.final_state in (
        ProductionState.EXPORTED,
        ProductionState.APPROVED,
        ProductionState.APPROVED_WITH_WARNINGS,
        ProductionState.MANUAL_REVIEW_REQUIRED,
    )
    assert outcome.quality_report is not None
    assert outcome.overall_quality_score > 0.70
    assert outcome.total_iterations >= 0
    assert "total_runtime" in outcome.timing_metrics


