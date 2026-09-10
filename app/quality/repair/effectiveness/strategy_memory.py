"""
Universal Document Intelligence System V5 — Self-Disqualifying Strategy Memory.

Phase 3D.1: Fine-grained tracking of strategy attempts bound to (artifact_type, artifact_id,
root_cause_cluster, strategy_id). Automatically disqualifies strategies that fail to produce
causal finding reduction across 2 consecutive cycles.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.repair.effectiveness.contracts import EffectivenessStatus, RepairEffectivenessResult

logger = logging.getLogger("quality.repair.memory")


class StrategyHistoryKey(BaseModel):
    """Granular composite key indexing repair strategy memory."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    artifact_id: str
    root_cause_cluster: str
    strategy_id: str


class StrategyHistoryEntry(BaseModel):
    """Accumulated performance metrics for a specific strategy on a defect cluster."""
    key: StrategyHistoryKey
    attempt_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    consecutive_ineffective_count: int = 0
    total_severity_delta: float = 0.0
    total_quality_delta: float = 0.0
    regression_count: int = 0
    last_state_hash: Optional[str] = None
    is_disqualified: bool = False
    disqualification_reason: Optional[str] = None
    last_defect_signature: Optional[str] = None


class SelfDisqualifyingStrategyMemory:
    """
    In-memory deterministic historical tracker enforcing the 2-cycle disqualification rule.
    Prevents repeated ineffective mutations from burning iteration budgets.
    """

    MAX_CONSECUTIVE_INEFFECTIVE_ATTEMPTS = 2

    def __init__(self) -> None:
        self._entries: Dict[StrategyHistoryKey, StrategyHistoryEntry] = {}

    def record_attempt_result(
        self,
        key: StrategyHistoryKey,
        result: RepairEffectivenessResult,
        defect_signature: str,
        post_state_hash: str,
    ) -> StrategyHistoryEntry:
        """Records an attempt outcome and updates disqualification status."""
        entry = self._entries.get(
            key,
            StrategyHistoryEntry(key=key),
        )

        new_attempts = entry.attempt_count + 1
        new_sev_delta = entry.total_severity_delta + result.severity_delta
        new_qual_delta = entry.total_quality_delta + result.quality_delta
        new_regs = entry.regression_count + (1 if result.regression_introduced else 0)

        is_effective = result.overall_status == EffectivenessStatus.EFFECTIVE

        if is_effective:
            new_success = entry.success_count + 1
            new_failure = entry.failure_count
            new_consecutive_ineffective = 0
            is_disqualified = False
            disqual_reason = None
        else:
            new_success = entry.success_count
            new_failure = entry.failure_count + 1
            # Increment consecutive ineffective attempts
            new_consecutive_ineffective = entry.consecutive_ineffective_count + 1

            if new_consecutive_ineffective >= self.MAX_CONSECUTIVE_INEFFECTIVE_ATTEMPTS:
                is_disqualified = True
                disqual_reason = (
                    f"Disqualified after {new_consecutive_ineffective} consecutive ineffective attempts "
                    f"against defect signature '{defect_signature}' (Cause: {key.root_cause_cluster})."
                )
                logger.warning("Strategy '%s' DISQUALIFIED: %s", key.strategy_id, disqual_reason)
            else:
                is_disqualified = False
                disqual_reason = None

        updated_entry = StrategyHistoryEntry(
            key=key,
            attempt_count=new_attempts,
            success_count=new_success,
            failure_count=new_failure,
            consecutive_ineffective_count=new_consecutive_ineffective,
            total_severity_delta=round(new_sev_delta, 4),
            total_quality_delta=round(new_qual_delta, 4),
            regression_count=new_regs,
            last_state_hash=post_state_hash,
            is_disqualified=is_disqualified,
            disqualification_reason=disqual_reason,
            last_defect_signature=defect_signature,
        )

        self._entries[key] = updated_entry
        return updated_entry

    def is_strategy_disqualified(
        self,
        artifact_type: str,
        artifact_id: str,
        root_cause_cluster: str,
        strategy_id: str,
        current_defect_signature: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Returns (is_disqualified, reason).
        If the defect signature materially changed, the strategy is unblocked for re-evaluation.
        """
        key = StrategyHistoryKey(
            artifact_type=artifact_type.strip().upper(),
            artifact_id=artifact_id,
            root_cause_cluster=root_cause_cluster,
            strategy_id=strategy_id,
        )
        entry = self._entries.get(key)
        if not entry or not entry.is_disqualified:
            return False, None

        # Check if defect signature materially changed
        if current_defect_signature and entry.last_defect_signature:
            if current_defect_signature != entry.last_defect_signature:
                # Material signature change unlocks the strategy
                return False, None

        return True, entry.disqualification_reason

    def get_disqualified_strategies(
        self,
        artifact_type: str,
        artifact_id: str,
        root_cause_cluster: str,
    ) -> List[Tuple[str, str]]:
        """Returns list of (strategy_id, reason) disqualified for this cluster."""
        disquals = []
        norm_art = artifact_type.strip().upper()
        for key, entry in self._entries.items():
            if (
                key.artifact_type == norm_art
                and key.artifact_id == artifact_id
                and key.root_cause_cluster == root_cause_cluster
                and entry.is_disqualified
            ):
                disquals.append((key.strategy_id, entry.disqualification_reason or "Ineffective loop."))
        return disquals

    def clear(self) -> None:
        """Clears memory (used for test isolation)."""
        self._entries.clear()
