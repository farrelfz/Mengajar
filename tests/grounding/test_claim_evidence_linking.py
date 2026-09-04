"""
Unit tests for Claim-Evidence Linking and support relations.
"""

import pytest
from app.grounding.contracts import Claim, Evidence, GroundingStatus, SupportRelation
from app.grounding.linker import ClaimEvidenceLinker


def test_linker_creates_supports_relation():
    claim = Claim(claim_id="c1", content="Torque is given by tau = r * F sin(theta)", domain="physics")
    ev = Evidence(evidence_id="e1", source_id="s1", content="Magnitude of torque tau is tau = r * F * sin(theta)", relevance_score=0.9, domain="physics")

    links, status = ClaimEvidenceLinker.link_claim(claim, [ev])

    assert len(links) >= 1
    assert links[0].relation == SupportRelation.SUPPORTS
    assert status == GroundingStatus.GROUNDED
