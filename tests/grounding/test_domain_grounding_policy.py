"""
Unit tests for Domain Grounding Policies.
"""

import pytest
from app.grounding.contracts import ClaimType, SourceAuthority
from app.grounding.policies import DomainGroundingPolicyRegistry


def test_domain_policy_registry_returns_configured_policies():
    phys_policy = DomainGroundingPolicyRegistry.get_policy("physics")
    assert phys_policy.min_overall_score >= 0.85
    assert phys_policy.min_authority == SourceAuthority.HIGH
    assert ClaimType.QUANTITATIVE in phys_policy.mandatory_grounded_claim_types

    gen_policy = DomainGroundingPolicyRegistry.get_policy("unknown_domain")
    assert gen_policy.domain == "general"
