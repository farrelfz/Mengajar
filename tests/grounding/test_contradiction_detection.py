"""
Unit tests for conservative deterministic Contradiction Detection.
"""

import pytest
from app.grounding.consistency import ContradictionDetector
from app.grounding.contracts import Claim, Evidence, SupportRelation


def test_detector_identifies_numeric_contradiction():
    claim = Claim(claim_id="c_num", content="Earth surface gravity is 12 m/s^2", domain="physics")
    ev = Evidence(evidence_id="e_num", source_id="s1", content="Earth standard surface gravitational acceleration is approximately 9.8 m/s^2.", relevance_score=0.8, domain="physics")

    rel, expl = ContradictionDetector.check_relation(claim, ev)

    assert rel == SupportRelation.CONTRADICTS
    assert "Numeric contradiction" in expl
