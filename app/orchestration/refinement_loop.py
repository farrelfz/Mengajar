"""
Refinement Loop Controller: Bounded iterative improvement with stagnation limits and convergence guarantees.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel
from app.orchestration.contracts import ProductionJobContext


class LoopControlDecision(BaseModel):
    should_continue: bool
    reason: str
    stagnation_count: int
    iteration_count: int


class RefinementLoopController:
    """Controls closed-loop iterative refinement without uncontrolled execution cycles."""

    def __init__(
        self,
        max_iterations: int = 3,
        minimum_improvement: float = 0.02,
        stagnation_limit: int = 2,
    ) -> None:
        self.max_iterations = max_iterations
        self.minimum_improvement = minimum_improvement
        self.stagnation_limit = stagnation_limit
        self.score_history: list[float] = []
        self.stagnation_count: int = 0

    def evaluate_next_iteration(self, current_score: float, iteration: int) -> LoopControlDecision:
        self.score_history.append(current_score)

        if iteration >= self.max_iterations:
            return LoopControlDecision(
                should_continue=False,
                reason=f"Reached maximum refinement iteration limit ({self.max_iterations}).",
                stagnation_count=self.stagnation_count,
                iteration_count=iteration,
            )

        if len(self.score_history) >= 2:
            prev_score = self.score_history[-2]
            delta = current_score - prev_score
            if delta < self.minimum_improvement:
                self.stagnation_count += 1
            else:
                self.stagnation_count = 0

            if self.stagnation_count >= self.stagnation_limit:
                return LoopControlDecision(
                    should_continue=False,
                    reason=f"Terminating refinement: improvement stagnated for {self.stagnation_count} iterations (delta < {self.minimum_improvement}).",
                    stagnation_count=self.stagnation_count,
                    iteration_count=iteration,
                )

        return LoopControlDecision(
            should_continue=True,
            reason=f"Proceeding with refinement iteration {iteration + 1}.",
            stagnation_count=self.stagnation_count,
            iteration_count=iteration,
        )
