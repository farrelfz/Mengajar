"""
Universal Document Intelligence System V5 — Production Convergence Controller.

Phase 3D: Real-time tracking of repair cycles, score trajectories, repeated state hashes,
and state oscillation patterns to guarantee deterministic termination of repair loops.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from app.quality.contracts.authority import UnifiedQualityReport
from app.quality.contracts.decisions import ExportDecision, UnifiedQualityDecision


class StagnationReason(str, Enum):
    """Categorical forensic reason for repair loop stagnation."""
    NO_QUALITY_GAIN = "NO_QUALITY_GAIN"
    NO_FINDING_REDUCTION = "NO_FINDING_REDUCTION"
    ROOT_CAUSE_PERSISTENT = "ROOT_CAUSE_PERSISTENT"
    ZERO_EFFECT_MUTATION = "ZERO_EFFECT_MUTATION"
    STRATEGY_LOOP = "STRATEGY_LOOP"
    INSUFFICIENT_CAUSAL_REACH = "INSUFFICIENT_CAUSAL_REACH"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"


class ProductionConvergenceOutcome(str, Enum):
    """Authoritative outcome of checking convergence status in production."""
    CONVERGED_APPROVED = "CONVERGED_APPROVED"
    CONVERGED_WITH_WARNINGS = "CONVERGED_WITH_WARNINGS"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    OSCILLATION_DETECTED = "OSCILLATION_DETECTED"
    NO_POSITIVE_PROGRESS = "NO_POSITIVE_PROGRESS"
    FALSE_PROGRESS = "FALSE_PROGRESS"
    REPAIR_SCOPE_EXHAUSTED = "REPAIR_SCOPE_EXHAUSTED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    CONTINUE_REPAIR = "CONTINUE_REPAIR"


@dataclass(frozen=True)
class ConvergenceCheckResult:
    """Outcome report evaluating whether to continue or terminate the repair loop."""
    outcome: ProductionConvergenceOutcome
    should_terminate: bool
    can_export: bool
    iteration: int
    cycle_detected: bool = False
    stagnation_reason: Optional[StagnationReason] = None
    rationale: str = ""


class ProductionConvergenceController:
    """Prevents infinite loops and ensures safe termination of closed-loop repairs."""

    def __init__(self, max_iterations: int = 3) -> None:
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.score_history: List[float] = []
        self.state_hashes: List[str] = []
        self.decisions: List[ExportDecision] = []
        self.hard_blocker_history: List[Tuple[str, ...]] = []

    def advance_iteration(self) -> int:
        self.current_iteration += 1
        return self.current_iteration

    def evaluate(
        self,
        report: UnifiedQualityReport,
        state_hash: str,
    ) -> ConvergenceCheckResult:
        """Evaluates convergence against quality decision, hash history, and score trajectory."""
        self.score_history.append(report.overall_quality_score)
        self.state_hashes.append(state_hash)
        self.decisions.append(report.decision)
        self.hard_blocker_history.append(tuple(report.hard_blockers))

        n = len(self.state_hashes)

        # 1. Direct Approval Convergence
        if report.decision == ExportDecision.EXPORT_APPROVED:
            return ConvergenceCheckResult(
                outcome=ProductionConvergenceOutcome.CONVERGED_APPROVED,
                should_terminate=True,
                can_export=True,
                iteration=self.current_iteration,
                rationale="Artifact successfully converged to EXPORT_APPROVED.",
            )

        if report.decision == ExportDecision.EXPORT_APPROVED_WITH_WARNINGS:
            return ConvergenceCheckResult(
                outcome=ProductionConvergenceOutcome.CONVERGED_WITH_WARNINGS,
                should_terminate=True,
                can_export=True,
                iteration=self.current_iteration,
                rationale="Artifact successfully converged to EXPORT_APPROVED_WITH_WARNINGS.",
            )

        # 2. Hard Blocks & Manual Review
        if report.decision == ExportDecision.MANUAL_REVIEW_REQUIRED:
            return ConvergenceCheckResult(
                outcome=ProductionConvergenceOutcome.MANUAL_REVIEW_REQUIRED,
                should_terminate=True,
                can_export=False,
                iteration=self.current_iteration,
                rationale="Flagged for manual review by Quality Authority.",
            )

        if report.decision == ExportDecision.BLOCKED and not report.repair_required:
            return ConvergenceCheckResult(
                outcome=ProductionConvergenceOutcome.BLOCKED,
                should_terminate=True,
                can_export=False,
                iteration=self.current_iteration,
                rationale="Quality Authority issued terminal non-repairable BLOCKED decision.",
            )

        # 3. Oscillation / Cycle Detection (A -> B -> A)
        if n >= 3:
            # Check if current state hash appeared previously in this loop
            if state_hash in self.state_hashes[:-1]:
                return ConvergenceCheckResult(
                    outcome=ProductionConvergenceOutcome.OSCILLATION_DETECTED,
                    should_terminate=True,
                    can_export=False,
                    iteration=self.current_iteration,
                    cycle_detected=True,
                    stagnation_reason=StagnationReason.STRATEGY_LOOP,
                    rationale=f"State oscillation cycle detected (state hash {state_hash[:8]} repeated).",
                )

        # 4. Check Blocker Reduction Priority
        blockers_reduced = False
        if len(self.hard_blocker_history) >= 2:
            prev_blocker_count = len(self.hard_blocker_history[-2])
            curr_blocker_count = len(self.hard_blocker_history[-1])
            if curr_blocker_count < prev_blocker_count:
                blockers_reduced = True

        # 5. Iteration Budget Check
        if self.current_iteration >= self.max_iterations:
            return ConvergenceCheckResult(
                outcome=ProductionConvergenceOutcome.BUDGET_EXHAUSTED,
                should_terminate=True,
                can_export=False,
                iteration=self.current_iteration,
                stagnation_reason=StagnationReason.BUDGET_EXHAUSTED,
                rationale=f"Maximum allowed repair iterations ({self.max_iterations}) exhausted without convergence.",
            )

        # 6. False Progress Detection (score increased but hard blockers unchanged over 2 cycles)
        if len(self.score_history) >= 3 and len(self.hard_blocker_history) >= 3:
            s0, s1, s2 = self.score_history[-3:]
            b0, b1, b2 = [len(h) for h in self.hard_blocker_history[-3:]]
            if s2 > s0 and b2 > 0 and b0 == b1 == b2:
                # Score increased superficially without resolving hard blockers
                return ConvergenceCheckResult(
                    outcome=ProductionConvergenceOutcome.FALSE_PROGRESS,
                    should_terminate=False,  # Allow pattern detector to escalate scope
                    can_export=False,
                    iteration=self.current_iteration,
                    stagnation_reason=StagnationReason.NO_FINDING_REDUCTION,
                    rationale="False progress detected: scalar score increased but hard blockers remained identical.",
                )

        # 7. Stagnation / No Positive Progress Check (last 3 iterations)
        # ONLY terminate if blockers DID NOT reduce!
        if len(self.score_history) >= 3 and not blockers_reduced:
            s_prev2, s_prev1, s_curr = self.score_history[-3:]
            if s_curr <= s_prev1 <= s_prev2 and self.hard_blocker_history[-1] == self.hard_blocker_history[-2]:
                return ConvergenceCheckResult(
                    outcome=ProductionConvergenceOutcome.NO_POSITIVE_PROGRESS,
                    should_terminate=True,
                    can_export=False,
                    iteration=self.current_iteration,
                    stagnation_reason=StagnationReason.NO_QUALITY_GAIN,
                    rationale="Zero positive quality improvement or blocker reduction over consecutive iterations.",
                )

        return ConvergenceCheckResult(
            outcome=ProductionConvergenceOutcome.CONTINUE_REPAIR,
            should_terminate=False,
            can_export=False,
            iteration=self.current_iteration,
            rationale="Continuing targeted repair.",
        )

