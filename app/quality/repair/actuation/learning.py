"""
Universal Document Intelligence System V5 — Repair Operator Performance Registry.

Phase 4: Deterministic tracking of repair operator efficacy, score improvement,
drift cost, and regression likelihood scoped by (artifact_type, root_cause, defect_signature).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("quality.repair.actuation.learning")


@dataclass
class OperatorPerformanceRecord:
    """Aggregated performance metrics for a repair operator under specific conditions."""
    operator_id: str
    artifact_type: str
    root_cause: str
    defect_signature: str
    total_attempts: int = 0
    successful_attempts: int = 0
    regressive_attempts: int = 0
    no_effect_attempts: int = 0
    total_score_delta: float = 0.0
    total_drift: float = 0.0
    total_execution_ms: float = 0.0

    @property
    def success_rate(self) -> float:
        return self.successful_attempts / max(1, self.total_attempts)

    @property
    def mean_score_delta(self) -> float:
        return self.total_score_delta / max(1, self.total_attempts)

    @property
    def mean_drift(self) -> float:
        return self.total_drift / max(1, self.total_attempts)


class RepairOperatorPerformanceRegistry:
    """Thread-safe, deterministic performance memory for repair actuators."""

    _instance: Optional[RepairOperatorPerformanceRegistry] = None

    def __init__(self) -> None:
        self._records: Dict[Tuple[str, str, str, str], OperatorPerformanceRecord] = {}

    @classmethod
    def get_default(cls) -> RepairOperatorPerformanceRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_default(cls) -> None:
        cls._instance = None

    def _make_key(
        self,
        operator_id: str,
        artifact_type: str,
        root_cause: str,
        defect_signature: str,
    ) -> Tuple[str, str, str, str]:
        return (
            operator_id.strip(),
            artifact_type.strip().upper(),
            root_cause.strip().upper(),
            defect_signature.strip(),
        )

    def record_execution(
        self,
        operator_id: str,
        artifact_type: str,
        root_cause: str,
        defect_signature: str,
        success: bool,
        score_delta: float,
        drift: float,
        execution_ms: float,
        is_regressive: bool = False,
        is_no_effect: bool = False,
    ) -> None:
        """Records an execution outcome deterministically."""
        key = self._make_key(operator_id, artifact_type, root_cause, defect_signature)
        if key not in self._records:
            self._records[key] = OperatorPerformanceRecord(
                operator_id=key[0],
                artifact_type=key[1],
                root_cause=key[2],
                defect_signature=key[3],
            )

        rec = self._records[key]
        rec.total_attempts += 1
        if success:
            rec.successful_attempts += 1
        if is_regressive:
            rec.regressive_attempts += 1
        if is_no_effect:
            rec.no_effect_attempts += 1
        rec.total_score_delta += score_delta
        rec.total_drift += drift
        rec.total_execution_ms += execution_ms

    def get_operator_multiplier(
        self,
        operator_id: str,
        artifact_type: str,
        root_cause: str,
        defect_signature: str = "",
    ) -> float:
        """Computes empirical utility multiplier based on historical performance."""
        key = self._make_key(operator_id, artifact_type, root_cause, defect_signature)
        rec = self._records.get(key)
        if not rec or rec.total_attempts == 0:
            return 1.0

        if rec.total_attempts >= 2 and rec.success_rate == 0.0:
            return 0.1  # Strongly penalized for repeated failure

        if rec.regressive_attempts > 0:
            return max(0.2, 1.0 - (rec.regressive_attempts * 0.3))

        if rec.success_rate >= 0.8:
            return min(1.5, 1.0 + (rec.mean_score_delta * 0.5))

        return 1.0

    def clear(self) -> None:
        self._records.clear()
