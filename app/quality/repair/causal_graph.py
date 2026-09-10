"""
Universal Document Intelligence System V5 — Causal Defect Graph & Root Cause Attribution.

Phase 3D.1: Formal hierarchical causal graph connecting symptoms (Level 0) through
local causes (Level 1), structural causes (Level 2), semantic causes (Level 3),
and source causes (Level 4). Enables lowest-causal-ancestor targeted repairs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.findings import QualityFinding


class CausalLevel(int, Enum):
    """Hierarchical causal depth in the document defect taxonomy."""
    LEVEL_0_SYMPTOM = 0           # Directly observed physical defect (e.g. text clipping, overlap)
    LEVEL_1_LOCAL_CAUSE = 1       # Immediate container or element constraint (e.g. insufficient height)
    LEVEL_2_STRUCTURAL_CAUSE = 2  # Component / layout geometry conflict (e.g. two-column wrapping)
    LEVEL_3_SEMANTIC_CAUSE = 3    # Blueprint grouping / density overload (e.g. over-dense beat)
    LEVEL_4_SOURCE_CAUSE = 4      # Source document inconsistency or missing knowledge


class RelationshipType(str, Enum):
    """Directed relationship between causal nodes."""
    CAUSES = "CAUSES"
    CONTRIBUTES_TO = "CONTRIBUTES_TO"
    CORRELATED_WITH = "CORRELATED_WITH"
    DERIVED_FROM = "DERIVED_FROM"
    MASKS = "MASKS"
    AMPLIFIES = "AMPLIFIES"
    CONFLICTS_WITH = "CONFLICTS_WITH"


class DefectNode(BaseModel):
    """Node in the Causal Defect Graph representing a symptom, cause, or structural defect."""
    model_config = ConfigDict(frozen=True)

    defect_id: str
    canonical_code: str
    severity: str
    artifact_type: str
    page_or_slide: Optional[int] = None
    affected_elements: Tuple[str, ...] = ()
    measurement: float = 0.0
    confidence: float = 1.0
    causal_level: CausalLevel = CausalLevel.LEVEL_0_SYMPTOM
    description: str = ""


class CausalEdge(BaseModel):
    """Directed edge from source defect (or symptom) to its target cause."""
    model_config = ConfigDict(frozen=True)

    source_defect_id: str
    target_cause_id: str
    relationship_type: RelationshipType
    confidence: float = 1.0
    rationale: str = ""


class CausalDefectGraph:
    """Directed Acyclic Graph (DAG) of document defects and inferred causes."""

    def __init__(self) -> None:
        self._nodes: Dict[str, DefectNode] = {}
        self._edges: List[CausalEdge] = []
        self._adjacency: Dict[str, List[CausalEdge]] = {}       # source -> outgoing edges
        self._reverse_adj: Dict[str, List[CausalEdge]] = {}    # target -> incoming edges

    def add_node(self, node: DefectNode) -> None:
        self._nodes[node.defect_id] = node
        if node.defect_id not in self._adjacency:
            self._adjacency[node.defect_id] = []
        if node.defect_id not in self._reverse_adj:
            self._reverse_adj[node.defect_id] = []

    def add_edge(self, edge: CausalEdge) -> None:
        self._edges.append(edge)
        self._adjacency.setdefault(edge.source_defect_id, []).append(edge)
        self._reverse_adj.setdefault(edge.target_cause_id, []).append(edge)

    @property
    def nodes(self) -> Dict[str, DefectNode]:
        return dict(self._nodes)

    @property
    def edges(self) -> Tuple[CausalEdge, ...]:
        return tuple(self._edges)

    def get_node(self, defect_id: str) -> Optional[DefectNode]:
        return self._nodes.get(defect_id)

    def get_causes_for(self, defect_id: str) -> List[DefectNode]:
        """Returns direct causes reachable from this defect/symptom."""
        edges = self._adjacency.get(defect_id, [])
        return [self._nodes[e.target_cause_id] for e in edges if e.target_cause_id in self._nodes]

    def get_symptoms_for(self, cause_id: str) -> List[DefectNode]:
        """Returns all symptoms caused by or deriving from this cause."""
        edges = self._reverse_adj.get(cause_id, [])
        return [self._nodes[e.source_defect_id] for e in edges if e.source_defect_id in self._nodes]

    def find_lowest_causal_ancestor(self, defect_ids: Sequence[str]) -> Optional[DefectNode]:
        """
        Finds the deepest (highest CausalLevel rank) causal ancestor that explains
        or connects multiple given defects.
        """
        if not defect_ids:
            return None

        # Gather all ancestors for each defect with level
        ancestor_sets: List[Dict[str, DefectNode]] = []
        for did in defect_ids:
            ancestors: Dict[str, DefectNode] = {}
            queue = [did]
            visited = set()
            while queue:
                curr = queue.pop(0)
                if curr in visited:
                    continue
                visited.add(curr)
                if curr in self._nodes and curr != did:
                    ancestors[curr] = self._nodes[curr]
                for edge in self._adjacency.get(curr, []):
                    queue.append(edge.target_cause_id)
            ancestor_sets.append(ancestors)

        if not ancestor_sets:
            return None

        # Common ancestors across all defects
        common_keys = set(ancestor_sets[0].keys())
        for s in ancestor_sets[1:]:
            common_keys &= set(s.keys())

        if common_keys:
            # Pick highest causal level, then highest confidence
            candidates = [self._nodes[k] for k in common_keys]
            candidates.sort(key=lambda n: (n.causal_level.value, n.confidence), reverse=True)
            return candidates[0]

        # If no common ancestor across ALL defects, find ancestor covering the most defects
        counts: Dict[str, int] = {}
        for s in ancestor_sets:
            for k in s:
                counts[k] = counts.get(k, 0) + 1

        if counts:
            best_id = max(counts, key=lambda k: (counts[k], self._nodes[k].causal_level.value, self._nodes[k].confidence))
            return self._nodes[best_id]

        # Fallback to direct cause of first defect
        first_causes = self.get_causes_for(defect_ids[0])
        return first_causes[0] if first_causes else self._nodes.get(defect_ids[0])


class DeterministicConfidenceModel:
    """Computes deterministic root cause confidence without AI models."""

    @classmethod
    def calculate_confidence(
        cls,
        measurement_evidence: float,
        spatial_correlation: float,
        cross_signal_agreement: float,
        historical_outcome: float = 1.0,
        causal_specificity: float = 0.90,
    ) -> float:
        """
        RootCauseConfidence = MeasurementEvidence * SpatialCorrelation * CrossSignalAgreement * HistoricalRepairOutcome * CausalSpecificity
        Clamped to [0.05, 1.0].
        """
        raw = (
            max(0.1, measurement_evidence)
            * max(0.1, spatial_correlation)
            * max(0.1, cross_signal_agreement)
            * max(0.2, historical_outcome)
            * max(0.2, causal_specificity)
        )
        # Normalize and cap
        return round(min(1.0, max(0.05, raw)), 4)
