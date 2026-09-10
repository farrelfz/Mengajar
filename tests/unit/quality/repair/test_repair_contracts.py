"""
Unit tests for canonical repair contracts, mutation classes, risk tiers, and serializability.
"""

import json
import pytest
from app.quality.contracts.decisions import ExportDecision, UnifiedQualityDecision
from app.quality.contracts.findings import QualityFinding, SignalSeverity
from app.quality.repair.contracts import (
    ConvergenceState,
    RepairAction,
    RepairHistoryEntry,
    RepairMutationClass,
    RepairPlan,
    RepairRequest,
    RepairResult,
    RepairRiskLevel,
    RepairTarget,
)


def test_repair_mutation_classes():
    assert RepairMutationClass.CLASS_A_GEOMETRY == "CLASS_A_GEOMETRY"
    assert RepairMutationClass.CLASS_B_COMPOSITION == "CLASS_B_COMPOSITION"
    assert RepairMutationClass.CLASS_C_LAYOUT_REMAPPING == "CLASS_C_LAYOUT_REMAPPING"
    assert RepairMutationClass.CLASS_D_PEDAGOGICAL_STRUCTURE == "CLASS_D_PEDAGOGICAL_STRUCTURE"
    assert RepairMutationClass.CLASS_E_SEMANTIC_INTEGRITY == "CLASS_E_SEMANTIC_INTEGRITY"
    assert RepairMutationClass.CLASS_F_NON_REPAIRABLE == "CLASS_F_NON_REPAIRABLE"


def test_repair_target_immutability():
    target = RepairTarget(
        artifact_type="PRESENTATION",
        slide_index=3,
        source_knowledge_ids=("ku_1", "ku_2"),
    )
    assert target.artifact_type == "PRESENTATION"
    assert target.slide_index == 3
    assert "ku_1" in target.source_knowledge_ids

    with pytest.raises(Exception):
        target.slide_index = 4  # Frozen


def test_repair_action_and_plan_serializability():
    target = RepairTarget(artifact_type="HANDOUT", page_index=2)
    action = RepairAction(
        strategy_id="handout_density_balance",
        target=target,
        mutation_type="split_dense_explanatory_section",
        mutation_class=RepairMutationClass.CLASS_B_COMPOSITION,
        before_state_hash="hash123",
        rationale="Density relief",
        expected_effect="Better reading flow",
        risk_level=RepairRiskLevel.MEDIUM,
    )
    plan = RepairPlan(
        root_cause_id="rc_test",
        artifact_type="HANDOUT",
        actions=(action,),
        execution_order=(action.action_id,),
        expected_quality_improvement=0.20,
    )

    data = plan.model_dump()
    json_str = json.dumps(data)
    assert "handout_density_balance" in json_str
    assert "CLASS_B_COMPOSITION" in json_str


def test_repair_result_and_history():
    dec_before = UnifiedQualityDecision(
        decision=ExportDecision.RENDER_REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        rationale="Render overflow",
    )
    dec_after = UnifiedQualityDecision(
        decision=ExportDecision.EXPORT_APPROVED,
        can_export=True,
        repair_required=False,
        rationale="Resolved",
    )
    result = RepairResult(
        plan_id="plan_1",
        success=True,
        pre_authority=dec_before,
        post_authority=dec_after,
        convergence_state=ConvergenceState.CONVERGED,
    )
    assert result.success is True
    assert result.convergence_state == ConvergenceState.CONVERGED

    entry = RepairHistoryEntry(
        iteration=1,
        authority_decision_before=dec_before.decision.value,
        findings_before=("TEXT_OVERFLOW",),
        root_cause="CONTENT_DENSITY",
        repair_plan_id="plan_1",
        mutations=("split_overloaded_slide",),
        authority_decision_after=dec_after.decision.value,
        score_delta=0.15,
        regressions=(),
    )
    entry_json = entry.model_dump_json()
    assert "split_overloaded_slide" in entry_json
