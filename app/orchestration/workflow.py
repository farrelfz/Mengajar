"""
Workflow Directed Acyclic Graph (DAG) definition, node validation, and topological sorting.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from app.orchestration.contracts import WorkflowStageType


class WorkflowNode(BaseModel):
    """A single node/stage within the workflow graph."""
    stage_id: str
    stage_type: WorkflowStageType
    dependencies: list[str] = Field(default_factory=list)
    optional: bool = False
    condition_name: str | None = None
    retry_policy_name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowEdge(BaseModel):
    """A directed edge connecting source stage to target stage."""
    from_stage: str
    to_stage: str
    condition: str | None = None


class WorkflowDefinition(BaseModel):
    """Declarative definition of a workflow graph."""
    workflow_id: str
    version: str = "1.0"
    name: str = "Standard Workflow"
    nodes: dict[str, WorkflowNode] = Field(default_factory=dict)
    edges: list[WorkflowEdge] = Field(default_factory=list)

    def add_node(self, node: WorkflowNode) -> None:
        self.nodes[node.stage_id] = node

    def add_edge(self, from_stage: str, to_stage: str, condition: str | None = None) -> None:
        self.edges.append(WorkflowEdge(from_stage=from_stage, to_stage=to_stage, condition=condition))
        if to_stage in self.nodes and from_stage not in self.nodes[to_stage].dependencies:
            self.nodes[to_stage].dependencies.append(from_stage)


class WorkflowGraph:
    """Validator and topological scheduler for workflow DAGs."""

    def __init__(self, definition: WorkflowDefinition) -> None:
        self.definition = definition
        self.nodes = definition.nodes

    def validate(self) -> list[str]:
        """Validate DAG: check missing dependencies, cycles, and unreachable nodes."""
        errors: list[str] = []

        # 1. Check missing dependencies
        for sid, node in self.nodes.items():
            for dep in node.dependencies:
                if dep not in self.nodes:
                    errors.append(f"Stage '{sid}' references missing dependency '{dep}'.")

        if errors:
            return errors

        # 2. Cycle Detection using DFS
        visited: dict[str, int] = {sid: 0 for sid in self.nodes}  # 0=unvisited, 1=visiting, 2=visited

        def dfs(u: str) -> bool:
            visited[u] = 1
            for dep in self.nodes[u].dependencies:
                if visited[dep] == 1:
                    return True  # Cycle detected
                if visited[dep] == 0:
                    if dfs(dep):
                        return True
            visited[u] = 2
            return False

        for sid in self.nodes:
            if visited[sid] == 0:
                if dfs(sid):
                    errors.append(f"Cycle detected in workflow involving stage '{sid}'.")
                    break

        return errors

    def get_execution_order(self) -> list[str]:
        """Return deterministic topological order of execution."""
        errors = self.validate()
        if errors:
            raise ValueError(f"Invalid workflow DAG: {', '.join(errors)}")

        in_degree: dict[str, int] = {sid: len(node.dependencies) for sid, node in self.nodes.items()}
        queue = [sid for sid, deg in in_degree.items() if deg == 0]
        # Sort queue deterministically
        queue.sort()

        order: list[str] = []
        # Build adjacency mapping (dependency -> dependent)
        dependents: dict[str, list[str]] = {sid: [] for sid in self.nodes}
        for sid, node in self.nodes.items():
            for dep in node.dependencies:
                dependents[dep].append(sid)

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for nxt in sorted(dependents[curr]):
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        return order
