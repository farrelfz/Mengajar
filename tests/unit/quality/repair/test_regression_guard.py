"""
Unit tests for the Regression Guard, rollback triggers, and invariant enforcement.
"""

from app.intelligence.transformation.blueprints import (
    HandoutBlueprint,
    LearningActivity,
    LearningActivityType,
    WorksheetBlueprint,
)
from app.intelligence.transformation.intent import ArtifactType, get_default_intent
from app.quality.contracts.decisions import ExportDecision, UnifiedQualityDecision
from app.quality.repair.regression_guard import RegressionGuard


def test_regression_guard_clean_pass():
    pre_dec = UnifiedQualityDecision(
        decision=ExportDecision.RENDER_REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        hard_blockers=(),
        rationale="Overflow",
    )
    post_dec = UnifiedQualityDecision(
        decision=ExportDecision.EXPORT_APPROVED,
        can_export=True,
        repair_required=False,
        hard_blockers=(),
        rationale="Clean",
    )

    res = RegressionGuard.evaluate(
        pre_decision=pre_dec,
        post_decision=post_dec,
        pre_blueprint={},
        post_blueprint={},
        pre_score=0.70,
        post_score=0.88,
    )
    assert res.passed is True
    assert res.should_rollback is False
    assert res.score_delta == 0.18


def test_regression_guard_new_hard_blocker_triggers_rollback():
    pre_dec = UnifiedQualityDecision(
        decision=ExportDecision.RENDER_REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        hard_blockers=("TEXT_OVERFLOW: Clipped on slide 1",),
        rationale="Overflow",
    )
    # Post-repair resolved text overflow but created FONT_TOO_SMALL hard blocker!
    post_dec = UnifiedQualityDecision(
        decision=ExportDecision.BLOCKED,
        can_export=False,
        repair_required=True,
        hard_blockers=("FONT_TOO_SMALL: Font shrunk to 8pt",),
        rationale="Tiny text",
    )

    res = RegressionGuard.evaluate(
        pre_decision=pre_dec,
        post_decision=post_dec,
        pre_blueprint={},
        post_blueprint={},
        pre_score=0.70,
        post_score=0.72,
    )
    assert res.passed is False
    assert res.should_rollback is True
    assert "FONT_TOO_SMALL" in res.hard_blockers_introduced


def test_regression_guard_traceability_break_triggers_rollback():
    pre_dec = UnifiedQualityDecision(decision=ExportDecision.REPAIR_REQUIRED, can_export=False, repair_required=True, rationale="")
    post_dec = UnifiedQualityDecision(decision=ExportDecision.EXPORT_APPROVED, can_export=True, repair_required=False, rationale="")

    class MockBP:
        def __init__(self, refs):
            self.selected_knowledge_unit_ids = tuple(refs)

    pre_bp = MockBP(["ku_1", "ku_2", "ku_3"])
    post_bp = MockBP(["ku_1"])  # ku_2 and ku_3 lost!

    res = RegressionGuard.evaluate(
        pre_decision=pre_dec,
        post_decision=post_dec,
        pre_blueprint=pre_bp,
        post_blueprint=post_bp,
        pre_score=0.70,
        post_score=0.85,
    )
    assert res.passed is False
    assert res.should_rollback is True
    assert res.traceability_broken is True


def test_regression_guard_worksheet_invariant():
    pre_dec = UnifiedQualityDecision(decision=ExportDecision.REPAIR_REQUIRED, can_export=False, repair_required=True, rationale="")
    post_dec = UnifiedQualityDecision(decision=ExportDecision.EXPORT_APPROVED, can_export=True, repair_required=False, rationale="")

    # Post blueprint violates anti-spoiling
    act = LearningActivity(
        activity_id="a1", sequence_index=1, activity_type=LearningActivityType.PREDICTION,
        title="Predict", prompt_text="Prompt", scaffolding_level="MEDIUM",
        withhold_explanation=False, expected_reasoning_type="PRED"
    )
    post_bp = WorksheetBlueprint(
        blueprint_id="bp", artifact_type=ArtifactType.WORKSHEET,
        source_manifest_id="sm", document_title="LKS",
        intent=get_default_intent(ArtifactType.WORKSHEET), activities=(act,)
    )

    res = RegressionGuard.evaluate(
        pre_decision=pre_dec,
        post_decision=post_dec,
        pre_blueprint={},
        post_blueprint=post_bp,
        pre_score=0.70,
        post_score=0.80,
    )
    assert res.passed is False
    assert res.should_rollback is True
    assert any("anti-spoiling invariant" in r for r in res.failure_reasons)
