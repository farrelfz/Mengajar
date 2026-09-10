"""
Universal Document Intelligence System V5 — Multi-Hypothesis Repair Portfolio & Leverage.

Phase 3D.1: Multi-hypothesis repair candidate generation, cross-defect coverage leverage,
and Pareto portfolio selection. Replaces brittle single-path repair planning.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.findings import QualityFinding
from app.quality.repair.contracts import RepairTarget
from app.quality.repair.mutation_budget import MutationBudgetTracker
from app.quality.repair.mutation_contract import RepairMutation, RepairMutationScope
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType
from app.quality.repair.strategies.base import RepairStrategy

logger = logging.getLogger("quality.repair.portfolio")


class CandidateRepairOption(BaseModel):
    """Evaluated candidate repair strategy within the repair portfolio."""
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
    cross_defect_coverage: float = 1.0
    reversibility: float = 1.0
    minimality: float = 1.0
    leverage_score: float = 1.0
    is_budget_approved: bool = True
    rejection_reason: Optional[str] = None
    is_pareto_dominated: bool = False


class RepairHypothesisSet(BaseModel):
    """Set of competing root-cause hypotheses explaining an observed defect cluster."""
    model_config = ConfigDict(frozen=True)

    canonical_defect_code: str
    artifact_type: str
    hypotheses: Tuple[RootCauseHypothesis, ...]
    primary_hypothesis: RootCauseHypothesis

    @classmethod
    def create(
        cls,
        code: str,
        artifact_type: str,
        primary: RootCauseHypothesis,
        competing: Sequence[RootCauseHypothesis] = (),
    ) -> RepairHypothesisSet:
        all_hyps = (primary,) + tuple(h for h in competing if h.cause_type != primary.cause_type)
        return cls(
            canonical_defect_code=code,
            artifact_type=artifact_type,
            hypotheses=all_hyps,
            primary_hypothesis=primary,
        )


class RepairCandidatePortfolio:
    """Evaluates, ranks, and filters candidate repair options across multiple hypotheses."""

    @classmethod
    def calculate_minimality(cls, scope: RepairMutationScope) -> float:
        """Higher minimality score (close to 1.0) for lower-rank, less invasive scopes."""
        return round(1.0 / (1.0 + (scope.rank - 1) * 0.35), 4)

    @classmethod
    def calculate_leverage(
        cls,
        cross_defect_coverage: float,
        expected_gain: float,
        root_cause_confidence: float,
        minimality: float,
        regression_risk: float,
    ) -> float:
        """
        RegressionAdjustedLeverage = (CrossDefectCoverage * ExpectedGain * RootCauseConfidence * Minimality) / RegressionRisk
        """
        num = cross_defect_coverage * expected_gain * root_cause_confidence * minimality
        den = max(0.01, regression_risk)
        return round(num / den, 4)

    @classmethod
    def calculate_utility(
        cls,
        expected_quality_gain: float,
        root_cause_confidence: float,
        cross_defect_coverage: float,
        reversibility: float,
        minimality: float,
        mutation_cost: float,
        blast_radius: float,
        regression_risk: float,
    ) -> float:
        """
        Canonical Formula:
        (ExpectedGain * Confidence * Coverage * Reversibility * Minimality) / (Cost * BlastRadius * Risk)
        """
        numerator = expected_quality_gain * root_cause_confidence * cross_defect_coverage * reversibility * minimality
        denominator = max(0.001, mutation_cost * max(0.05, blast_radius) * max(0.05, regression_risk))
        return round(numerator / denominator, 4)

    @classmethod
    def map_strategy_to_scope(cls, strategy: RepairStrategy) -> RepairMutationScope:
        sid = strategy.strategy_id.lower()
        if "token" in sid or "padding" in sid or "typography_scale" in sid or "font" in sid:
            return RepairMutationScope.LEVEL_1_LOCAL_TOKEN
        elif "reflow" in sid or "geometry" in sid or "workspace" in sid or "component" in sid:
            return RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY
        elif "layout" in sid or "remap" in sid or "pagination" in sid or "alternation" in sid or "balance" in sid:
            return RepairMutationScope.LEVEL_3_PAGE_COMPOSITION
        elif "split" in sid or "density_split" in sid or "regroup" in sid or "citation" in sid:
            return RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING
        elif "inquiry" in sid or "anti_spoiling" in sid or "methodology" in sid or "claim" in sid:
            return RepairMutationScope.LEVEL_5_ARTIFACT_STRUCTURE
        return RepairMutationScope.LEVEL_3_PAGE_COMPOSITION

    @classmethod
    def evaluate_portfolio(
        cls,
        strategies: Sequence[RepairStrategy],
        target: RepairTarget,
        hypotheses: Sequence[RootCauseHypothesis],
        budget_tracker: MutationBudgetTracker,
        blueprint: Any,
        artifact_type: str,
        total_findings_count: int = 1,
        ineffective_penalties: Optional[Dict[str, float]] = None,
    ) -> List[CandidateRepairOption]:
        """
        Builds and evaluates a portfolio of candidates across all provided hypotheses.
        Filters strategies strictly by supported_artifact_types.
        """
        penalties = ineffective_penalties or {}
        options: List[CandidateRepairOption] = []
        norm_art = artifact_type.strip().upper()

        from app.quality.repair.effectiveness.firewall import RepairStrategyCompatibilityFirewall
        eligible_strats, _ = RepairStrategyCompatibilityFirewall.filter_eligible_strategies(
            strategies=strategies,
            artifact_type=artifact_type,
        )

        for hyp in hypotheses:
            filtered_strats, _ = RepairStrategyCompatibilityFirewall.filter_eligible_strategies(
                strategies=eligible_strats,
                artifact_type=artifact_type,
                root_cause=hyp.cause_type,
            )
            for strat in filtered_strats:
                if not strat.check_preconditions(blueprint, target, hyp):
                    continue

                scope = cls.map_strategy_to_scope(strat)
                minimality = cls.calculate_minimality(scope)
                blast_radius = 0.15 if scope.rank <= 1 else (0.35 if scope.rank <= 2 else (0.60 if scope.rank <= 4 else 0.85))
                regression_risk = 0.04 if strat.risk_level.value == "LOW" else (0.12 if strat.risk_level.value == "MEDIUM" else 0.30)
                reversibility = 1.0  # strategies support rollback snapshotting

                # Cross-defect coverage: how many findings does this hypothesis/strategy affect
                covered_findings = len(hyp.supporting_findings)
                coverage = min(1.0, max(0.2, covered_findings / max(1, total_findings_count)))

                # Apply penalty for historically ineffective strategies
                penalty_factor = penalties.get(strat.strategy_id, 1.0)

                utility = cls.calculate_utility(
                    expected_quality_gain=0.20 * penalty_factor,
                    root_cause_confidence=hyp.confidence,
                    cross_defect_coverage=coverage,
                    reversibility=reversibility,
                    minimality=minimality,
                    mutation_cost=strat.mutation_cost,
                    blast_radius=blast_radius,
                    regression_risk=regression_risk,
                )

                leverage = cls.calculate_leverage(
                    cross_defect_coverage=coverage,
                    expected_gain=0.20 * penalty_factor,
                    root_cause_confidence=hyp.confidence,
                    minimality=minimality,
                    regression_risk=regression_risk,
                )

                # Budget consumption verification
                target_id_str = target.element_id or target.artifact_id or "target"
                sim_mutation = RepairMutation(
                    mutation_id=f"sim_{strat.strategy_id}",
                    artifact_type=norm_art,
                    target_scope=scope,
                    target_ids=(target_id_str,),
                    operation=strat.strategy_id,
                    expected_quality_gain=0.20,
                    mutation_cost=strat.mutation_cost,
                    blast_radius=blast_radius,
                    regression_risk=regression_risk,
                )
                can_consume, reason = budget_tracker.can_consume(sim_mutation)

                options.append(
                    CandidateRepairOption(
                        strategy_id=strat.strategy_id,
                        target=target,
                        hypothesis=hyp,
                        mutation_scope=scope,
                        utility_score=utility,
                        expected_quality_gain=0.20,
                        mutation_cost=strat.mutation_cost,
                        blast_radius=blast_radius,
                        regression_risk=regression_risk,
                        cross_defect_coverage=coverage,
                        reversibility=reversibility,
                        minimality=minimality,
                        leverage_score=leverage,
                        is_budget_approved=can_consume,
                        rejection_reason=reason,
                    )
                )

        # Mark Pareto-dominated candidates
        cls._mark_pareto_dominance(options)

        # Sort:
        # 1. Budget approved first
        # 2. Non-dominated first
        # 3. Higher utility score first
        # 4. Higher leverage first
        options.sort(
            key=lambda o: (
                not o.is_budget_approved,
                o.is_pareto_dominated,
                -o.utility_score,
                -o.leverage_score,
            )
        )
        return options

    @classmethod
    def _mark_pareto_dominance(cls, options: List[CandidateRepairOption]) -> None:
        """
        Candidate B dominates A if:
        - B.cost <= A.cost AND B.risk <= A.risk AND (B.utility > A.utility OR B.leverage > A.leverage)
        """
        for i, a in enumerate(options):
            for j, b in enumerate(options):
                if i == j:
                    continue
                if (
                    b.mutation_cost <= a.mutation_cost
                    and b.regression_risk <= a.regression_risk
                    and b.utility_score >= a.utility_score
                    and b.leverage_score >= a.leverage_score
                    and (b.utility_score > a.utility_score or b.leverage_score > a.leverage_score)
                ):
                    options[i] = a.model_copy(update={"is_pareto_dominated": True})
                    break
