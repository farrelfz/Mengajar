"""
Unit tests for Convergence and Oscillation Detection.
"""

import pytest
from app.refinement.contracts import ImprovementDecision
from app.refinement.convergence import ConvergenceDetector


def test_detector_identifies_oscillation_state():
    history_fps = ["fp_state_a", "fp_state_b"]
    current_fp = "fp_state_a"  # Cycled back to state A

    decision = ConvergenceDetector.check_convergence(
        history_fingerprints=history_fps,
        history_scores=[0.80, 0.82],
        current_fingerprint=current_fp,
        current_score=0.80,
    )

    assert decision == ImprovementDecision.STOP_OSCILLATION


def test_detector_identifies_convergence_plateau():
    history_fps = ["fp_1", "fp_2"]
    history_scores = [0.880, 0.882]  # deltas < 0.005

    decision = ConvergenceDetector.check_convergence(
        history_fingerprints=history_fps,
        history_scores=history_scores,
        current_fingerprint="fp_3",
        current_score=0.883,
    )

    assert decision == ImprovementDecision.STOP_CONVERGED
