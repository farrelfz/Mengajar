"""
Universal Document Intelligence System V5 — Minimal Intervention Repair Planner.

Phase 3C.1: Multi-dimensional utility scoring, hierarchical scope preference
(Level 1 over Level 4), and budget-gated strategy selection.
"""

from __future__ import annotations

import logging
from typing import Any, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.repair.contracts import RepairAction, RepairPlan, RepairTarget
from app.quality.repair.mutation_contract import RepairMutation, RepairMutationRisk, RepairMutationScope
from app.quality.repair.mutation_budget import MutationBudgetTracker, RepairMutationBudget
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType
from app.quality.repair.strategies.base import RepairStrategy

logger = logging.getLogger("quality.repair.planner")


class CandidateRepairOption(BaseModel):
    """Evaluated candidate repair strategy with computed utility score."""
    model_config = ConfigDict(frozen=True)

    strategy_id: str
    target: RepairTarget
    hypothesis: RootCauseHypothesis
    mutation_scope: RepairMutationScope
    utility_score: float
    expected_quality_gain: float
    mutation_cost: float
    blast_radius: float
    regression_risk: float
    is_budget_approved: bool = True
    rejection_reason: Optional[str] = None


class MinimalInterventionRepairPlanner:
    """Plans minimal-cost, high-utility repairs conforming strictly to mutation budgets."""

    @classmethod
    def calculate_utility(
        cls,
        expected_quality_gain: float,
        strategy_confidence: float,
        root_cause_confidence: float,
        mutation_cost: float,
        blast_radius: float,
        regression_risk: float,
    ) -> float:
        """
        Computes canonical repair utility:
        (gain * conf * rc_conf) / (cost * blast_radius * regression_risk)
        """
        numerator = expected_quality_gain * strategy_confidence * root_cause_confidence
        denominator = max(0.001, mutation_cost * max(0.05, blast_radius) * max(0.05, regression_risk))
        return round(numerator / denominator, 4)

    @classmethod
    def map_strategy_to_scope(cls, strategy: RepairStrategy) -> RepairMutationScope:
        """Determines the canonical hierarchical mutation scope for a strategy."""
        sid = strategy.strategy_id.lower()
        if "padding" in sid or "token" in sid or "density_balance" in sid:
            return RepairMutationScope.LEVEL_1_LOCAL_TOKEN
        elif "workspace" in sid or "geometry" in sid:
            return RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY
        elif "layout" in sid or "remap" in sid or "pagination" in sid or "hierarchy" in sid:
            return RepairMutationScope.LEVEL_3_PAGE_COMPOSITION
        elif "split" in sid or "regroup" in sid or "merge" in sid:
            return RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING
        elif "inquiry" in sid or "anti_spoiling" in sid or "methodology" in sid or "claim" in sid:
            return RepairMutationScope.LEVEL_5_ARTIFACT_STRUCTURE
        return RepairMutationScope.LEVEL_3_PAGE_COMPOSITION

    @classmethod
    def evaluate_candidates(
        cls,
        strategies: Sequence[RepairStrategy],
        target: RepairTarget,
        hypothesis: RootCauseHypothesis,
        budget_tracker: MutationBudgetTracker,
        blueprint: Any,
    ) -> List[CandidateRepairOption]:
        """Evaluates all candidate strategies against preconditions, utility, and budget."""
        from app.quality.repair.effectiveness.firewall import RepairStrategyCompatibilityFirewall
        eligible_strats, _ = RepairStrategyCompatibilityFirewall.filter_eligible_strategies(
            strategies=strategies,
            artifact_type=target.artifact_type,
            root_cause=hypothesis.cause_type,
        )

        options: List[CandidateRepairOption] = []

        for strat in eligible_strats:
            if not strat.check_preconditions(blueprint, target, hypothesis):
                continue

            scope = cls.map_strategy_to_scope(strat)
            blast_radius = 0.2 if scope.rank <= 2 else (0.5 if scope.rank <= 4 else 0.8)
            regression_risk = 0.05 if strat.risk_level.value == "LOW" else (0.15 if strat.risk_level.value == "MEDIUM" else 0.35)

            target_id_str = target.element_id or target.artifact_id or "target"
            sim_mutation = RepairMutation(
                mutation_id=f"sim_{strat.strategy_id}",
                artifact_type=strat.supported_artifact_types[0] if strat.supported_artifact_types else "main",
                target_scope=scope,
                target_ids=(target_id_str,),
                operation=strat.strategy_id,
                expected_quality_gain=0.15,
                mutation_cost=strat.mutation_cost,
                blast_radius=blast_radius,
                regression_risk=regression_risk,
            )

            can_consume, reason = budget_tracker.can_consume(sim_mutation)

            utility = cls.calculate_utility(
                expected_quality_gain=0.15,
                strategy_confidence=0.90,
                root_cause_confidence=hypothesis.confidence,
                mutation_cost=strat.mutation_cost,
                blast_radius=blast_radius,
                regression_risk=regression_risk,
            )

            options.append(
                CandidateRepairOption(
                    strategy_id=strat.strategy_id,
                    target=target,
                    hypothesis=hypothesis,
                    mutation_scope=scope,
                    utility_score=utility,
                    expected_quality_gain=0.15,
                    mutation_cost=strat.mutation_cost,
                    blast_radius=blast_radius,
                    regression_risk=regression_risk,
                    is_budget_approved=can_consume,
                    rejection_reason=reason,
                )
            )

        # Sort:
        # 1. Budget approved first
        # 2. Prefer LOWER mutation scope (scope.rank ascending)
        # 3. Prefer HIGHER utility score (utility descending)
        options.sort(key=lambda o: (not o.is_budget_approved, o.mutation_scope.rank, -o.utility_score))
        return options
