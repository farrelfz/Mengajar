"""
Unit tests for the Convergence Controller and iteration budget enforcement.
"""

from app.quality.contracts.decisions import ExportDecision, UnifiedQualityDecision
from app.quality.repair.contracts import ConvergenceState
from app.quality.repair.convergence import ConvergenceController


def test_convergence_on_export_approval():
    controller = ConvergenceController(max_iterations=3)
    dec = UnifiedQualityDecision(
        decision=ExportDecision.EXPORT_APPROVED,
        can_export=True,
        repair_required=False,
        rationale="Approved",
    )

    state, osc = controller.evaluate_state(
        decision=dec,
        state_hash="hash_1",
        strategy_id="strat_1",
        score=0.90,
    )
    assert state == ConvergenceState.CONVERGED
    assert osc.is_oscillating is False


def test_budget_exhaustion_enforcement():
    controller = ConvergenceController(max_iterations=2)
    dec_repair = UnifiedQualityDecision(
        decision=ExportDecision.REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        rationale="Needs repair",
    )

    controller.advance_iteration()
    state1, _ = controller.evaluate_state(dec_repair, "hash_1", "strat_1", 0.70)
    assert state1 == ConvergenceState.IN_PROGRESS

    controller.advance_iteration()
    state2, _ = controller.evaluate_state(dec_repair, "hash_2", "strat_2", 0.75)
    # Budget of 2 reached without export approval -> BUDGET_EXHAUSTED!
    assert state2 == ConvergenceState.BUDGET_EXHAUSTED
