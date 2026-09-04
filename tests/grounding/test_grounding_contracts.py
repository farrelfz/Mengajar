"""
Unit tests for Grounding contracts, enums, and data models.
"""

import pytest
from app.grounding.contracts import (
    ClaimType,
    EvidenceType,
    FreshnessStatus,
    GroundingStatus,
    KnowledgeSourceType,
    SourceAuthority,
    SupportRelation,
)


def test_grounding_enums():
    assert KnowledgeSourceType.LOCAL_DOCUMENT == "local_document"
    assert SourceAuthority.PRIMARY == "primary"
    assert EvidenceType.DEFINITION == "definition"
    assert ClaimType.DEFINITIONAL == "definitional"
    assert SupportRelation.SUPPORTS == "supports"
    assert SupportRelation.CONTRADICTS == "contradicts"
    assert GroundingStatus.GROUNDED == "grounded"
    assert FreshnessStatus.TIME_INSENSITIVE == "time_insensitive"
