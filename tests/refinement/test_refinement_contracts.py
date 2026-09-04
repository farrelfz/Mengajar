"""
Unit tests for Refinement domain contracts and serialization.
"""

import pytest
from app.refinement.contracts import (
    ImprovementDecision,
    InvariantCategory,
    RefinementAction,
    RefinementIntent,
    RefinementPlan,
    RefinementRisk,
    RefinementScope,
    RefinementStage,
    RefinementTargetLayer,
)


def test_refinement_enums_and_constants():
    assert RefinementStage.PLANNING == "planning"
    assert RefinementTargetLayer.DIRECTOR == "director"
    assert RefinementScope.PAGE == "page"
    assert RefinementIntent.REORDER == "reorder"
    assert RefinementRisk.LOW == "low"
    assert ImprovementDecision.ACCEPT == "accept"
    assert InvariantCategory.SEMANTIC_INVARIANT == "semantic_invariant"


def test_refinement_plan_serialization():
    action = RefinementAction(
        action_id="act_01",
        source_finding_ids=["find_01"],
        target_layer=RefinementTargetLayer.DIRECTOR,
        target_scope=RefinementScope.SECTION,
        target_identifier="stage_1",
        intent=RefinementIntent.REORDER,
        rationale="Reorder stages so concepts precede practice.",
        expected_benefit="Proper scaffolding.",
        estimated_risk=RefinementRisk.LOW,
    )
    plan = RefinementPlan(
        plan_id="plan_test_01",
        source_artifact_id="art_01",
        iteration=1,
        actions=[action],
        invariants=["learning_objectives_preserved"],
        expected_improvement="Better pedagogy.",
    )

    data = plan.model_dump()
    assert data["plan_id"] == "plan_test_01"
    assert len(data["actions"]) == 1
    assert data["actions"][0]["intent"] == "reorder"
