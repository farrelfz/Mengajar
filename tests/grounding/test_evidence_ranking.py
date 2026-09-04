"""
Unit tests for multi-dimensional deterministic Evidence Ranking.
"""

import pytest
from app.grounding.contracts import Claim, ClaimType, Evidence, SourceAuthority
from app.grounding.evidence_ranker import EvidenceRanker


def test_evidence_ranking_prioritizes_primary_authority():
    claim = Claim(claim_id="c1", content="Torque is rotational force", domain="physics")

    ev_low = Evidence(evidence_id="e_low", source_id="s_low", content="Torque is rotational force", authority=SourceAuthority.LOW, relevance_score=0.9, domain="physics")
    ev_prim = Evidence(evidence_id="e_prim", source_id="s_prim", content="Torque is rotational force", authority=SourceAuthority.PRIMARY, relevance_score=0.9, domain="physics")

    ranked = EvidenceRanker.rank_evidence(claim, [ev_low, ev_prim])

    assert len(ranked) == 2
    assert ranked[0][1].evidence_id == "e_prim"
    assert ranked[0][0] > ranked[1][0]
