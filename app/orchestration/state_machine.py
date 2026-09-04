"""
Workflow State Machine: Enforces valid state transitions and manages stage execution lifecycle.
"""

from __future__ import annotations

from typing import Any
from app.orchestration.contracts import ProductionJobStatus, StageState
from app.orchestration.workflow import WorkflowDefinition


class WorkflowStateMachine:
    """Manages state transitions for production jobs and individual workflow stages."""

    # Valid transitions for stages
    VALID_STAGE_TRANSITIONS: dict[StageState, set[StageState]] = {
        StageState.PENDING: {StageState.READY, StageState.SKIPPED, StageState.BLOCKED},
        StageState.READY: {StageState.RUNNING, StageState.SKIPPED, StageState.BLOCKED},
        StageState.RUNNING: {StageState.SUCCEEDED, StageState.FAILED, StageState.RETRYING, StageState.SKIPPED},
        StageState.RETRYING: {StageState.RUNNING, StageState.FAILED},
        StageState.SUCCEEDED: set(),
        StageState.FAILED: {StageState.RETRYING},
        StageState.SKIPPED: set(),
        StageState.BLOCKED: set(),
    }

    # Valid transitions for jobs
    VALID_JOB_TRANSITIONS: dict[ProductionJobStatus, set[ProductionJobStatus]] = {
        ProductionJobStatus.CREATED: {ProductionJobStatus.RUNNING, ProductionJobStatus.CANCELLED},
        ProductionJobStatus.RUNNING: {
            ProductionJobStatus.WAITING_FOR_REFINEMENT,
            ProductionJobStatus.COMPLETED,
            ProductionJobStatus.FAILED,
            ProductionJobStatus.CANCELLED,
        },
        ProductionJobStatus.WAITING_FOR_REFINEMENT: {ProductionJobStatus.RUNNING, ProductionJobStatus.FAILED},
        ProductionJobStatus.COMPLETED: set(),
        ProductionJobStatus.FAILED: set(),
        ProductionJobStatus.CANCELLED: set(),
    }

    def __init__(self, workflow: WorkflowDefinition) -> None:
        self.workflow = workflow
        self.stage_states: dict[str, StageState] = {sid: StageState.PENDING for sid in workflow.nodes}
        self.job_status: ProductionJobStatus = ProductionJobStatus.CREATED

    def transition_stage(self, stage_id: str, new_state: StageState) -> None:
        if stage_id not in self.stage_states:
            raise KeyError(f"Stage '{stage_id}' does not exist in workflow.")

        curr_state = self.stage_states[stage_id]
        if new_state != curr_state and new_state not in self.VALID_STAGE_TRANSITIONS[curr_state]:
            raise ValueError(f"Illegal stage transition for '{stage_id}': {curr_state.value} -> {new_state.value}")

        self.stage_states[stage_id] = new_state

    def transition_job(self, new_status: ProductionJobStatus) -> None:
        if new_status != self.job_status and new_status not in self.VALID_JOB_TRANSITIONS[self.job_status]:
            raise ValueError(f"Illegal job status transition: {self.job_status.value} -> {new_status.value}")

        self.job_status = new_status

    def is_stage_ready(self, stage_id: str) -> bool:
        """A stage is ready if it is PENDING and all dependencies are SUCCEEDED or SKIPPED."""
        if self.stage_states.get(stage_id) != StageState.PENDING:
            return False

        node = self.workflow.nodes[stage_id]
        for dep in node.dependencies:
            dep_state = self.stage_states.get(dep)
            if dep_state not in [StageState.SUCCEEDED, StageState.SKIPPED]:
                return False

        return True

    def propagate_failure(self, failed_stage_id: str) -> None:
        """Block dependent stages when an upstream required stage fails."""
        for sid, node in self.workflow.nodes.items():
            if failed_stage_id in node.dependencies and self.stage_states[sid] == StageState.PENDING:
                if not node.optional:
                    self.stage_states[sid] = StageState.BLOCKED
                    self.propagate_failure(sid)
