"""
Universal Document Intelligence System V5 — Causal Path Representation.

Phase 3B: Explicit graph/sequence representing the step-by-step causal chain
from upstream architectural root defect down to observed physical symptoms.
"""

from __future__ import annotations

from typing import List, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.causal.causal_taxonomy import (
    CausalArchitecturalLayer,
    CausalPathEdgeRelationship,
)


class CausalPathNode(BaseModel):
    """A discrete architectural state or event node within a causal path."""
    model_config = ConfigDict(frozen=True)

    layer: CausalArchitecturalLayer
    event: str
    evidence_refs: Tuple[str, ...] = Field(default_factory=tuple)


class CausalPathEdge(BaseModel):
    """Directional edge linking two causal events with relationship and confidence."""
    model_config = ConfigDict(frozen=True)

    from_node_idx: int
    to_node_idx: int
    relationship: CausalPathEdgeRelationship
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class CausalPath(BaseModel):
    """Complete explainable causal path from root cause down to observed symptom."""
    model_config = ConfigDict(frozen=True)

    nodes: Tuple[CausalPathNode, ...] = Field(default_factory=tuple)
    edges: Tuple[CausalPathEdge, ...] = Field(default_factory=tuple)

    @classmethod
    def from_steps(cls, steps: Sequence[Tuple[CausalArchitecturalLayer, str]]) -> CausalPath:
        """Constructs a sequential linear causal path from layer/event pairs."""
        nodes = tuple(CausalPathNode(layer=lyr, event=ev) for lyr, ev in steps)
        edges = tuple(
            CausalPathEdge(
                from_node_idx=i,
                to_node_idx=i + 1,
                relationship=CausalPathEdgeRelationship.CAUSES,
            )
            for i in range(len(nodes) - 1)
        )
        return cls(nodes=nodes, edges=edges)

    def format_text_path(self) -> str:
        """Formats the causal path as an explainable ASCII chain."""
        if not self.nodes:
            return "No causal path"
        if len(self.nodes) == 1:
            return f"{self.nodes[0].event} ({self.nodes[0].layer.value})"

        chain_parts: List[str] = []
        for i, node in enumerate(self.nodes):
            chain_parts.append(f"{node.event} [{node.layer.value}]")
            if i < len(self.edges):
                rel = self.edges[i].relationship.value
                chain_parts.append(f" --({rel})--> ")

        return "".join(chain_parts)

    def format_chain(self) -> str:
        """Alias for format_text_path for Phase 3B compatibility."""
        return self.format_text_path()
