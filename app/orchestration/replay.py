"""
Deterministic Replay: Captures execution snapshots and validates identical re-execution paths.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from app.orchestration.contracts import ProductionJobRequest, ProductionJobResult


class ExecutionSnapshot(BaseModel):
    snapshot_id: str
    request: ProductionJobRequest
    stage_execution_order: list[str]
    gate_decisions: list[str]
    final_status: str
    artifact_checksums: dict[str, str] = Field(default_factory=dict)


class ReplayResult(BaseModel):
    is_identical: bool
    differences: list[str] = Field(default_factory=list)


class ReplayEngine:
    """Compares original execution snapshot with replayed run."""

    @classmethod
    def compare_runs(cls, snapshot: ExecutionSnapshot, replayed_result: ProductionJobResult) -> ReplayResult:
        diffs = []
        if snapshot.final_status != replayed_result.status.value:
            diffs.append(f"Status mismatch: original='{snapshot.final_status}' vs replayed='{replayed_result.status.value}'")

        if snapshot.stage_execution_order != replayed_result.stage_history:
            diffs.append(f"Stage sequence mismatch: original={snapshot.stage_execution_order} vs replayed={replayed_result.stage_history}")

        return ReplayResult(
            is_identical=len(diffs) == 0,
            differences=diffs,
        )
