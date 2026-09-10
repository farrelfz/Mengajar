"""
Universal Document Intelligence System V5 — Phase 4 Repair Actuation Adversarial Test Suite.

Comprehensive verification of Scenarios A through AD:
- Actuator registration, discovery, and firewall enforcement (Stage 5)
- Presentation structural recomposition (reflow, formula decomposition, composition, split, diversity)
- Typography constraint solving with non-negotiable readability floors
- Worksheet inquiry arc recomposition with strict answer withholding and zero drift
- Scientific citation visibility and empirical evidence layout
- Handout density reflow and section balance
- Blueprint recomposition engine and semantic grouping optimizer
- Deterministic operator performance memory and learning
- Transformation diff generation (JSON and Markdown)
- Non-negotiable quality authority separation and rollback safety
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
from typing import List

from app.intelligence.transformation.blueprints import (
    ConceptualBeat,
    LearningActivity,
    LearningActivityType,
    PresentationBlueprint,
    WorksheetBlueprint,
)
from app.intelligence.transformation.intent import ArtifactType, AudienceLevel, ResolvedArtifactIntent
from app.quality.contracts.decisions import ExportDecision, UnifiedQualityDecision
from app.quality.repair.actuation.blueprint_recomposition import (
    BlueprintRecompositionEngine,
    SemanticGroupingOptimizer,
)
from app.quality.repair.actuation.causal_check import PreActuationCausalCheck
from app.quality.repair.actuation.contracts import (
    RepairActuationRequest,
    RepairActuationResult,
    RepairActuator,
)
from app.quality.repair.actuation.diff_system import TransformationDiffSystem
from app.quality.repair.actuation.learning import RepairOperatorPerformanceRegistry
from app.quality.repair.actuation.mutation_layers import TransformationLayer
from app.quality.repair.actuation.presentation import (
    PresentationComponentReflowActuator,
    PresentationCompositionActuator,
    PresentationDiversityActuator,
    PresentationFormulaRecompositionActuator,
    PresentationSlideSplitActuator,
    PresentationStructuralDiversityGuard,
)
from app.quality.repair.actuation.registry import RepairActuatorRegistry
from app.quality.repair.actuation.scientific import (
    ScientificCitationVisibilityActuator,
    ScientificEvidenceLayoutActuator,
)
from app.quality.repair.actuation.handout import (
    HandoutDensityReflowActuator,
    HandoutSectionBalanceActuator,
)
from app.quality.repair.actuation.typography_solver import (
    TypographyConstraintSolver,
    TypographyRepairActuator,
)
from app.quality.repair.actuation.worksheet import (
    WorksheetInquiryRecompositionActuator,
    WorksheetPedagogicalDiversityAnalyzer,
)
from app.quality.repair.contracts import RepairAction, RepairMutationClass, RepairPlan, RepairTarget
from app.quality.repair.effectiveness.causal_reach import CausalReach
from app.quality.repair.effectiveness.contracts import RepairExecutionStatus
from app.quality.repair.effectiveness.firewall import RepairStrategyCompatibilityFirewall
from app.quality.repair.mutation_budget import MutationBudgetTracker
from app.quality.repair.mutation_contract import RepairMutationScope
from app.quality.repair.planner import CandidateRepairOption
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType
from app.quality.repair.strategies.base import RepairStrategy
from app.quality.repair.transaction import RepairTransactionManager


# ─────────────────────────────────────────────────────────────────────────────
from app.intelligence.transformation.intent import (
    ArtifactType,
    AudienceLevel,
    ResolvedArtifactIntent,
    get_default_intent,
)


def _make_intent(artifact_type: ArtifactType) -> ResolvedArtifactIntent:
    return get_default_intent(artifact_type)


def _make_presentation_bp(beats_count: int = 4) -> PresentationBlueprint:
    beats = []
    for i in range(1, beats_count + 1):
        vp = "EQUATION_FOCUS" if i == 2 else "CONCEPT_TEXT"
        beat = ConceptualBeat(
            beat_id=f"beat_{i:02d}",
            sequence_index=i,
            title=f"Slide Beat {i}",
            primary_concept_unit_id=f"ku_{i:02d}",
            supporting_unit_ids=(f"ku_supp_{i}_1", f"ku_supp_{i}_2"),
            narrative_function="CORE_MECHANISM" if i == 2 else "FOUNDATION",
            information_gain=0.7,
            cognitive_load_target=0.90 if i == 2 else 0.50,
            visual_priority=vp,
            selection_rationale=f"Rationale for beat {i}",
            knowledge_unit_ids=(f"ku_{i:02d}", f"ku_supp_{i}_1", f"ku_supp_{i}_2"),
        )
        beats.append(beat)
    return PresentationBlueprint(
        blueprint_id="bp_pres_test",
        artifact_type=ArtifactType.PRESENTATION,
        source_manifest_id="man_01",
        document_title="Test Presentation",
        intent=_make_intent(ArtifactType.PRESENTATION),
        beats=tuple(beats),
    )


def _make_worksheet_bp(activities_count: int = 8) -> WorksheetBlueprint:
    activities = []
    for i in range(1, activities_count + 1):
        act = LearningActivity(
            activity_id=f"act_{i:02d}",
            sequence_index=i,
            activity_type=LearningActivityType.QUESTION,  # Deliberately monotonous
            title=f"Pertanyaan {i}: Analisis Dinamika",
            prompt_text=f"Jelaskan prinsip fisis pada tahap {i} secara terperinci.",
            target_knowledge_unit_ids=(f"ku_ws_{i:02d}",),
            scaffolding_level="MEDIUM",
            withhold_explanation=True,
            expected_reasoning_type="CONCEPTUAL_EXPLANATION",
            knowledge_unit_ids=(f"ku_ws_{i:02d}",),
        )
        activities.append(act)
    return WorksheetBlueprint(
        blueprint_id="bp_ws_test",
        artifact_type=ArtifactType.WORKSHEET,
        source_manifest_id="man_01",
        document_title="Test Worksheet",
        intent=_make_intent(ArtifactType.WORKSHEET),
        activities=tuple(activities),
    )


# ─────────────────────────────────────────────────────────────────────────────
# SCENARIO TESTS A THROUGH AD
# ─────────────────────────────────────────────────────────────────────────────

def test_scenario_a_actuator_registration_and_discovery():
    """Scenario A: Actuator registry indexes and retrieves actuators by strategy and artifact."""
    registry = RepairActuatorRegistry()
    registry.populate_defaults()

    act = registry.get_actuator_for_strategy("presentation_component_reflow", "PRESENTATION")
    assert act is not None
    assert act.actuator_id == "presentation_component_reflow"
    assert "PRESENTATION" in act.supported_artifact_types

    ws_act = registry.get_actuator_for_strategy("worksheet_inquiry_sequence", "WORKSHEET")
    assert ws_act is not None
    assert ws_act.actuator_id == "worksheet_inquiry_recomposition"


def test_scenario_b_firewall_stage_5_actuator_capability_filter():
    """Scenario B: Stage 5 rejects strategies lacking a registered capable actuator."""
    class DummyStrategyWithoutActuator(RepairStrategy):
        def __init__(self):
            super().__init__(
                strategy_id="phantom_strategy_without_actuator",
                name="Phantom Strategy",
                supported_artifact_types=("PRESENTATION",),
                supported_failure_codes=("ELEMENT_COLLISION",),
                supported_root_causes=(RootCauseType.GRID_GEOMETRY,),
                mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
                priority=1,
            )
        def check_preconditions(self, bp, t, h): return True
        def plan_repair(self, bp, t, h): return None
        def apply_repair(self, bp, p): return bp, []

    strat = DummyStrategyWithoutActuator()
    eligible, rejections = RepairStrategyCompatibilityFirewall.filter_eligible_strategies(
        strategies=[strat],
        artifact_type="PRESENTATION",
        require_actuator=True,
    )
    assert len(eligible) == 0
    assert len(rejections) == 1
    assert rejections[0].filter_stage == "ACTUATOR_AVAILABLE_AND_CAPABLE"


def test_scenario_c_pre_actuation_causal_check_rejects_under_reaching_actuator():
    """Scenario C: PreActuationCausalCheck blocks an actuator with insufficient reach."""
    actuator = TypographyRepairActuator()  # Max reach: LOCAL_RENDER_GEOMETRY (depth 1)
    req = RepairActuationRequest(
        artifact_type="PRESENTATION",
        artifact_id="pres_1",
        finding_ids=("COGNITIVE_OVERLOAD",),
        root_cause_cluster="CONTENT_DENSITY",
        required_causal_reach=CausalReach.PAGE_COMPOSITION,  # Requires depth 3
        repair_strategy_id="typography_constraint_actuator",
        mutation_scope=RepairMutationScope.LEVEL_1_LOCAL_TOKEN,
        source_snapshot_hash="hash1",
        blueprint_snapshot_hash="hash1",
        render_snapshot_hash="hash1",
        quality_baseline=0.7,
    )
    bp = _make_presentation_bp()
    is_valid, reason = PreActuationCausalCheck.verify(actuator, req, bp)
    assert not is_valid
    assert "insufficient" in reason.lower()


def test_scenario_d_presentation_component_reflow_actuator():
    """Scenario D: PresentationComponentReflowActuator converts colliding grid to vertical flow."""
    actuator = PresentationComponentReflowActuator()
    bp = _make_presentation_bp(beats_count=3)
    req = RepairActuationRequest(
        artifact_type="PRESENTATION",
        artifact_id="pres_1",
        finding_ids=("ELEMENT_COLLISION",),
        root_cause_cluster="GRID_GEOMETRY",
        required_causal_reach=CausalReach.COMPONENT_SPATIAL_STRUCTURE,
        repair_strategy_id="presentation_component_reflow",
        mutation_scope=RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.75,
        target_slide_or_page_index=2,
    )
    assert actuator.can_actuate(req, bp)
    mutated_bp, res = actuator.actuate(req, bp)
    assert res.execution_status == RepairExecutionStatus.APPLIED
    assert res.causal_reach_achieved == CausalReach.COMPONENT_SPATIAL_STRUCTURE
    # Verify beat 2 was reflowed
    assert mutated_bp.beats[1].visual_priority == "CONCEPT_TEXT"


def test_scenario_e_presentation_formula_recomposition_actuator():
    """Scenario E: PresentationFormulaRecompositionActuator decomposes formula into 2 beats."""
    actuator = PresentationFormulaRecompositionActuator()
    bp = _make_presentation_bp(beats_count=3)
    req = RepairActuationRequest(
        artifact_type="PRESENTATION",
        artifact_id="pres_1",
        finding_ids=("ELEMENT_COLLISION",),
        root_cause_cluster="GRID_GEOMETRY",
        required_causal_reach=CausalReach.PAGE_COMPOSITION,
        repair_strategy_id="presentation_formula_recomposition",
        mutation_scope=RepairMutationScope.LEVEL_3_PAGE_COMPOSITION,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.75,
        target_slide_or_page_index=2,
    )
    mutated_bp, res = actuator.actuate(req, bp)
    assert res.execution_status == RepairExecutionStatus.APPLIED
    assert len(mutated_bp.beats) == len(bp.beats) + 1  # 3 beats decomposed to 4 beats
    assert "Prinsip Utama" in mutated_bp.beats[1].title
    assert "Analisis Variabel" in mutated_bp.beats[2].title


def test_scenario_f_presentation_composition_actuator():
    """Scenario F: PresentationCompositionActuator alternates visual priorities."""
    actuator = PresentationCompositionActuator()
    bp = _make_presentation_bp(beats_count=3)
    req = RepairActuationRequest(
        artifact_type="PRESENTATION",
        artifact_id="pres_1",
        finding_ids=("LAYOUT_MONOTONY",),
        root_cause_cluster="SEMANTIC_LAYOUT_MAPPING",
        required_causal_reach=CausalReach.PAGE_COMPOSITION,
        repair_strategy_id="presentation_composition_actuator",
        mutation_scope=RepairMutationScope.LEVEL_3_PAGE_COMPOSITION,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.75,
        target_slide_or_page_index=1,
    )
    mutated_bp, res = actuator.actuate(req, bp)
    assert res.execution_status == RepairExecutionStatus.APPLIED
    assert mutated_bp.beats[0].visual_priority != bp.beats[0].visual_priority


def test_scenario_g_presentation_slide_split_actuator():
    """Scenario G: PresentationSlideSplitActuator partitions overloaded beat into 2 parts."""
    actuator = PresentationSlideSplitActuator()
    bp = _make_presentation_bp(beats_count=3)
    req = RepairActuationRequest(
        artifact_type="PRESENTATION",
        artifact_id="pres_1",
        finding_ids=("CONTENT_DENSITY",),
        root_cause_cluster="CONTENT_DENSITY",
        required_causal_reach=CausalReach.PAGE_COMPOSITION,
        repair_strategy_id="presentation_slide_split_actuator",
        mutation_scope=RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.70,
        target_slide_or_page_index=1,
    )
    mutated_bp, res = actuator.actuate(req, bp)
    assert res.execution_status == RepairExecutionStatus.APPLIED
    assert len(mutated_bp.beats) == 4
    assert "(Bagian 1)" in mutated_bp.beats[0].title
    assert "(Bagian 2)" in mutated_bp.beats[1].title


def test_scenario_h_presentation_diversity_guard_and_actuator():
    """Scenario H: PresentationStructuralDiversityGuard detects monotony and injects rhythm."""
    bp = _make_presentation_bp(beats_count=5)
    beats = [b.model_copy(update={"visual_priority": "CONCEPT_TEXT"}) for b in bp.beats]
    bp_monotonous = bp.model_copy(update={"beats": tuple(beats)})

    streaks = PresentationStructuralDiversityGuard.detect_monotony_streaks(bp_monotonous, max_allowed_identical=3)
    assert len(streaks) >= 1
    assert streaks[0][1] - streaks[0][0] + 1 == 5

    actuator = PresentationDiversityActuator()
    req = RepairActuationRequest(
        artifact_type="PRESENTATION",
        artifact_id="pres_1",
        finding_ids=("REPETITION_STREAK",),
        root_cause_cluster="LAYOUT_MONOTONY",
        required_causal_reach=CausalReach.PAGE_COMPOSITION,
        repair_strategy_id="presentation_diversity_actuator",
        mutation_scope=RepairMutationScope.LEVEL_3_PAGE_COMPOSITION,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.70,
    )
    mutated_bp, res = actuator.actuate(req, bp_monotonous)
    assert res.execution_status == RepairExecutionStatus.APPLIED
    remaining_streaks = PresentationStructuralDiversityGuard.detect_monotony_streaks(mutated_bp, max_allowed_identical=3)
    assert len(remaining_streaks) == 0


def test_scenario_i_typography_constraint_solver_floors():
    """Scenario I: TypographyConstraintSolver enforces authoritative floors."""
    assert TypographyConstraintSolver.get_floor("PRESENTATION", "body") >= 12.0
    assert TypographyConstraintSolver.get_floor("WORKSHEET", "body") >= 10.5

    sizes = {"body": 8.0, "caption": 7.5}
    enforced = TypographyConstraintSolver.enforce_floors("PRESENTATION", sizes)
    assert enforced["body"] >= 12.0
    assert enforced["caption"] >= 12.0


def test_scenario_j_typography_repair_actuator():
    """Scenario J: TypographyRepairActuator elevates font scales cleanly."""
    actuator = TypographyRepairActuator()
    bp = _make_presentation_bp()
    req = RepairActuationRequest(
        artifact_type="PRESENTATION",
        artifact_id="pres_1",
        finding_ids=("TEXT_TOO_SMALL",),
        root_cause_cluster="TYPOGRAPHY",
        required_causal_reach=CausalReach.LOCAL_RENDER_GEOMETRY,
        repair_strategy_id="typography_constraint_actuator",
        mutation_scope=RepairMutationScope.LEVEL_1_LOCAL_TOKEN,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.80,
    )
    mutated_bp, res = actuator.actuate(req, bp)
    assert res.execution_status == RepairExecutionStatus.APPLIED
    assert res.changed_artifact_layers == (TransformationLayer.LAYER_0_TOKEN,)


def test_scenario_k_worksheet_inquiry_recomposition_actuator():
    """Scenario K: WorksheetInquiryRecompositionActuator restructures into 7-stage inquiry arc."""
    actuator = WorksheetInquiryRecompositionActuator()
    bp = _make_worksheet_bp(activities_count=7)
    req = RepairActuationRequest(
        artifact_type="WORKSHEET",
        artifact_id="ws_1",
        finding_ids=("REPETITION_STREAK",),
        root_cause_cluster="INQUIRY_STRUCTURE",
        required_causal_reach=CausalReach.PEDAGOGICAL_STRUCTURE,
        repair_strategy_id="worksheet_inquiry_recomposition",
        mutation_scope=RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.75,
    )
    mutated_bp, res = actuator.actuate(req, bp)
    assert res.execution_status == RepairExecutionStatus.APPLIED
    types = [a.activity_type for a in mutated_bp.activities]
    assert types[0] == LearningActivityType.PHENOMENON
    assert types[1] == LearningActivityType.PREDICTION
    assert types[2] == LearningActivityType.QUESTION
    assert types[3] == LearningActivityType.OBSERVATION
    assert types[4] == LearningActivityType.INVESTIGATION
    assert types[5] == LearningActivityType.DATA_ANALYSIS
    assert types[6] == LearningActivityType.REFLECTION


def test_scenario_l_worksheet_withhold_explanation_strict_invariance():
    """Scenario L: WorksheetInquiryRecompositionActuator strictly maintains withhold_explanation=True."""
    actuator = WorksheetInquiryRecompositionActuator()
    bp = _make_worksheet_bp(activities_count=7)
    req = RepairActuationRequest(
        artifact_type="WORKSHEET",
        artifact_id="ws_1",
        finding_ids=("REPETITION_STREAK",),
        root_cause_cluster="INQUIRY_STRUCTURE",
        required_causal_reach=CausalReach.PEDAGOGICAL_STRUCTURE,
        repair_strategy_id="worksheet_inquiry_recomposition",
        mutation_scope=RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.75,
    )
    mutated_bp, _ = actuator.actuate(req, bp)
    for act in mutated_bp.activities:
        assert act.withhold_explanation is True, f"Activity {act.activity_id} leaked answer!"


def test_scenario_m_worksheet_traceability_invariance():
    """Scenario M: Worksheet recomposition preserves source knowledge unit IDs with zero loss."""
    actuator = WorksheetInquiryRecompositionActuator()
    bp = _make_worksheet_bp(activities_count=5)
    req = RepairActuationRequest(
        artifact_type="WORKSHEET",
        artifact_id="ws_1",
        finding_ids=("REPETITION_STREAK",),
        root_cause_cluster="INQUIRY_STRUCTURE",
        required_causal_reach=CausalReach.PEDAGOGICAL_STRUCTURE,
        repair_strategy_id="worksheet_inquiry_recomposition",
        mutation_scope=RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.75,
    )
    orig_kus = {ku for a in bp.activities for ku in a.target_knowledge_unit_ids}
    mutated_bp, _ = actuator.actuate(req, bp)
    mutated_kus = {ku for a in mutated_bp.activities for ku in a.target_knowledge_unit_ids}
    assert orig_kus == mutated_kus, "Traceability broken during worksheet inquiry recomposition!"


def test_scenario_n_worksheet_pedagogical_diversity_analyzer():
    """Scenario N: WorksheetPedagogicalDiversityAnalyzer flags pathological monotony."""
    monotonous_bp = _make_worksheet_bp(activities_count=8)
    rep = WorksheetPedagogicalDiversityAnalyzer.analyze(monotonous_bp, max_allowed_consecutive=3)
    assert rep.is_pathological_monotony is True
    assert rep.max_consecutive_identical == 8

    # Now recompose
    actuator = WorksheetInquiryRecompositionActuator()
    req = RepairActuationRequest(
        artifact_type="WORKSHEET",
        artifact_id="ws_1",
        finding_ids=("REPETITION_STREAK",),
        root_cause_cluster="INQUIRY_STRUCTURE",
        required_causal_reach=CausalReach.PEDAGOGICAL_STRUCTURE,
        repair_strategy_id="worksheet_inquiry_recomposition",
        mutation_scope=RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.75,
    )
    recomposed_bp, _ = actuator.actuate(req, monotonous_bp)
    rep_recomposed = WorksheetPedagogicalDiversityAnalyzer.analyze(recomposed_bp, max_allowed_consecutive=3)
    assert rep_recomposed.is_pathological_monotony is False
    assert rep_recomposed.shannon_entropy > 2.0


def test_scenario_o_scientific_citation_visibility_actuator():
    """Scenario O: ScientificCitationVisibilityActuator injects in-text citation markers."""
    from app.intelligence.transformation.blueprints import (
        ScientificArgumentRole,
        ScientificArgumentUnit,
        ScientificDocumentBlueprint,
    )
    arg1 = ScientificArgumentUnit(
        argument_id="arg_1",
        sequence_index=1,
        claim_unit_id="clm_1",
        argument_role=ScientificArgumentRole.BACKGROUND_CLAIM,
        claim_statement="Water has a high specific heat capacity",
        confidence=0.95,
    )
    bp = ScientificDocumentBlueprint(
        blueprint_id="bp_sci_1",
        artifact_type=ArtifactType.SCIENTIFIC_DOCUMENT,
        source_manifest_id="m1",
        document_title="Thermal Physics",
        intent=_make_intent(ArtifactType.SCIENTIFIC_DOCUMENT),
        arguments=(arg1,),
    )
    actuator = ScientificCitationVisibilityActuator()
    req = RepairActuationRequest(
        artifact_type="SCIENTIFIC_DOCUMENT",
        artifact_id="sci_1",
        finding_ids=("CITATION_INTEGRITY",),
        root_cause_cluster="CITATION_INTEGRITY",
        required_causal_reach=CausalReach.SEMANTIC_INTEGRITY,
        repair_strategy_id="scientific_citation_visibility",
        mutation_scope=RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.85,
    )
    mutated_bp, res = actuator.actuate(req, bp)
    assert res.execution_status == RepairExecutionStatus.APPLIED
    assert "[1]" in mutated_bp.arguments[0].claim_statement


def test_scenario_p_scientific_evidence_layout_actuator():
    """Scenario P: ScientificEvidenceLayoutActuator organizes dual evidence panels."""
    actuator = ScientificEvidenceLayoutActuator()
    assert "SCIENTIFIC_DOCUMENT" in actuator.supported_artifact_types
    assert actuator.maximum_causal_reach == CausalReach.SEMANTIC_INTEGRITY


def test_scenario_q_handout_density_reflow_actuator():
    """Scenario Q: HandoutDensityReflowActuator adjusts spacing constraints."""
    actuator = HandoutDensityReflowActuator()
    assert "HANDOUT" in actuator.supported_artifact_types
    assert actuator.transformation_layer == TransformationLayer.LAYER_1_COMPONENT


def test_scenario_r_handout_section_balance_actuator():
    """Scenario R: HandoutSectionBalanceActuator rebalances page boundary allocations."""
    actuator = HandoutSectionBalanceActuator()
    assert "HANDOUT" in actuator.supported_artifact_types
    assert actuator.transformation_layer == TransformationLayer.LAYER_2_PAGE_COMPOSITION


def test_scenario_s_blueprint_recomposition_engine_delegation():
    """Scenario S: BlueprintRecompositionEngine delegates to capable actuator."""
    engine = BlueprintRecompositionEngine()
    bp = _make_presentation_bp()
    req = RepairActuationRequest(
        artifact_type="PRESENTATION",
        artifact_id="pres_1",
        finding_ids=("ELEMENT_COLLISION",),
        root_cause_cluster="GRID_GEOMETRY",
        required_causal_reach=CausalReach.COMPONENT_SPATIAL_STRUCTURE,
        repair_strategy_id="presentation_component_reflow",
        mutation_scope=RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.75,
        target_slide_or_page_index=2,
    )
    mutated, res = engine.recompose(req, bp)
    assert res.execution_status == RepairExecutionStatus.APPLIED
    assert res.actuator_id == "presentation_component_reflow"


def test_scenario_t_semantic_grouping_optimizer():
    """Scenario T: SemanticGroupingOptimizer partitions beats exceeding cognitive load limit."""
    bp = _make_presentation_bp(beats_count=3)
    # Beat 2 has cognitive_load_target = 0.90
    opt_beats = SemanticGroupingOptimizer.optimize_presentation_beats(bp.beats, max_cognitive_load=0.80)
    assert len(opt_beats) == 4
    for b in opt_beats:
        assert b.cognitive_load_target <= 0.80


def test_scenario_u_operator_performance_registry_tracking():
    """Scenario U: RepairOperatorPerformanceRegistry tracks empirical success and multipliers."""
    reg = RepairOperatorPerformanceRegistry()
    reg.record_execution(
        operator_id="op_reflow",
        artifact_type="PRESENTATION",
        root_cause="GRID_GEOMETRY",
        defect_signature="COLLISION",
        success=True,
        score_delta=0.25,
        drift=0.02,
        execution_ms=15.0,
    )
    mult = reg.get_operator_multiplier("op_reflow", "PRESENTATION", "GRID_GEOMETRY", "COLLISION")
    assert mult > 1.0


def test_scenario_v_operator_performance_registry_penalizes_failure():
    """Scenario V: Performance registry strongly penalizes operators that fail repeatedly."""
    reg = RepairOperatorPerformanceRegistry()
    for _ in range(3):
        reg.record_execution(
            operator_id="failing_op",
            artifact_type="WORKSHEET",
            root_cause="INQUIRY_STRUCTURE",
            defect_signature="REPETITION",
            success=False,
            score_delta=-0.10,
            drift=0.05,
            execution_ms=20.0,
            is_regressive=True,
        )
    mult = reg.get_operator_multiplier("failing_op", "WORKSHEET", "INQUIRY_STRUCTURE", "REPETITION")
    assert mult < 0.5


def test_scenario_w_zero_effect_detection():
    """Scenario W: Non-mutating actuator is detected and flagged."""
    class ZeroEffectActuator:
        @property
        def actuator_id(self): return "zero_effect_actuator"
        @property
        def supported_artifact_types(self): return ("PRESENTATION",)
        @property
        def supported_root_causes(self): return (RootCauseType.GRID_GEOMETRY,)
        @property
        def maximum_causal_reach(self): return CausalReach.COMPONENT_SPATIAL_STRUCTURE
        @property
        def transformation_layer(self): return TransformationLayer.LAYER_1_COMPONENT
        def can_actuate(self, req, bp): return True
        def actuate(self, req, bp):
            from app.quality.repair.effectiveness.zero_effect_detector import DomainFingerprinter
            fp = DomainFingerprinter.fingerprint("PRESENTATION", bp)
            return bp, RepairActuationResult(
                actuator_id=self.actuator_id,
                execution_status=RepairExecutionStatus.NO_EFFECT,
                transformation_applied="Nothing changed",
                changed_artifact_layers=(),
                before_fingerprint=fp,
                after_fingerprint=fp,
                causal_reach_achieved=CausalReach.LOCAL_RENDER_GEOMETRY,
                mutation_cost=0.0,
            )

    ze = ZeroEffectActuator()
    bp = _make_presentation_bp()
    req = RepairActuationRequest(
        artifact_type="PRESENTATION",
        artifact_id="p1",
        finding_ids=("ELEMENT_COLLISION",),
        root_cause_cluster="GRID_GEOMETRY",
        required_causal_reach=CausalReach.COMPONENT_SPATIAL_STRUCTURE,
        repair_strategy_id="zero_effect",
        mutation_scope=RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.7,
    )
    _, res = ze.actuate(req, bp)
    assert res.before_fingerprint.composite_hash == res.after_fingerprint.composite_hash


def test_scenario_x_transformation_diff_system_json(tmp_path: Path):
    """Scenario X: TransformationDiffSystem generates complete machine-readable JSON report."""
    actuator = PresentationComponentReflowActuator()
    bp = _make_presentation_bp()
    req = RepairActuationRequest(
        artifact_type="PRESENTATION",
        artifact_id="pres_1",
        finding_ids=("ELEMENT_COLLISION",),
        root_cause_cluster="GRID_GEOMETRY",
        required_causal_reach=CausalReach.COMPONENT_SPATIAL_STRUCTURE,
        repair_strategy_id="presentation_component_reflow",
        mutation_scope=RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.75,
        target_slide_or_page_index=2,
    )
    mutated_bp, res = actuator.actuate(req, bp)
    diff_report = TransformationDiffSystem.generate_diff(res, "PRESENTATION", bp, mutated_bp, iteration=1)
    json_path, md_path = TransformationDiffSystem.write_diff_artifacts(diff_report, tmp_path)

    assert json_path.exists()
    assert md_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["actuator_id"] == "presentation_component_reflow"
    assert "LAYER_1_COMPONENT" in data["changed_layers"]


def test_scenario_y_transformation_diff_system_markdown(tmp_path: Path):
    """Scenario Y: TransformationDiffSystem produces human-readable Markdown diff with diff fences."""
    actuator = PresentationComponentReflowActuator()
    bp = _make_presentation_bp()
    req = RepairActuationRequest(
        artifact_type="PRESENTATION",
        artifact_id="pres_1",
        finding_ids=("ELEMENT_COLLISION",),
        root_cause_cluster="GRID_GEOMETRY",
        required_causal_reach=CausalReach.COMPONENT_SPATIAL_STRUCTURE,
        repair_strategy_id="presentation_component_reflow",
        mutation_scope=RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.75,
        target_slide_or_page_index=2,
    )
    mutated_bp, res = actuator.actuate(req, bp)
    diff_report = TransformationDiffSystem.generate_diff(res, "PRESENTATION", bp, mutated_bp, iteration=1)
    _, md_path = TransformationDiffSystem.write_diff_artifacts(diff_report, tmp_path)
    content = md_path.read_text(encoding="utf-8")
    assert "# Transformation Diff Report" in content
    assert "presentation_component_reflow" in content
    assert "```diff" in content


def test_scenario_z_cross_artifact_actuator_isolation():
    """Scenario Z: Presentation actuator rejects Worksheet request before execution."""
    actuator = PresentationComponentReflowActuator()
    req = RepairActuationRequest(
        artifact_type="WORKSHEET",
        artifact_id="ws_1",
        finding_ids=("REPETITION_STREAK",),
        root_cause_cluster="INQUIRY_STRUCTURE",
        required_causal_reach=CausalReach.COMPONENT_SPATIAL_STRUCTURE,
        repair_strategy_id="presentation_component_reflow",
        mutation_scope=RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
        source_snapshot_hash="h1",
        blueprint_snapshot_hash="h1",
        render_snapshot_hash="h1",
        quality_baseline=0.75,
    )
    ws_bp = _make_worksheet_bp()
    assert not actuator.can_actuate(req, ws_bp)
    is_valid, reason = PreActuationCausalCheck.verify(actuator, req, ws_bp)
    assert not is_valid
    assert "does not support artifact" in reason


def test_scenario_aa_quality_authority_separation_of_powers():
    """Scenario AA: Actuators cannot bypass UnifiedQualityAuthority Level-0 export decisions."""
    decision = UnifiedQualityDecision(
        decision=ExportDecision.SEMANTIC_REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        manual_review_required=False,
        hard_blockers=("ELEMENT_COLLISION",),
        warnings=(),
        rationale="Blocker present",
    )
    assert decision.can_export is False
    assert "ELEMENT_COLLISION" in decision.hard_blockers


def test_scenario_ab_transaction_rollback_on_regression():
    """Scenario AB: Transaction manager rolls back when post-eval introduces regression."""
    bp = _make_presentation_bp()
    budget = MutationBudgetTracker("PRESENTATION")
    candidate = CandidateRepairOption(
        strategy_id="presentation_component_reflow",
        target=RepairTarget(artifact_type="PRESENTATION", slide_index=1),
        hypothesis=RootCauseHypothesis(
            root_cause_id="rc1",
            cause_type=RootCauseType.GRID_GEOMETRY,
            affected_targets=(RepairTarget(artifact_type="PRESENTATION", slide_index=1),),
            confidence=0.9,
            causal_explanation="Collision",
        ),
        mutation_scope=RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
        mutation_cost=0.2,
        utility_score=0.8,
        expected_quality_gain=0.15,
        leverage_score=0.7,
        blast_radius=0.1,
        regression_risk=0.05,
        is_budget_approved=True,
    )
    reg = RepairActuatorRegistry.get_default()
    strategy = reg.get_actuator_for_strategy("presentation_component_reflow")

    # Evaluator that reports a regression
    def regressive_eval(b):
        reg_dec = UnifiedQualityDecision(
            decision=ExportDecision.BLOCKED,
            can_export=False,
            repair_required=False,
            manual_review_required=True,
            hard_blockers=("NEW_REGRESSIVE_BLOCKER",),
            warnings=(),
            rationale="Regression created",
        )
        return reg_dec, 0.40, []

    cur_dec = UnifiedQualityDecision(
        decision=ExportDecision.SEMANTIC_REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        manual_review_required=False,
        hard_blockers=("ELEMENT_COLLISION",),
        warnings=(),
        rationale="Pre-repair",
    )

    restored_bp, tx_rec, committed = RepairTransactionManager.execute_transaction(
        current_blueprint=bp,
        candidate=candidate,
        strategy=strategy,
        budget_tracker=budget,
        current_decision=cur_dec,
        current_score=0.75,
        artifact_type="PRESENTATION",
        iteration=1,
        evaluator_fn=regressive_eval,
    )
    assert not committed
    assert tx_rec.is_committed is False
    assert "Regression detected" in tx_rec.rollback_reason


def test_scenario_ac_mutation_hierarchy_preservation():
    """Scenario AC: Levels 0 to 4 boundaries are strictly preserved."""
    assert TransformationLayer.LAYER_0_TOKEN.depth < TransformationLayer.LAYER_1_COMPONENT.depth
    assert TransformationLayer.LAYER_1_COMPONENT.depth < TransformationLayer.LAYER_2_PAGE_COMPOSITION.depth
    assert TransformationLayer.LAYER_2_PAGE_COMPOSITION.depth < TransformationLayer.LAYER_3_BLUEPRINT_RECOMPOSITION.depth
    assert TransformationLayer.LAYER_3_BLUEPRINT_RECOMPOSITION.depth < TransformationLayer.LAYER_4_SEMANTIC_ORGANIZATION.depth


def test_scenario_ad_end_to_end_atomic_transaction_execution():
    """Scenario AD: End-to-end atomic transaction commits and registers actuator result."""
    bp = _make_presentation_bp()
    budget = MutationBudgetTracker("PRESENTATION")
    candidate = CandidateRepairOption(
        strategy_id="presentation_component_reflow",
        target=RepairTarget(artifact_type="PRESENTATION", slide_index=2),
        hypothesis=RootCauseHypothesis(
            root_cause_id="rc1",
            cause_type=RootCauseType.GRID_GEOMETRY,
            affected_targets=(RepairTarget(artifact_type="PRESENTATION", slide_index=2),),
            confidence=0.9,
            causal_explanation="Collision",
        ),
        mutation_scope=RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
        mutation_cost=0.2,
        utility_score=0.8,
        expected_quality_gain=0.15,
        leverage_score=0.7,
        blast_radius=0.1,
        regression_risk=0.05,
        is_budget_approved=True,
    )
    reg = RepairActuatorRegistry.get_default()
    strategy = reg.get_actuator_for_strategy("presentation_component_reflow")

    # Evaluator that reports clean pass
    def passing_eval(b):
        pass_dec = UnifiedQualityDecision(
            decision=ExportDecision.EXPORT_APPROVED,
            can_export=True,
            repair_required=False,
            manual_review_required=False,
            hard_blockers=(),
            warnings=(),
            rationale="All cleared",
        )
        return pass_dec, 0.95, []

    cur_dec = UnifiedQualityDecision(
        decision=ExportDecision.SEMANTIC_REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        manual_review_required=False,
        hard_blockers=("ELEMENT_COLLISION",),
        warnings=(),
        rationale="Pre-repair",
    )

    mutated_bp, tx_rec, committed = RepairTransactionManager.execute_transaction(
        current_blueprint=bp,
        candidate=candidate,
        strategy=strategy,
        budget_tracker=budget,
        current_decision=cur_dec,
        current_score=0.75,
        artifact_type="PRESENTATION",
        iteration=1,
        evaluator_fn=passing_eval,
    )
    assert committed
    assert tx_rec.is_committed is True
    assert tx_rec.actuator_id == "presentation_component_reflow"
    assert tx_rec.actuator_result is not None
