"""
Unit tests for deterministic Claim Extraction from blueprints and textual materials.
"""

import pytest
from app.blueprints.content import (
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    FactStatement,
    KnowledgeDomain,
)
from app.grounding.claims import HeuristicClaimExtractor
from app.grounding.contracts import ClaimType


def test_extractor_extracts_definitions_and_formulas():
    content = ContentBlueprint(
        blueprint_id="bp1",
        metadata=ContentMetadata(title="Torque", domain=KnowledgeDomain.PHYSICS),
        concepts=[ConceptDefinition(id="c1", name="Torque", formal_definition="Rotational force analog.", formula="tau = r * F sin(theta)")],
        facts=[FactStatement(id="f1", statement="Rotational equilibrium occurs when net torque is zero.")],
    )

    extractor = HeuristicClaimExtractor()
    claims = extractor.extract_claims(content)

    assert len(claims) == 3
    types = [c.claim_type for c in claims]
    assert ClaimType.DEFINITIONAL in types
    assert ClaimType.QUANTITATIVE in types
    assert ClaimType.FACTUAL in types
