"""
Universal Knowledge Core — Derived Specialized Graph Views & Cycle Diagnostics.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Dict, List, Set, Tuple
from pydantic import BaseModel, Field

from app.intelligence.graph.universal_graph import UniversalKnowledgeGraph
from app.intelligence.schemas.relationships import (
    KnowledgeRelationship,
    RelationshipOrigin,
    RelationshipType,
)


class CycleResolutionStrategy(str, Enum):
    EXCLUDE_AI_INFERRED = "exclude_ai_inferred"
    DOWNGRADE_DETERMINISTIC = "downgrade_deterministic"
    BREAK_LOWEST_CONFIDENCE = "break_lowest_confidence"
    MANUAL_OVERRIDE_REQUIRED = "manual_override_required"


class DependencyCycleDiagnostic(BaseModel):
    """Transparent record of cycle detection and edge exclusion in DependencyGraphView.
    Core UniversalKnowledgeGraph is NEVER mutated.
    """
    diagnostic_id: str = Field(default_factory=lambda: f"diag_{uuid.uuid4().hex[:8]}")
    cycle_nodes: List[str]
    cycle_edges: List[str]
    excluded_edges: List[str]
    reason: str
    severity: str = "WARNING"  # WARNING, ERROR
    resolution_strategy: CycleResolutionStrategy


class DependencyGraphView(BaseModel):
    """Derived read-only DAG view of prerequisite relationships.
    
    Enforces strict DAG validation for concept sequencing. If cycles exist,
    AI-inferred edges or low-confidence edges are excluded from the view
    with explicit DependencyCycleDiagnostic records. Core graph remains intact.
    """
    prerequisite_edges: List[KnowledgeRelationship] = Field(default_factory=list)
    topological_sort_order: List[str] = Field(default_factory=list)
    diagnostics: List[DependencyCycleDiagnostic] = Field(default_factory=list)

    @classmethod
    def build_from_graph(cls, graph: UniversalKnowledgeGraph) -> DependencyGraphView:
        # 1. Filter prerequisite edges
        prereq_edges = graph.get_edges_by_type(RelationshipType.PREREQUISITE_OF)
        if not prereq_edges:
            return cls(
                prerequisite_edges=[],
                topological_sort_order=list(graph.nodes.keys()),
                diagnostics=[],
            )

        # 2. Build adjacency for cycle detection
        adj: Dict[str, List[KnowledgeRelationship]] = {node_id: [] for node_id in graph.nodes}
        for edge in prereq_edges:
            if edge.source_unit_id in adj:
                adj[edge.source_unit_id].append(edge)

        excluded_edges: Set[str] = set()
        diagnostics: List[DependencyCycleDiagnostic] = []

        # Tarjan's or DFS cycle detection
        visited: Dict[str, int] = {node_id: 0 for node_id in graph.nodes}  # 0: unvisited, 1: visiting, 2: visited
        stack: List[str] = []

        def _dfs(u: str) -> None:
            visited[u] = 1
            stack.append(u)

            for edge in adj[u]:
                edge_id = f"{edge.source_unit_id}->{edge.target_unit_id}"
                if edge_id in excluded_edges:
                    continue

                v = edge.target_unit_id
                if visited[v] == 1:
                    # Cycle detected! Find cycle nodes
                    cycle_start_idx = stack.index(v)
                    cycle_nodes = list(stack[cycle_start_idx:]) + [v]

                    # Identify candidate edge to exclude
                    cycle_edges_list: List[KnowledgeRelationship] = []
                    for i in range(len(cycle_nodes) - 1):
                        src, tgt = cycle_nodes[i], cycle_nodes[i + 1]
                        for e in adj[src]:
                            if e.target_unit_id == tgt:
                                cycle_edges_list.append(e)

                    # Rule: NEVER exclude EXPLICIT_SOURCE edges silently. Exclude AI_INFERRED first.
                    candidate_to_exclude = None
                    ai_candidates = [e for e in cycle_edges_list if e.evidence.origin == RelationshipOrigin.AI_INFERRED]
                    if ai_candidates:
                        # Exclude lowest confidence AI candidate
                        candidate_to_exclude = min(ai_candidates, key=lambda e: e.evidence.confidence)
                        strategy = CycleResolutionStrategy.EXCLUDE_AI_INFERRED
                    else:
                        rule_candidates = [e for e in cycle_edges_list if e.evidence.origin == RelationshipOrigin.DETERMINISTIC_RULE]
                        if rule_candidates:
                            candidate_to_exclude = min(rule_candidates, key=lambda e: e.evidence.confidence)
                            strategy = CycleResolutionStrategy.DOWNGRADE_DETERMINISTIC
                        else:
                            # Explicit source cycle
                            candidate_to_exclude = min(cycle_edges_list, key=lambda e: e.evidence.confidence)
                            strategy = CycleResolutionStrategy.BREAK_LOWEST_CONFIDENCE

                    target_edge_id = f"{candidate_to_exclude.source_unit_id}->{candidate_to_exclude.target_unit_id}"
                    excluded_edges.add(target_edge_id)

                    diag = DependencyCycleDiagnostic(
                        cycle_nodes=cycle_nodes,
                        cycle_edges=[f"{e.source_unit_id}->{e.target_unit_id}" for e in cycle_edges_list],
                        excluded_edges=[target_edge_id],
                        reason=f"Prerequisite cycle detected across {len(cycle_nodes)-1} nodes. Excluded edge {target_edge_id}.",
                        severity="WARNING",
                        resolution_strategy=strategy,
                    )
                    diagnostics.append(diag)

                elif visited[v] == 0:
                    _dfs(v)

            stack.pop()
            visited[u] = 2

        for node_id in graph.nodes:
            if visited[node_id] == 0:
                _dfs(node_id)

        # 3. Filtered valid edges
        valid_edges = [
            e for e in prereq_edges
            if f"{e.source_unit_id}->{e.target_unit_id}" not in excluded_edges
        ]

        # 4. Kahn's Algorithm for Topological Sort
        in_degree: Dict[str, int] = {node_id: 0 for node_id in graph.nodes}
        valid_adj: Dict[str, List[str]] = {node_id: [] for node_id in graph.nodes}

        for edge in valid_edges:
            valid_adj[edge.source_unit_id].append(edge.target_unit_id)
            in_degree[edge.target_unit_id] += 1

        queue = [n for n, deg in in_degree.items() if deg == 0]
        topo_order: List[str] = []

        while queue:
            curr = queue.pop(0)
            topo_order.append(curr)
            for nxt in valid_adj[curr]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        # Remaining unvisited nodes appended at end
        remaining = [n for n in graph.nodes if n not in topo_order]
        topo_order.extend(remaining)

        return cls(
            prerequisite_edges=valid_edges,
            topological_sort_order=topo_order,
            diagnostics=diagnostics,
        )
