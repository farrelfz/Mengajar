"""
Unit tests for Unsupported Claim Detection.
"""

import pytest
from app.grounding.contracts import Claim, ClaimType, GroundingStatus
from app.grounding.unsupported import UnsupportedClaimDetector


def test_detector_flags_foundational_unsupported_claim():
    c_def = Claim(claim_id="c_def", content="Definition of X", claim_type=ClaimType.DEFINITIONAL, importance=1.0, requires_grounding=True, grounding_status=GroundingStatus.UNGROUNDED)
    c_dec = Claim(claim_id="c_dec", content="Let's explore!", claim_type=ClaimType.PEDAGOGICAL, importance=0.1, requires_grounding=False, grounding_status=GroundingStatus.NOT_REQUIRED)

    findings = UnsupportedClaimDetector.detect_findings([c_def, c_dec])

    assert len(findings) == 1
    assert findings[0].claim_id == "c_def"
    assert findings[0].severity == "error"
