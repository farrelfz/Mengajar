"""
Unit tests for Workflow State Machine transitions and illegal transition enforcement.
"""

import pytest
from app.orchestration.contracts import ProductionJobStatus, StageState, WorkflowStageType
from app.orchestration.state_machine import WorkflowStateMachine
from app.orchestration.workflow import WorkflowDefinition, WorkflowNode


def test_state_machine_prevents_illegal_transitions():
    wf = WorkflowDefinition(workflow_id="test_sm")
    wf.add_node(WorkflowNode(stage_id="stage_1", stage_type=WorkflowStageType.VALIDATION, dependencies=[]))

    sm = WorkflowStateMachine(wf)
    assert sm.stage_states["stage_1"] == StageState.PENDING

    # Legal: PENDING -> READY -> RUNNING -> SUCCEEDED
    sm.transition_stage("stage_1", StageState.READY)
    sm.transition_stage("stage_1", StageState.RUNNING)
    sm.transition_stage("stage_1", StageState.SUCCEEDED)

    # Illegal: SUCCEEDED -> RUNNING (should raise ValueError)
    with pytest.raises(ValueError, match="Illegal stage transition"):
        sm.transition_stage("stage_1", StageState.RUNNING)


def test_state_machine_failure_propagation():
    wf = WorkflowDefinition(workflow_id="fail_sm")
    wf.add_node(WorkflowNode(stage_id="s1", stage_type=WorkflowStageType.VALIDATION, dependencies=[]))
    wf.add_node(WorkflowNode(stage_id="s2", stage_type=WorkflowStageType.DIRECTING, dependencies=["s1"]))

    sm = WorkflowStateMachine(wf)
    sm.transition_stage("s1", StageState.READY)
    sm.transition_stage("s1", StageState.RUNNING)
    sm.transition_stage("s1", StageState.FAILED)

    sm.propagate_failure("s1")
    assert sm.stage_states["s2"] == StageState.BLOCKED
