"""
Universal Document Intelligence System V5 — Correlation Graph Contract & Representation.

Phase 3B: Explicit graph representation of diagnostic signal relationships across
spatial, structural, semantic, lineage, and failure pattern dimensions.
"""

from __future__ import annotations

from collections import defaultdict
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.causal.contracts import QualitySignal


class CorrelationRelationshipType(str, Enum):
    """Primary structural nature of an observed correlation edge."""
    CO_LOCATED = "CO_LOCATED"
    STRUCTURALLY_RELATED = "STRUCTURALLY_RELATED"
    SEMANTICALLY_RELATED = "SEMANTICALLY_RELATED"
    LINEAGE_RELATED = "LINEAGE_RELATED"
    PATTERN_COMPATIBLE = "PATTERN_COMPATIBLE"
    CAUSALLY_SUGGESTIVE = "CAUSALLY_SUGGESTIVE"


class CorrelationScoreBreakdown(BaseModel):
    """Explainable component score breakdown for a correlation edge."""
    model_config = ConfigDict(frozen=True)

    total_score: float = Field(ge=0.0, le=1.0)
    spatial: float = Field(ge=0.0, le=1.0)
    structural: float = Field(ge=0.0, le=1.0)
    semantic: float = Field(ge=0.0, le=1.0)
    lineage: float = Field(ge=0.0, le=1.0)
    pattern: float = Field(ge=0.0, le=1.0)

    def to_dict(self) -> Dict[str, float]:
        return self.model_dump()


class CorrelationEdge(BaseModel):
    """Immutable edge linking two correlated QualitySignals with explicit evidence."""
    model_config = ConfigDict(frozen=True)

    signal_a_id: str
    signal_b_id: str
    score: float = Field(ge=0.0, le=1.0)
    breakdown: CorrelationScoreBreakdown
    relationship_type: CorrelationRelationshipType
    evidence: Tuple[str, ...] = Field(default_factory=tuple)
    dimensions: Tuple[str, ...] = Field(default_factory=tuple)


class CorrelationGraph(BaseModel):
    """Graph structure maintaining nodes (QualitySignals) and edges (CorrelationEdges)."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    nodes: Dict[str, QualitySignal] = Field(default_factory=dict)
    edges: List[CorrelationEdge] = Field(default_factory=list)

    def add_signal(self, signal: QualitySignal) -> None:
        """Adds a node to the correlation graph."""
        self.nodes[signal.signal_id] = signal

    def add_edge(self, edge: CorrelationEdge) -> None:
        """Adds an edge to the correlation graph."""
        self.edges.append(edge)

    def get_edge(self, signal_a_id: str, signal_b_id: str) -> Optional[CorrelationEdge]:
        """Finds an undirected edge between two signals if present."""
        for edge in self.edges:
            if (edge.signal_a_id == signal_a_id and edge.signal_b_id == signal_b_id) or (
                edge.signal_a_id == signal_b_id and edge.signal_b_id == signal_a_id
            ):
                return edge
        return None

    def get_neighbors(self, signal_id: str) -> List[Tuple[str, CorrelationEdge]]:
        """Returns neighboring signal IDs and the connecting edge."""
        neighbors: List[Tuple[str, CorrelationEdge]] = []
        for edge in self.edges:
            if edge.signal_a_id == signal_id:
                neighbors.append((edge.signal_b_id, edge))
            elif edge.signal_b_id == signal_id:
                neighbors.append((edge.signal_a_id, edge))
        return neighbors

    def find_connected_components(self, min_score: float = 0.60) -> List[Set[str]]:
        """Computes deterministic connected components above the minimum correlation score."""
        adj: Dict[str, Set[str]] = defaultdict(set)
        for edge in self.edges:
            if edge.score >= min_score:
                adj[edge.signal_a_id].add(edge.signal_b_id)
                adj[edge.signal_b_id].add(edge.signal_a_id)

        visited: Set[str] = set()
        components: List[Set[str]] = []

        # Deterministic node traversal in sorted order
        for node_id in sorted(self.nodes.keys()):
            if node_id not in visited and node_id in adj:
                comp: Set[str] = set()
                queue = [node_id]
                visited.add(node_id)
                while queue:
                    curr = queue.pop(0)
                    comp.add(curr)
                    for neighbor in sorted(adj[curr]):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                if len(comp) > 1:
                    components.append(comp)

        return components

    def get_isolated_signals(self, min_score: float = 0.60) -> List[str]:
        """Returns signals that have no connecting edges >= min_score."""
        connected: Set[str] = set()
        for edge in self.edges:
            if edge.score >= min_score:
                connected.add(edge.signal_a_id)
                connected.add(edge.signal_b_id)

        return [nid for nid in sorted(self.nodes.keys()) if nid not in connected]
