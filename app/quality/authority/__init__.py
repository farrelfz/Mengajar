"""
Universal Document Intelligence System V5 — Quality Authority Package.

Phase 3A.1: Consolidated Quality Authority, Profiles, Correlation, and Normalization.
"""

from app.quality.authority.correlation import FindingCorrelationEngine
from app.quality.authority.decision_engine import AuthoritativeDecisionEngine
from app.quality.authority.dimension_normalizer import QualityDimensionNormalizer
from app.quality.authority.master_authority import UnifiedQualityAuthority
from app.quality.authority.profiles import (
    HANDOUT_PROFILE,
    PRESENTATION_PROFILE,
    SCIENTIFIC_DOCUMENT_PROFILE,
    WORKSHEET_PROFILE,
    ArtifactQualityProfile,
    get_profile_for_artifact,
)

__all__ = [
    "UnifiedQualityAuthority",
    "FindingCorrelationEngine",
    "QualityDimensionNormalizer",
    "AuthoritativeDecisionEngine",
    "ArtifactQualityProfile",
    "PRESENTATION_PROFILE",
    "HANDOUT_PROFILE",
    "WORKSHEET_PROFILE",
    "SCIENTIFIC_DOCUMENT_PROFILE",
    "get_profile_for_artifact",
]
