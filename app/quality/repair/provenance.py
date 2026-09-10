"""
Universal Document Intelligence System V5 — Repair Provenance Graph & Reporting.

Phase 3B: End-to-end traceability graph linking QualityFindings to RootCauses,
RepairPlans, Mutations, Re-evaluations, and Final Authoritative Decisions.
Generates structured repair_report.json and repair_report.md.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.decisions import UnifiedQualityDecision
from app.quality.repair.contracts import (
    ConvergenceState,
    RepairAction,
    RepairHistoryEntry,
    RepairPlan,
    RepairResult,
)
from app.quality.repair.root_cause import RootCauseHypothesis


class ProvenanceNode(BaseModel):
    """A traceable node in the repair provenance graph."""
    model_config = ConfigDict(frozen=True)

    node_id: str
    node_type: str  # "FINDING", "ROOT_CAUSE", "PLAN", "ACTION", "EVALUATION", "DECISION"
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class ProvenanceEdge(BaseModel):
    """A causal relationship between two provenance nodes."""
    model_config = ConfigDict(frozen=True)

    source_node_id: str
    target_node_id: str
    relation: str  # "EXPLAINS", "PLANS", "EXECUTES", "REVALUATES", "CONCLUDES"


class RepairProvenanceGraph:
    """Directed acyclic graph capturing complete lineage of automated repairs."""

    def __init__(self) -> None:
        self.nodes: Dict[str, ProvenanceNode] = {}
        self.edges: List[ProvenanceEdge] = []
        self.history: List[RepairHistoryEntry] = []

    def add_node(self, node_id: str, node_type: str, payload: Dict[str, Any]) -> None:
        self.nodes[node_id] = ProvenanceNode(node_id=node_id, node_type=node_type, payload=payload)

    def add_edge(self, source_id: str, target_id: str, relation: str) -> None:
        self.edges.append(ProvenanceEdge(source_node_id=source_id, target_node_id=target_id, relation=relation))

    def record_history(self, entry: RepairHistoryEntry) -> None:
        self.history.append(entry)

    def export_json(self) -> str:
        data = {
            "nodes": {k: v.model_dump() for k, v in self.nodes.items()},
            "edges": [e.model_dump() for e in self.edges],
            "history": [h.model_dump() for h in self.history],
        }
        return json.dumps(data, indent=2)

    def generate_markdown_report(
        self,
        artifact_type: str,
        initial_decision: UnifiedQualityDecision,
        final_decision: UnifiedQualityDecision,
        convergence_state: ConvergenceState,
    ) -> str:
        md = []
        md.append("# Repair Execution Report\n")
        md.append(f"- **Artifact Type**: `{artifact_type.upper()}`")
        md.append(f"- **Initial Decision**: `{initial_decision.decision.value}`")
        md.append(f"- **Final Decision**: `{final_decision.decision.value}`")
        md.append(f"- **Convergence State**: `{convergence_state.value}`\n")

        md.append("## Initial Quality Findings & Hard Blockers")
        if initial_decision.hard_blockers:
            for hb in initial_decision.hard_blockers:
                md.append(f"- 🛑 **Hard Blocker**: {hb}")
        else:
            md.append("- *No hard blockers detected*")

        md.append("\n## Repair Iteration History\n")
        if not self.history:
            md.append("*No repair mutations were required or executed.*\n")
        else:
            for entry in self.history:
                md.append(f"### Iteration {entry.iteration}")
                md.append(f"- **Root Cause**: `{entry.root_cause}`")
                mutations_str = ', '.join(entry.mutations) if entry.mutations else 'None'
                md.append(f"- **Mutations Applied**: {mutations_str}")
                md.append(f"- **Pre Decision**: `{entry.authority_decision_before}` -> **Post Decision**: `{entry.authority_decision_after}`")
                md.append(f"- **Score Delta**: `{entry.score_delta:+.3f}`")
                if entry.regressions:
                    md.append(f"- ⚠️ **Regressions**: {', '.join(entry.regressions)}")
                else:
                    md.append("- ✅ **Regression Guard**: Passed (No regressions)")
                md.append("")

        md.append("## Final Authority Assessment")
        md.append(f"- **Export Authorized**: `{final_decision.can_export}`")
        md.append(f"- **Rationale**: {final_decision.rationale}\n")
        return "\n".join(md)
