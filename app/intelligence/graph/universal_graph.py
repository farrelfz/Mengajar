"""
Universal Knowledge Core — UniversalKnowledgeGraph Data Structure.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.intelligence.schemas.knowledge_unit import KnowledgeUnit
from app.intelligence.schemas.relationships import KnowledgeRelationship, RelationshipType


class UniversalKnowledgeGraph(BaseModel):
    """General Directed Typed Graph representing knowledge relationships.
    
    Cycles are explicitly allowed in the core graph (e.g. reciprocal contrasts,
    concept-experiment feedback loops). Core graph is immutable after compilation.
    """
    nodes: Dict[str, KnowledgeUnit] = Field(default_factory=dict)
    edges: List[KnowledgeRelationship] = Field(default_factory=list)

    def get_node(self, unit_id: str) -> Optional[KnowledgeUnit]:
        return self.nodes.get(unit_id)

    def get_outgoing(self, unit_id: str) -> List[KnowledgeRelationship]:
        return [e for e in self.edges if e.source_unit_id == unit_id]

    def get_incoming(self, unit_id: str) -> List[KnowledgeRelationship]:
        return [e for e in self.edges if e.target_unit_id == unit_id]

    def get_neighbors(self, unit_id: str) -> List[str]:
        neighbors = set()
        for e in self.edges:
            if e.source_unit_id == unit_id:
                neighbors.add(e.target_unit_id)
            elif e.target_unit_id == unit_id:
                neighbors.add(e.source_unit_id)
        return list(neighbors)

    def get_edges_by_type(self, rel_type: RelationshipType) -> List[KnowledgeRelationship]:
        return [e for e in self.edges if e.relationship == rel_type]

    @classmethod
    def from_manifest(cls, manifest: Any) -> UniversalKnowledgeGraph:
        units = manifest.units
        nodes_dict = {u.id: u for u in units} if isinstance(units, (list, tuple)) else dict(units)
        return cls(nodes=nodes_dict, edges=list(manifest.relationships))
