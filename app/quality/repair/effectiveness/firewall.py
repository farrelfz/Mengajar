"""
Universal Document Intelligence System V5 — Repair Strategy Compatibility Firewall.

Phase 3D.1: Strict pre-ranking firewall enforcing artifact type isolation,
root cause compatibility, owning layer bounds, and scope admissibility BEFORE scoring.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Sequence, Tuple

from app.quality.repair.mutation_contract import RepairMutationScope
from app.quality.repair.root_cause import RootCauseType
from app.quality.repair.strategies.base import RepairStrategy

logger = logging.getLogger("quality.repair.firewall")


class IncompatibleStrategyError(ValueError):
    """Raised when an incompatible strategy is forcibly submitted to an artifact."""
    pass


class StrategyRejectionRecord:
    """Record explaining why a strategy was disqualified before ranking."""
    def __init__(self, strategy_id: str, reason: str, filter_stage: str) -> None:
        self.strategy_id = strategy_id
        self.reason = reason
        self.filter_stage = filter_stage

    def __repr__(self) -> str:
        return f"<StrategyRejection: {self.strategy_id} rejected at {self.filter_stage}: {self.reason}>"


class RepairStrategyCompatibilityFirewall:
    """
    Firewall executing ordered deterministic filtration:
    1. Artifact Type Compatibility Filter
    2. Root Cause Compatibility Filter
    3. Owning Layer Compatibility Filter
    4. Mutation Scope Admissibility Filter
    5. Actuator Available and Capable Filter
    """

    @classmethod
    def filter_eligible_strategies(
        cls,
        strategies: Sequence[RepairStrategy],
        artifact_type: str,
        root_cause: Optional[RootCauseType] = None,
        owning_layer: Optional[str] = None,
        allowed_scopes: Optional[Sequence[RepairMutationScope]] = None,
        require_actuator: bool = False,
        actuator_registry: Optional[Any] = None,
        actuation_request: Optional[Any] = None,
        blueprint: Optional[Any] = None,
    ) -> Tuple[List[RepairStrategy], List[StrategyRejectionRecord]]:
        """
        Filters candidate strategies strictly BEFORE utility scoring or candidate ranking.
        Strategies incompatible with artifact_type NEVER proceed past stage 1.
        """
        norm_art = artifact_type.strip().upper()
        eligible: List[RepairStrategy] = []
        rejections: List[StrategyRejectionRecord] = []

        allowed_scope_set = set(allowed_scopes) if allowed_scopes is not None else None

        for strat in strategies:
            # ─────────────────────────────────────────────────────────────
            # STAGE 1: HARD ARTIFACT COMPATIBILITY FILTER
            # ─────────────────────────────────────────────────────────────
            supported = getattr(strat, "supported_artifact_types", ())
            norm_supported = [s.strip().upper() for s in supported]

            if not norm_supported:
                rejections.append(
                    StrategyRejectionRecord(
                        strategy_id=strat.strategy_id,
                        reason=f"Strategy '{strat.strategy_id}' declares no supported artifact types.",
                        filter_stage="ARTIFACT_COMPATIBILITY",
                    )
                )
                continue

            if norm_art not in norm_supported and "ALL" not in norm_supported:
                rejections.append(
                    StrategyRejectionRecord(
                        strategy_id=strat.strategy_id,
                        reason=f"Strategy '{strat.strategy_id}' targets {norm_supported}, incompatible with '{norm_art}'.",
                        filter_stage="ARTIFACT_COMPATIBILITY",
                    )
                )
                continue

            # ─────────────────────────────────────────────────────────────
            # STAGE 2: ROOT CAUSE COMPATIBILITY FILTER
            # ─────────────────────────────────────────────────────────────
            if root_cause is not None:
                supported_causes = getattr(strat, "supported_root_causes", ())
                if supported_causes and root_cause not in supported_causes:
                    rejections.append(
                        StrategyRejectionRecord(
                            strategy_id=strat.strategy_id,
                            reason=f"Strategy '{strat.strategy_id}' does not support root cause '{root_cause.name}'.",
                            filter_stage="ROOT_CAUSE_COMPATIBILITY",
                        )
                    )
                    continue

            # ─────────────────────────────────────────────────────────────
            # STAGE 3: OWNING LAYER COMPATIBILITY FILTER
            # ─────────────────────────────────────────────────────────────
            if owning_layer is not None:
                strat_layer = getattr(strat, "owning_layer", None)
                if strat_layer and strat_layer != owning_layer:
                    rejections.append(
                        StrategyRejectionRecord(
                            strategy_id=strat.strategy_id,
                            reason=f"Strategy owning layer '{strat_layer}' mismatches target layer '{owning_layer}'.",
                            filter_stage="OWNING_LAYER_COMPATIBILITY",
                        )
                    )
                    continue

            # ─────────────────────────────────────────────────────────────
            # STAGE 4: MUTATION SCOPE ADMISSIBILITY FILTER
            # ─────────────────────────────────────────────────────────────
            if allowed_scope_set is not None:
                # Resolve scope
                scope = getattr(strat, "mutation_scope", None)
                if scope is None:
                    # Map heuristically from strategy id/class
                    sid = strat.strategy_id.lower()
                    if "padding" in sid or "token" in sid:
                        scope = RepairMutationScope.LEVEL_1_LOCAL_TOKEN
                    elif "workspace" in sid or "geometry" in sid:
                        scope = RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY
                    elif "layout" in sid or "remap" in sid or "pagination" in sid:
                        scope = RepairMutationScope.LEVEL_3_PAGE_COMPOSITION
                    elif "split" in sid or "merge" in sid:
                        scope = RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING
                    else:
                        scope = RepairMutationScope.LEVEL_3_PAGE_COMPOSITION

                if scope not in allowed_scope_set:
                    rejections.append(
                        StrategyRejectionRecord(
                            strategy_id=strat.strategy_id,
                            reason=f"Strategy mutation scope '{scope.name}' not in allowed reservation scopes.",
                            filter_stage="MUTATION_SCOPE_ADMISSIBILITY",
                        )
                    )
                    continue

            # ─────────────────────────────────────────────────────────────
            # STAGE 5: ACTUATOR AVAILABLE AND CAPABLE FILTER
            # ─────────────────────────────────────────────────────────────
            if require_actuator:
                reg = actuator_registry
                if reg is None:
                    from app.quality.repair.actuation.registry import RepairActuatorRegistry
                    reg = RepairActuatorRegistry.get_default()

                actuator = reg.get_actuator_for_strategy(strat.strategy_id, artifact_type=norm_art)
                if actuator is None:
                    rejections.append(
                        StrategyRejectionRecord(
                            strategy_id=strat.strategy_id,
                            reason=f"Strategy '{strat.strategy_id}' has no registered actuator capable of mutating '{norm_art}'.",
                            filter_stage="ACTUATOR_AVAILABLE_AND_CAPABLE",
                        )
                    )
                    continue

                if actuation_request is not None and blueprint is not None:
                    try:
                        if not actuator.can_actuate(actuation_request, blueprint):
                            rejections.append(
                                StrategyRejectionRecord(
                                    strategy_id=strat.strategy_id,
                                    reason=f"Actuator '{actuator.actuator_id}' cannot actuate for current defect/blueprint.",
                                    filter_stage="ACTUATOR_AVAILABLE_AND_CAPABLE",
                                )
                            )
                            continue
                    except Exception as err:
                        rejections.append(
                            StrategyRejectionRecord(
                                strategy_id=strat.strategy_id,
                                reason=f"Actuator '{actuator.actuator_id}' check failed with error: {err}",
                                filter_stage="ACTUATOR_AVAILABLE_AND_CAPABLE",
                            )
                        )
                        continue

            # Passed all firewall stages
            eligible.append(strat)

        return eligible, rejections
