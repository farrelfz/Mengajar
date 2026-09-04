"""
Unit tests for In-Memory Typed Evidence Graph traversal.
"""

import pytest
from app.grounding.contracts import (
    Claim,
    ClaimEvidenceLink,
    Evidence,
    GroundingStatus,
    SupportRelation,
)
from app.grounding.graph import EvidenceGraph


def test_evidence_graph_lookup_and_contradiction_discovery():
    graph = EvidenceGraph()

    c1 = Claim(claim_id="c1", content="Gravity is 12", grounding_status=GroundingStatus.CONTRADICTED)
    ev1 = Evidence(evidence_id="e1", source_id="s1", content="Gravity is 9.8")
    l1 = ClaimEvidenceLink(claim_id="c1", evidence_id="e1", relation=SupportRelation.CONTRADICTS, explanation="Value mismatch")

    graph.add_claim(c1)
    graph.add_evidence(ev1)
    graph.add_link(l1)

    contradictions = graph.find_contradictions()
    assert len(contradictions) == 1
    assert contradictions[0][0].claim_id == "c1"
    assert "Value mismatch" in contradictions[0][2]
