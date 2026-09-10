"""
Universal Knowledge Core — Artifact-Specific Semantic Blueprints.

Phase 1C Semantic Transformation Contract:
Defines immutable semantic blueprints for Presentation, Handout, Worksheet,
and Scientific Document artifacts.

Contains NO layout parameters, CSS, font sizes, margins, or rendering engine code.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.intelligence.transformation.intent import ArtifactType, ResolvedArtifactIntent


class ArtifactBlueprint(BaseModel):
    """Base immutable semantic blueprint for transformed knowledge."""
    model_config = ConfigDict(frozen=True)

    blueprint_id: str
    artifact_type: ArtifactType
    source_manifest_id: str
    document_title: str
    intent: ResolvedArtifactIntent
    selected_knowledge_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)
    selection_rationale: str = ""
    created_at: float = Field(default_factory=time.time)


# ============================================================================
# 1. PRESENTATION BLUEPRINT
# ============================================================================

class ConceptualBeat(BaseModel):
    """A compressed conceptual beat designed for progressive reveal in presentations."""
    model_config = ConfigDict(frozen=True)

    beat_id: str
    sequence_index: int
    title: str
    primary_concept_unit_id: str
    supporting_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)
    narrative_function: str  # HOOK, FOUNDATION, CORE_MECHANISM, APPLICATION, SUMMARY
    information_gain: float = Field(ge=0.0, le=1.0)
    cognitive_load_target: float = Field(ge=0.0, le=1.0)
    visual_priority: str  # HIGH_DIAGRAM, EQUATION_FOCUS, CONCEPT_TEXT
    selection_rationale: str
    knowledge_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)


class PresentationBlueprint(ArtifactBlueprint):
    """Semantic blueprint for presentation artifacts."""
    beats: Tuple[ConceptualBeat, ...] = Field(default_factory=tuple)


# ============================================================================
# 2. HANDOUT BLUEPRINT
# ============================================================================

class ExplanatorySection(BaseModel):
    """A hierarchical explanatory section for comprehensive reading handouts."""
    model_config = ConfigDict(frozen=True)

    section_id: str
    sequence_index: int
    topic: str
    heading_level: int = 1
    core_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)
    supporting_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)
    definitions: Tuple[str, ...] = Field(default_factory=tuple)
    examples: Tuple[str, ...] = Field(default_factory=tuple)
    relationships: Tuple[str, ...] = Field(default_factory=tuple)
    reading_depth: str
    knowledge_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)


class HandoutBlueprint(ArtifactBlueprint):
    """Semantic blueprint for handout artifacts."""
    sections: Tuple[ExplanatorySection, ...] = Field(default_factory=tuple)


# ============================================================================
# 3. WORKSHEET BLUEPRINT
# ============================================================================

class LearningActivityType(str, Enum):
    PHENOMENON = "PHENOMENON"
    PREDICTION = "PREDICTION"
    QUESTION = "QUESTION"
    OBSERVATION = "OBSERVATION"
    INVESTIGATION = "INVESTIGATION"
    DATA_ANALYSIS = "DATA_ANALYSIS"
    REFLECTION = "REFLECTION"


class LearningActivity(BaseModel):
    """An active learning activity designed for student inquiry without answer spoiling."""
    model_config = ConfigDict(frozen=True)

    activity_id: str
    sequence_index: int
    activity_type: LearningActivityType
    title: str
    prompt_text: str
    target_knowledge_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)
    scaffolding_level: str  # HIGH, MEDIUM, LOW
    withhold_explanation: bool = True
    expected_reasoning_type: str
    knowledge_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)


class WorksheetBlueprint(ArtifactBlueprint):
    """Semantic blueprint for worksheet / LKS artifacts."""
    activities: Tuple[LearningActivity, ...] = Field(default_factory=tuple)


# ============================================================================
# 4. SCIENTIFIC DOCUMENT BLUEPRINT
# ============================================================================

class ScientificArgumentRole(str, Enum):
    BACKGROUND_CLAIM = "BACKGROUND_CLAIM"
    HYPOTHESIS = "HYPOTHESIS"
    METHODOLOGY_DESCRIPTION = "METHODOLOGY_DESCRIPTION"
    EMPIRICAL_EVIDENCE = "EMPIRICAL_EVIDENCE"
    COUNTER_CONSIDERATION = "COUNTER_CONSIDERATION"
    LIMITATION = "LIMITATION"
    CONCLUSION = "CONCLUSION"


class ScientificArgumentUnit(BaseModel):
    """A claim-evidence scientific argument unit."""
    model_config = ConfigDict(frozen=True)

    argument_id: str
    sequence_index: int
    claim_unit_id: str
    argument_role: ScientificArgumentRole
    claim_statement: str
    supporting_evidence_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)
    evidence_relationship_ids: Tuple[str, ...] = Field(default_factory=tuple)
    counter_considerations: Tuple[str, ...] = Field(default_factory=tuple)
    confidence: float = Field(ge=0.0, le=1.0)
    source_traceability: Tuple[str, ...] = Field(default_factory=tuple)
    knowledge_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)


class ScientificDocumentBlueprint(ArtifactBlueprint):
    """Semantic blueprint for scientific document / KTI artifacts."""
    arguments: Tuple[ScientificArgumentUnit, ...] = Field(default_factory=tuple)
