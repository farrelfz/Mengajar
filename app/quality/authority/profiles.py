"""
Universal Document Intelligence System V5 — Artifact Quality Profiles.

Phase 3A.1: Format-specific quality calibration profiles defining hard blockers,
warning tolerances, dimension weights, and zero-tolerance invariants across
Presentation, Handout, Worksheet, and Scientific Document.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Set

from app.quality.contracts.dimensions import CanonicalQualityDimension


@dataclass(frozen=True)
class ArtifactQualityProfile:
    """Base specification of quality thresholds and hard blockers for an artifact type."""
    artifact_type: str
    hard_blockers: FrozenSet[str]
    warning_tolerance: int = 3
    min_overall_score: float = 0.80
    min_dimension_score: float = 0.60
    dimension_weights: Dict[str, float] = field(default_factory=dict)

    def is_hard_blocker(self, code: str) -> bool:
        return code.strip().upper() in self.hard_blockers


PRESENTATION_HARD_BLOCKERS: FrozenSet[str] = frozenset({
    "TEXT_CLIPPING",
    "ELEMENT_COLLISION",
    "FONT_TOO_SMALL",
    "FIVE_CONSECUTIVE_IDENTICAL_LAYOUT",
    "COGNITIVE_OVERLOAD",
    "EXCESSIVE_DENSITY",
    "OVERLAPPING_CONTENT",
    "TRACEABILITY_BREAK",
})

HANDOUT_HARD_BLOCKERS: FrozenSet[str] = frozenset({
    "FONT_TOO_SMALL",
    "TINY_BODY_TEXT",
    "COGNITIVE_OVERLOAD",
    "EXTREME_DENSE_PAGE",
    "STRUCTURAL_HIERARCHY_INVERSION",
    "HEADING_HIERARCHY_INVERSION",
    "ACCIDENTAL_PAGE",
    "ALMOST_EMPTY_ACCIDENTAL_PAGE",
    "TRACEABILITY_BREAK",
})

WORKSHEET_HARD_BLOCKERS: FrozenSet[str] = frozenset({
    "ANTI_SPOILING_BREACH",
    "ANSWER_LEAKAGE",
    "EXPLANATION_LEAKED_BEFORE_PREDICTION",
    "ANSWER_LEAKED_INSIDE_QUESTION",
    "OBSERVATION_CONCLUSION_PREFILLED",
    "ELEMENT_COLLISION",
    "WORKSPACE_OVERLAPS_CONTENT",
    "INQUIRY_ARC_BROKEN",
    "QUESTION_SEQUENCE_NO_INQUIRY",
    "TRACEABILITY_BREAK",
})

SCIENTIFIC_DOCUMENT_HARD_BLOCKERS: FrozenSet[str] = frozenset({
    "UNSUPPORTED_SCIENTIFIC_CLAIM",
    "CLAIM_WITHOUT_EVIDENCE",
    "UNSUPPORTED_CLAIM_AS_FACT",
    "MISATTRIBUTED_EVIDENCE",
    "EVIDENCE_ATTACHED_TO_WRONG_CLAIM",
    "FABRICATED_CITATION",
    "FABRICATED_CITATION_MARKER",
    "CONTRADICTORY_CLAIMS",
    "CONTRADICTORY_ADJACENT_CLAIMS",
    "STRUCTURAL_HIERARCHY_INVERSION",
    "BAB_HIERARCHY_INVERSION",
    "TRACEABILITY_BREAK",
})


PRESENTATION_PROFILE = ArtifactQualityProfile(
    artifact_type="PRESENTATION",
    hard_blockers=PRESENTATION_HARD_BLOCKERS,
    warning_tolerance=3,
    min_overall_score=0.85,
    min_dimension_score=0.70,
    dimension_weights={
        CanonicalQualityDimension.PHYSICAL_GEOMETRY.value: 1.5,
        CanonicalQualityDimension.READABILITY.value: 1.3,
        CanonicalQualityDimension.STYLE_DESIGN.value: 1.2,
        CanonicalQualityDimension.COGNITIVE_LOAD.value: 1.2,
        CanonicalQualityDimension.NARRATIVE_FLOW.value: 1.0,
        CanonicalQualityDimension.BLUEPRINT_FIDELITY.value: 1.0,
        CanonicalQualityDimension.SEMANTIC_GROUNDING.value: 1.0,
    },
)

HANDOUT_PROFILE = ArtifactQualityProfile(
    artifact_type="HANDOUT",
    hard_blockers=HANDOUT_HARD_BLOCKERS,
    warning_tolerance=3,
    min_overall_score=0.85,
    min_dimension_score=0.70,
    dimension_weights={
        CanonicalQualityDimension.READABILITY.value: 1.4,
        CanonicalQualityDimension.NARRATIVE_FLOW.value: 1.3,
        CanonicalQualityDimension.PAGE_BALANCE.value: 1.2,
        CanonicalQualityDimension.COGNITIVE_LOAD.value: 1.2,
        CanonicalQualityDimension.BLUEPRINT_FIDELITY.value: 1.0,
        CanonicalQualityDimension.SEMANTIC_GROUNDING.value: 1.0,
    },
)

WORKSHEET_PROFILE = ArtifactQualityProfile(
    artifact_type="WORKSHEET",
    hard_blockers=WORKSHEET_HARD_BLOCKERS,
    warning_tolerance=2,
    min_overall_score=0.85,
    min_dimension_score=0.75,
    dimension_weights={
        CanonicalQualityDimension.INQUIRY_STRUCTURE.value: 1.8,
        CanonicalQualityDimension.PHYSICAL_GEOMETRY.value: 1.4,
        CanonicalQualityDimension.NARRATIVE_FLOW.value: 1.2,
        CanonicalQualityDimension.READABILITY.value: 1.0,
        CanonicalQualityDimension.BLUEPRINT_FIDELITY.value: 1.0,
        CanonicalQualityDimension.SEMANTIC_GROUNDING.value: 1.0,
    },
)

SCIENTIFIC_DOCUMENT_PROFILE = ArtifactQualityProfile(
    artifact_type="SCIENTIFIC_DOCUMENT",
    hard_blockers=SCIENTIFIC_DOCUMENT_HARD_BLOCKERS,
    warning_tolerance=2,
    min_overall_score=0.88,
    min_dimension_score=0.80,
    dimension_weights={
        CanonicalQualityDimension.CLAIM_VERACITY.value: 2.0,
        CanonicalQualityDimension.SCIENTIFIC_RIGOR.value: 1.8,
        CanonicalQualityDimension.SEMANTIC_GROUNDING.value: 1.5,
        CanonicalQualityDimension.KNOWLEDGE_TRACEABILITY.value: 1.3,
        CanonicalQualityDimension.BLUEPRINT_FIDELITY.value: 1.0,
        CanonicalQualityDimension.READABILITY.value: 1.0,
    },
)

DEFAULT_PROFILE = ArtifactQualityProfile(
    artifact_type="DEFAULT",
    hard_blockers=frozenset({"TEXT_CLIPPING", "TRACEABILITY_BREAK"}),
    warning_tolerance=3,
    min_overall_score=0.80,
    min_dimension_score=0.60,
    dimension_weights={},
)


def get_profile_for_artifact(artifact_type: str) -> ArtifactQualityProfile:
    """Retrieve the authoritative quality profile for an artifact type."""
    norm = artifact_type.strip().upper()
    if "PRESENTATION" in norm or "SLIDE" in norm:
        return PRESENTATION_PROFILE
    if "HANDOUT" in norm or "READING" in norm:
        return HANDOUT_PROFILE
    if "WORKSHEET" in norm or "LKS" in norm or "ACTIVITY" in norm:
        return WORKSHEET_PROFILE
    if "SCIENTIFIC" in norm or "KTI" in norm or "PAPER" in norm or "ACADEMIC" in norm:
        return SCIENTIFIC_DOCUMENT_PROFILE
    return DEFAULT_PROFILE
