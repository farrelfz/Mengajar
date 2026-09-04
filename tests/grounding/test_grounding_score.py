"""
Unit tests for Grounding Score computation and formula transparency.
"""

import pytest
from app.grounding.contracts import (
    Claim,
    ClaimEvidenceLink,
    Evidence,
    GroundingStatus,
    SourceAuthority,
    SupportRelation,
)
from app.grounding.scoring import GroundingScoreCalculator


def test_score_calculator_computes_explainable_score():
    c1 = Claim(claim_id="c1", content="Claim 1", requires_grounding=True, grounding_status=GroundingStatus.GROUNDED)
    ev1 = Evidence(evidence_id="e1", source_id="s1", content="Ev 1", authority=SourceAuthority.PRIMARY)
    l1 = ClaimEvidenceLink(claim_id="c1", evidence_id="e1", relation=SupportRelation.SUPPORTS, support_score=0.9)

    score = GroundingScoreCalculator.calculate_score([c1], [ev1], [l1])

    assert score.coverage == 1.0
    assert score.support_strength == 0.9
    assert score.authority == 1.0
    assert score.consistency == 1.0
    assert score.overall_score >= 0.85
