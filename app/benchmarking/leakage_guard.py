"""
Universal Document Intelligence System V5 — Benchmark Leakage Protection Guard.

Phase 4.1: Enforces the Anti-Leakage Invariant. Prevents held-out unseen benchmarks
from updating the RepairOperatorPerformanceRegistry or influencing adaptive operator weights.
"""

from __future__ import annotations

import copy
import logging
from typing import Any, Dict, Optional, Tuple

from app.benchmarking.taxonomy import CorpusSplit
from app.quality.repair.actuation.learning import RepairOperatorPerformanceRegistry

logger = logging.getLogger("benchmarking.leakage_guard")


class BenchmarkLeakageError(RuntimeError):
    """Raised when unseen benchmark execution attempts to mutate persistent operator learning state."""
    pass


class BenchmarkLeakageGuard:
    """Context manager guaranteeing zero benchmark leakage during unseen/adversarial evaluations."""

    def __init__(self, split: CorpusSplit, strict_raise: bool = False) -> None:
        self.split = split
        self.strict_raise = strict_raise
        self.is_protected = split in (CorpusSplit.UNSEEN_GENERALIZATION, CorpusSplit.ADVERSARIAL)
        self._initial_state: Optional[Dict[Tuple[str, str, str, str], Any]] = None
        self.leakage_detected: bool = False
        self.leaked_keys: list[Tuple[str, str, str, str]] = []

    def __enter__(self) -> BenchmarkLeakageGuard:
        if self.is_protected:
            reg = RepairOperatorPerformanceRegistry.get_default()
            # Deep snapshot of performance memory
            self._initial_state = copy.deepcopy(reg._records)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.is_protected and self._initial_state is not None:
            reg = RepairOperatorPerformanceRegistry.get_default()
            current_keys = set(reg._records.keys())
            initial_keys = set(self._initial_state.keys())

            new_keys = current_keys - initial_keys
            modified_keys = []
            for k in initial_keys & current_keys:
                if reg._records[k] != self._initial_state[k]:
                    modified_keys.append(k)

            all_leaks = list(new_keys) + modified_keys
            if all_leaks:
                self.leakage_detected = True
                self.leaked_keys = all_leaks
                logger.warning(
                    "Benchmark leakage detected during %s run! Rolled back %d operator records: %s",
                    self.split.value,
                    len(all_leaks),
                    all_leaks,
                )
                # Strictly restore the initial state to prevent contaminating subsequent fixtures
                reg._records = self._initial_state

                if self.strict_raise:
                    raise BenchmarkLeakageError(
                        f"Anti-Leakage violation: {len(all_leaks)} operator records mutated during {self.split.value} evaluation"
                    )
