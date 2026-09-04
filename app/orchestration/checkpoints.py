"""
Workflow Checkpointing and Resumption: In-memory state persistence for resuming failed workflows.
"""

from __future__ import annotations

import copy
import time
from typing import Any
from pydantic import BaseModel, Field
from app.orchestration.contracts import ProductionJobContext, StageExecutionResult, StageState


class WorkflowCheckpoint(BaseModel):
    """Snapshot of job execution state at a point in time."""
    checkpoint_id: str
    job_id: str
    timestamp: float
    completed_stages: list[str]
    stage_results: dict[str, StageExecutionResult]
    shared_data: dict[str, Any]
    artifacts: list[str]


class CheckpointStore:
    """Abstract interface for checkpoint storage."""

    def save(self, checkpoint: WorkflowCheckpoint) -> None:
        pass

    def get(self, checkpoint_id: str) -> WorkflowCheckpoint | None:
        pass

    def get_latest_for_job(self, job_id: str) -> WorkflowCheckpoint | None:
        pass


class InMemoryCheckpointStore(CheckpointStore):
    """In-memory dictionary-backed checkpoint repository."""

    def __init__(self) -> None:
        self._checkpoints: dict[str, WorkflowCheckpoint] = {}
        self._job_index: dict[str, list[str]] = {}

    def save(self, checkpoint: WorkflowCheckpoint) -> None:
        self._checkpoints[checkpoint.checkpoint_id] = checkpoint
        if checkpoint.job_id not in self._job_index:
            self._job_index[checkpoint.job_id] = []
        self._job_index[checkpoint.job_id].append(checkpoint.checkpoint_id)

    def get(self, checkpoint_id: str) -> WorkflowCheckpoint | None:
        return self._checkpoints.get(checkpoint_id)

    def get_latest_for_job(self, job_id: str) -> WorkflowCheckpoint | None:
        cids = self._job_index.get(job_id, [])
        if not cids:
            return None
        return self._checkpoints.get(cids[-1])

    @classmethod
    def create_checkpoint_from_context(cls, context: ProductionJobContext) -> WorkflowCheckpoint:
        completed = [sid for sid, res in context.stage_results.items() if res.state == StageState.SUCCEEDED]
        cid = f"chk_{context.job_id}_{int(time.time() * 1000)}"
        return WorkflowCheckpoint(
            checkpoint_id=cid,
            job_id=context.job_id,
            timestamp=time.time(),
            completed_stages=completed,
            stage_results=copy.deepcopy(context.stage_results),
            shared_data=copy.deepcopy(context.shared_data),
            artifacts=list(context.artifacts),
        )

    @classmethod
    def restore_context(cls, checkpoint: WorkflowCheckpoint, request: Any) -> ProductionJobContext:
        ctx = ProductionJobContext(
            job_id=checkpoint.job_id,
            request=request,
            stage_results=copy.deepcopy(checkpoint.stage_results),
            shared_data=copy.deepcopy(checkpoint.shared_data),
            artifacts=list(checkpoint.artifacts),
        )
        return ctx
