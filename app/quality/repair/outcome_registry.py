"""
Universal Document Intelligence System V5 — Repair Outcome Registry & Historical Memory.

Phase 3D.1: Deterministic repository-local memory tracking empirical repair effectiveness.
Zero AI, zero external APIs. Penalizes historically failing strategies on specific defects
and boosts strategies with verified positive blocker deltas.
"""

from __future__ import annotations

import threading
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field


class RepairOutcomeRecord(BaseModel):
    """Immutable record of an empirical repair intervention outcome."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    defect_code: str
    root_cause_type: str
    strategy_id: str
    mutation_scope: str
    quality_delta: float
    blocker_delta: int           # Negative means blockers were reduced (good!)
    success: bool


class RepairOutcomeRegistry:
    """Repository-local singleton registry tracking empirical repair outcomes."""

    _instance: Optional[RepairOutcomeRegistry] = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._records: List[RepairOutcomeRecord] = []

    @classmethod
    def get_instance(cls) -> RepairOutcomeRegistry:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def record_outcome(
        self,
        artifact_type: str,
        defect_code: str,
        root_cause_type: str,
        strategy_id: str,
        mutation_scope: str,
        quality_delta: float,
        blocker_delta: int,
        success: bool,
    ) -> None:
        with self._lock:
            self._records.append(
                RepairOutcomeRecord(
                    artifact_type=artifact_type.strip().upper(),
                    defect_code=defect_code.strip().upper(),
                    root_cause_type=root_cause_type,
                    strategy_id=strategy_id,
                    mutation_scope=mutation_scope,
                    quality_delta=round(quality_delta, 4),
                    blocker_delta=blocker_delta,
                    success=success,
                )
            )

    def get_strategy_multiplier(
        self,
        strategy_id: str,
        defect_code: Optional[str] = None,
        artifact_type: Optional[str] = None,
    ) -> float:
        """
        Computes deterministic penalty or boost based on historical performance:
        - If strategy failed repeatedly without reducing blockers: penalty (e.g. 0.40)
        - If strategy reliably reduced blockers: boost (e.g. 1.35)
        """
        with self._lock:
            matching = [
                r for r in self._records
                if r.strategy_id == strategy_id
                and (defect_code is None or r.defect_code == defect_code.strip().upper())
                and (artifact_type is None or r.artifact_type == artifact_type.strip().upper())
            ]

        if not matching:
            return 1.0

        failures = [r for r in matching if not r.success or r.blocker_delta >= 0]
        successes = [r for r in matching if r.success and r.blocker_delta < 0]

        if len(failures) >= 2 and not successes:
            return 0.35  # Strong penalty for repeated failure
        elif len(failures) > len(successes):
            return 0.60
        elif len(successes) >= 2:
            return 1.35  # Deterministic boost for proven strategy

        return 1.0

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
