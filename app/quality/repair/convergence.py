"""
Universal Document Intelligence System V5 — Convergence Controller & Oscillation Detection.

Phase 3B: Enforces bounded repair iteration loops, detects state oscillation cycles,
and safely routes stagnating or diverging repairs to MANUAL_REVIEW_REQUIRED.
"""

from __future__ import annotations

from typing import List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.decisions import UnifiedQualityDecision
from app.quality.repair.contracts import ConvergenceState


class OscillationDetectionResult(BaseModel):
    """Outcome of checking for repair loop cycles or stagnation."""
    model_config = ConfigDict(frozen=True)

    is_oscillating: bool
    cycle_type: Optional[str] = None  # "STATE_REPEAT", "STRATEGY_ALTERNATION", "STAGNATION"
    cycle_length: int = 0
    rationale: str = ""


class RepairOscillationDetector:
    """Detects cyclical repair loops, alternating mutations, or zero-progress stagnation."""

    def __init__(self) -> None:
        self.state_hashes: List[str] = []
        self.strategy_sequence: List[str] = []
        self.score_history: List[float] = []

    def record_step(self, state_hash: str, strategy_id: str, score: float) -> None:
        self.state_hashes.append(state_hash)
        self.strategy_sequence.append(strategy_id)
        self.score_history.append(score)

    def check_oscillation(self) -> OscillationDetectionResult:
        n = len(self.state_hashes)
        if n < 2:
            return OscillationDetectionResult(is_oscillating=False)

        current_hash = self.state_hashes[-1]

        # 1. State Repeat Detection: Have we returned to an exact prior composition?
        if current_hash in self.state_hashes[:-1]:
            prior_idx = self.state_hashes[:-1].index(current_hash)
            cycle_len = (n - 1) - prior_idx
            return OscillationDetectionResult(
                is_oscillating=True,
                cycle_type="STATE_REPEAT",
                cycle_length=cycle_len,
                rationale=f"State hash {current_hash} recurred after {cycle_len} iterations (infinite repair loop detected).",
            )

        # 2. Strategy Alternation Detection: e.g. A -> B -> A
        if n >= 3:
            if self.strategy_sequence[-1] == self.strategy_sequence[-3] and self.strategy_sequence[-1] != self.strategy_sequence[-2]:
                return OscillationDetectionResult(
                    is_oscillating=True,
                    cycle_type="STRATEGY_ALTERNATION",
                    cycle_length=2,
                    rationale=f"Alternating strategy loop detected: {self.strategy_sequence[-2]} <-> {self.strategy_sequence[-1]}; terminating mutation flip-flop.",
                )

        # 3. Score Stagnation Detection: 2 steps with zero score delta and same decision
        if n >= 3:
            if abs(self.score_history[-1] - self.score_history[-2]) < 0.001 and abs(self.score_history[-2] - self.score_history[-3]) < 0.001:
                return OscillationDetectionResult(
                    is_oscillating=True,
                    cycle_type="STAGNATION",
                    cycle_length=2,
                    rationale="Quality score stagnated across 2 consecutive repair iterations without progression.",
                )

        return OscillationDetectionResult(is_oscillating=False)


class ConvergenceController:
    """Oversees convergence progress across iterations against a bounded repair budget."""

    def __init__(self, max_iterations: int = 3) -> None:
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.oscillation_detector = RepairOscillationDetector()

    def can_continue(self) -> bool:
        return self.current_iteration < self.max_iterations

    def advance_iteration(self) -> int:
        self.current_iteration += 1
        return self.current_iteration

    def evaluate_state(
        self,
        decision: UnifiedQualityDecision,
        state_hash: str,
        strategy_id: str,
        score: float,
    ) -> Tuple[ConvergenceState, OscillationDetectionResult]:
        self.oscillation_detector.record_step(state_hash, strategy_id, score)
        osc = self.oscillation_detector.check_oscillation()

        if osc.is_oscillating:
            return ConvergenceState.OSCILLATION_DETECTED, osc

        if decision.can_export:
            return ConvergenceState.CONVERGED, osc

        if not self.can_continue():
            return ConvergenceState.BUDGET_EXHAUSTED, osc

        return ConvergenceState.IN_PROGRESS, osc
