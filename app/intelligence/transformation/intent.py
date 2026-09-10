"""
Universal Knowledge Core — Artifact Intent Model.

Phase 1C Semantic Transformation Contract:
Defines artifact-neutral and artifact-specific intent models.
Strictly forbids rendering properties (e.g. CSS, margins, templates, Playwright settings).
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class ArtifactType(str, Enum):
    PRESENTATION = "PRESENTATION"
    HANDOUT = "HANDOUT"
    WORKSHEET = "WORKSHEET"
    SCIENTIFIC_DOCUMENT = "SCIENTIFIC_DOCUMENT"


class AudienceLevel(str, Enum):
    INTRODUCTORY = "INTRODUCTORY"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class UncertaintyHandlingPolicy(str, Enum):
    EXCLUDE_UNRESOLVED = "EXCLUDE_UNRESOLVED"
    FLAG_FOR_CLARIFICATION = "FLAG_FOR_CLARIFICATION"
    ISOLATE_AS_LIMITATION = "ISOLATE_AS_LIMITATION"


class ResolvedArtifactIntent(BaseModel):
    """Artifact-neutral semantic intent capturing high-level transformation directives.
    
    Contains ZERO rendering, layout, or CSS attributes.
    """
    model_config = ConfigDict(frozen=True)

    artifact_type: ArtifactType
    audience: AudienceLevel = AudienceLevel.INTERMEDIATE
    primary_goal: str
    depth: str
    information_density: float = Field(ge=0.0, le=1.0)
    interaction_level: float = Field(ge=0.0, le=1.0)
    evidence_requirement: float = Field(ge=0.0, le=1.0)
    narrative_mode: str
    compression_strategy: str
    sequencing_strategy: str
    knowledge_selection_policy: str
    uncertainty_policy: UncertaintyHandlingPolicy = UncertaintyHandlingPolicy.EXCLUDE_UNRESOLVED
    min_importance_threshold: str = "MEDIUM"
    allow_unresolved_in_core: bool = False


def get_default_intent(
    artifact_type: ArtifactType,
    custom_overrides: Optional[Dict[str, Any]] = None,
) -> ResolvedArtifactIntent:
    """Factory creating tuned default ResolvedArtifactIntent for each artifact type."""
    defaults: Dict[ArtifactType, Dict[str, Any]] = {
        ArtifactType.PRESENTATION: {
            "artifact_type": ArtifactType.PRESENTATION,
            "audience": AudienceLevel.INTERMEDIATE,
            "primary_goal": "Explain concepts progressively with high visual impact and low cognitive load.",
            "depth": "SURFACE_OVERVIEW",
            "information_density": 0.35,
            "interaction_level": 0.20,
            "evidence_requirement": 0.30,
            "narrative_mode": "PROGRESSIVE_REVEAL",
            "compression_strategy": "HIGH_COMPRESSION_BEATS",
            "sequencing_strategy": "STORY_BEATS",
            "knowledge_selection_policy": "CORE_CONCEPTS_ONLY",
            "uncertainty_policy": UncertaintyHandlingPolicy.EXCLUDE_UNRESOLVED,
            "min_importance_threshold": "MEDIUM",
            "allow_unresolved_in_core": False,
        },
        ArtifactType.HANDOUT: {
            "artifact_type": ArtifactType.HANDOUT,
            "audience": AudienceLevel.INTERMEDIATE,
            "primary_goal": "Provide comprehensive, reference-friendly reading material for independent study.",
            "depth": "BALANCED_EXPLANATION",
            "information_density": 0.70,
            "interaction_level": 0.10,
            "evidence_requirement": 0.50,
            "narrative_mode": "HIERARCHICAL_EXPLANATORY",
            "compression_strategy": "MODERATE_EXPLANATORY",
            "sequencing_strategy": "TAXONOMIC_SECTIONS",
            "knowledge_selection_policy": "BALANCED_COVERAGE",
            "uncertainty_policy": UncertaintyHandlingPolicy.FLAG_FOR_CLARIFICATION,
            "min_importance_threshold": "MEDIUM",
            "allow_unresolved_in_core": False,
        },
        ArtifactType.WORKSHEET: {
            "artifact_type": ArtifactType.WORKSHEET,
            "audience": AudienceLevel.INTERMEDIATE,
            "primary_goal": "Drive active student inquiry, prediction, and problem solving without revealing answers upfront.",
            "depth": "INQUIRY_DRIVEN",
            "information_density": 0.50,
            "interaction_level": 0.90,
            "evidence_requirement": 0.60,
            "narrative_mode": "GUIDED_DISCOVERY",
            "compression_strategy": "QUESTION_WITHHOLDING",
            "sequencing_strategy": "INQUIRY_STAGES",
            "knowledge_selection_policy": "PROBLEM_TARGETS",
            "uncertainty_policy": UncertaintyHandlingPolicy.EXCLUDE_UNRESOLVED,
            "min_importance_threshold": "MEDIUM",
            "allow_unresolved_in_core": False,
        },
        ArtifactType.SCIENTIFIC_DOCUMENT: {
            "artifact_type": ArtifactType.SCIENTIFIC_DOCUMENT,
            "audience": AudienceLevel.ADVANCED,
            "primary_goal": "Present rigorous scientific claims backed strictly by verifiable evidence relationships.",
            "depth": "RHO_RIGOROUS_PROOF",
            "information_density": 0.85,
            "interaction_level": 0.05,
            "evidence_requirement": 0.95,
            "narrative_mode": "ARGUMENTATIVE_CLAIM_EVIDENCE",
            "compression_strategy": "EVIDENCE_STRUCTURED",
            "sequencing_strategy": "IMRAD_SECTIONS",
            "knowledge_selection_policy": "CLAIMS_AND_EVIDENCE",
            "uncertainty_policy": UncertaintyHandlingPolicy.ISOLATE_AS_LIMITATION,
            "min_importance_threshold": "MEDIUM",
            "allow_unresolved_in_core": False,
        },
    }

    intent_dict = defaults[artifact_type].copy()
    if custom_overrides:
        intent_dict.update(custom_overrides)

    return ResolvedArtifactIntent.model_validate(intent_dict)
