"""
Unit tests for False Positive Safety: decorative statements are ignored and missing evidence is INSUFFICIENT, not CONTRADICTION.
"""

import pytest
from app.grounding.contracts import Claim, ClaimType, GroundingStatus, SupportRelation
from app.grounding.engine import KnowledgeGroundingEngine


def test_decorative_rhetoric_not_flagged_as_unsupported():
    engine = KnowledgeGroundingEngine(providers=[])
    text = "Let's explore physics together! Welcome to the lesson."

    grounded_context = engine.ground_material(text, domain="physics")
    rep = grounded_context.report

    # Decorative statements must have requires_grounding = False
    assert rep.claims_unsupported == 0
    assert len(rep.findings) == 0


def test_missing_evidence_is_insufficient_not_contradicted():
    engine = KnowledgeGroundingEngine(providers=[])
    text = "An unrecorded novel discovery in physics."

    grounded_context = engine.ground_material(text, domain="physics")
    rep = grounded_context.report

    assert rep.claims_contradicted == 0
    assert rep.claims_unsupported == 1
