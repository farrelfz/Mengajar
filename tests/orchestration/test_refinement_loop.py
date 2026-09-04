"""
Unit tests for bounded Refinement Loop Controller and stagnation protection.
"""

import pytest
from app.orchestration.refinement_loop import RefinementLoopController


def test_refinement_loop_terminates_on_stagnation():
    ctrl = RefinementLoopController(max_iterations=5, minimum_improvement=0.02, stagnation_limit=2)

    # Iteration 1: 0.60
    dec1 = ctrl.evaluate_next_iteration(0.60, 1)
    assert dec1.should_continue is True

    # Iteration 2: 0.61 (delta = 0.01 < 0.02 -> stagnation 1)
    dec2 = ctrl.evaluate_next_iteration(0.61, 2)
    assert dec2.should_continue is True
    assert dec2.stagnation_count == 1

    # Iteration 3: 0.61 (delta = 0.00 < 0.02 -> stagnation 2 -> terminate)
    dec3 = ctrl.evaluate_next_iteration(0.61, 3)
    assert dec3.should_continue is False
    assert "stagnated" in dec3.reason


def test_refinement_loop_terminates_on_max_iterations():
    ctrl = RefinementLoopController(max_iterations=3)
    dec = ctrl.evaluate_next_iteration(0.80, 3)
    assert dec.should_continue is False
    assert "maximum refinement iteration limit" in dec.reason
