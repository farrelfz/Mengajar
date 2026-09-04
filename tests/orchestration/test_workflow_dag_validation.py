"""
Unit tests for Workflow DAG validation, dependency checks, and cycle detection.
"""

import pytest
from app.orchestration.contracts import WorkflowStageType
from app.orchestration.workflow import (
    WorkflowDefinition,
    WorkflowGraph,
    WorkflowNode,
)


def test_dag_validation_detects_cycles():
    wf = WorkflowDefinition(workflow_id="cyclic_wf")
    # A -> B -> C -> A (cycle)
    wf.add_node(WorkflowNode(stage_id="stage_A", stage_type=WorkflowStageType.VALIDATION, dependencies=["stage_C"]))
    wf.add_node(WorkflowNode(stage_id="stage_B", stage_type=WorkflowStageType.DIRECTING, dependencies=["stage_A"]))
    wf.add_node(WorkflowNode(stage_id="stage_C", stage_type=WorkflowStageType.COMPOSITION, dependencies=["stage_B"]))

    graph = WorkflowGraph(wf)
    errors = graph.validate()

    assert len(errors) >= 1
    assert any("Cycle detected" in e for e in errors)


def test_dag_validation_topological_sort():
    wf = WorkflowDefinition(workflow_id="valid_wf")
    wf.add_node(WorkflowNode(stage_id="stage_A", stage_type=WorkflowStageType.VALIDATION, dependencies=[]))
    wf.add_node(WorkflowNode(stage_id="stage_B", stage_type=WorkflowStageType.DIRECTING, dependencies=["stage_A"]))
    wf.add_node(WorkflowNode(stage_id="stage_C", stage_type=WorkflowStageType.COMPOSITION, dependencies=["stage_B"]))

    graph = WorkflowGraph(wf)
    errors = graph.validate()
    assert len(errors) == 0

    order = graph.get_execution_order()
    assert order == ["stage_A", "stage_B", "stage_C"]
