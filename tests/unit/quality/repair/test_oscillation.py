"""
Unit tests for oscillation detection (state repeat, strategy alternation, score stagnation).
"""

from app.quality.repair.convergence import RepairOscillationDetector


def test_oscillation_state_repeat():
    detector = RepairOscillationDetector()
    detector.record_step(state_hash="state_alpha", strategy_id="strat_1", score=0.70)
    assert detector.check_oscillation().is_oscillating is False

    detector.record_step(state_hash="state_beta", strategy_id="strat_2", score=0.72)
    assert detector.check_oscillation().is_oscillating is False

    # Return to state_alpha -> loop!
    detector.record_step(state_hash="state_alpha", strategy_id="strat_1", score=0.70)
    res = detector.check_oscillation()
    assert res.is_oscillating is True
    assert res.cycle_type == "STATE_REPEAT"
    assert res.cycle_length == 2


def test_oscillation_strategy_alternation():
    detector = RepairOscillationDetector()
    detector.record_step(state_hash="hash_1", strategy_id="strategy_a", score=0.70)
    detector.record_step(state_hash="hash_2", strategy_id="strategy_b", score=0.71)
    # Alternating back to strategy_a
    detector.record_step(state_hash="hash_3", strategy_id="strategy_a", score=0.72)

    res = detector.check_oscillation()
    assert res.is_oscillating is True
    assert res.cycle_type == "STRATEGY_ALTERNATION"


def test_oscillation_stagnation():
    detector = RepairOscillationDetector()
    detector.record_step(state_hash="h1", strategy_id="strat_1", score=0.750)
    detector.record_step(state_hash="h2", strategy_id="strat_2", score=0.750)
    detector.record_step(state_hash="h3", strategy_id="strat_3", score=0.750)

    res = detector.check_oscillation()
    assert res.is_oscillating is True
    assert res.cycle_type == "STAGNATION"
