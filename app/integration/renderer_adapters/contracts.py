"""
Universal Knowledge Core — Renderer Contract Adapter Contracts.

Phase 2A Controlled Renderer Adapter Integration:
Defines immutable legacy intermediate representation models for:
- Presentation: SlideBlueprint, LegacyPresentationDeck
- Handout: DocumentOutline, DocumentContent, DocumentContentSection
- Worksheet: LegacyWorksheetActivity, LegacyWorksheetSection, LegacyWorksheetDocument
- Scientific Document: LegacyScientificEvidence, LegacyScientificSubsection, LegacyKtiBabSection, LegacyScientificDocument

These models translate renderer-neutral RenderArtifact contracts into the data structures
expected by legacy rendering systems without requiring renderer modifications.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.blueprints.pedagogical import PedagogicalBlueprint
from app.intelligence.schemas import ContentGroup, KtiBab


# ============================================================================
class GroupingDecisionTrace(BaseModel):
    """Auditable record of why elements were grouped into a legacy render object."""
    model_config = ConfigDict(frozen=True)

    group_id: str
    source_element_ids: Tuple[str, ...]
    grouping_reason: str
    compatibility_signals: Tuple[str, ...] = Field(default_factory=tuple)
    continuity_signals: Tuple[str, ...] = Field(default_factory=tuple)
    capacity_constraint: str = ""
    rejected_candidates: Tuple[str, ...] = Field(default_factory=tuple)
    confidence: float = 1.0

# 1. PRESENTATION CONTRACTS
# ============================================================================

class SlideBlueprint(BaseModel):
    """Legacy intermediate representation for an individual presentation slide."""
    model_config = ConfigDict(frozen=True)

    slide_id: str
    slide_number: int
    act_id: str = "act-01"
    act_name: str = "ACT 1 — PHENOMENON & HOOK"
    title: str
    subtitle: Optional[str] = None
    narrative_function: str = "CONCEPT_INTRODUCTION"
    layout: str = "concept_card"
    visual_priority: str = "MEDIUM"
    visual_intent: str = "concept_explainer"
    content: str = ""
    bullet_points: Tuple[str, ...] = Field(default_factory=tuple)
    source_element_ids: Tuple[str, ...] = Field(default_factory=tuple)  # Many-to-One traceability
    source_refs: Tuple[str, ...] = Field(default_factory=tuple)
    cognitive_load: float = 0.5
    information_gain: float = 0.5
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LegacyPresentationDeck(BaseModel):
    """Legacy intermediate model representing a full slide presentation deck."""
    model_config = ConfigDict(frozen=True)

    deck_title: str
    total_slides: int
    slides: Tuple[SlideBlueprint, ...] = Field(default_factory=tuple)
    source_to_slide_map: Dict[str, Tuple[int, ...]] = Field(default_factory=dict)
    slide_to_source_map: Dict[int, Tuple[str, ...]] = Field(default_factory=dict)
    layout_distribution: Dict[str, int] = Field(default_factory=dict)
    grouping_decision_traces: Tuple[GroupingDecisionTrace, ...] = Field(default_factory=tuple)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)


# ============================================================================
# 2. HANDOUT CONTRACTS
# ============================================================================

class DocumentOutlineItem(BaseModel):
    """Outline node representing a section in the document hierarchy."""
    model_config = ConfigDict(frozen=True)

    section_id: str
    title: str
    level: int = 1
    sequence_index: int = 1
    source_element_ids: Tuple[str, ...] = Field(default_factory=tuple)


class DocumentOutline(BaseModel):
    """Document outline structure preserving reading hierarchy."""
    model_config = ConfigDict(frozen=True)

    outline_id: str
    title: str
    items: Tuple[DocumentOutlineItem, ...] = Field(default_factory=tuple)


class DocumentContentSection(BaseModel):
    """Legacy content section containing narrative prose, definitions, and examples."""
    model_config = ConfigDict(frozen=True)

    section_id: str
    title: str
    level: int = 1
    sequence_index: int = 1
    content: str = ""
    definitions: Tuple[str, ...] = Field(default_factory=tuple)
    examples: Tuple[str, ...] = Field(default_factory=tuple)
    reading_depth: str = "STANDARD"
    source_element_ids: Tuple[str, ...] = Field(default_factory=tuple)  # Many-to-One traceability
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentContent(BaseModel):
    """Legacy document content model for handouts and continuous reading."""
    model_config = ConfigDict(frozen=True)

    document_id: str
    title: str
    outline: DocumentOutline
    sections: Tuple[DocumentContentSection, ...] = Field(default_factory=tuple)
    total_sections: int = 0
    source_refs: Tuple[str, ...] = Field(default_factory=tuple)
    grouping_decision_traces: Tuple[GroupingDecisionTrace, ...] = Field(default_factory=tuple)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)


# ============================================================================
# 3. WORKSHEET CONTRACTS
# ============================================================================

class LegacyWorksheetActivity(BaseModel):
    """Typed active learning activity for worksheets."""
    model_config = ConfigDict(frozen=True)

    activity_id: str
    activity_type: str  # PHENOMENON, PREDICTION, OBSERVATION, INVESTIGATION, DATA_ANALYSIS, REFLECTION
    title: str
    prompt_text: str
    scaffolding_level: str = "MEDIUM"
    withhold_explanation: bool = True
    requires_student_workspace: bool = True
    expected_reasoning_type: str = ""
    sequence_index: int = 1
    source_element_ids: Tuple[str, ...] = Field(default_factory=tuple)
    target_knowledge_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LegacyWorksheetSection(BaseModel):
    """Logical grouping of activities into a worksheet section or inquiry phase."""
    model_config = ConfigDict(frozen=True)

    section_id: str
    title: str
    sequence_index: int = 1
    activities: Tuple[LegacyWorksheetActivity, ...] = Field(default_factory=tuple)
    source_element_ids: Tuple[str, ...] = Field(default_factory=tuple)  # Many-to-One traceability
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LegacyWorksheetDocument(BaseModel):
    """Legacy intermediate representation for worksheets with pedagogical blueprints."""
    model_config = ConfigDict(frozen=True)

    document_id: str
    title: str
    pedagogical_blueprint: Optional[PedagogicalBlueprint] = None
    content_groups: Tuple[ContentGroup, ...] = Field(default_factory=tuple)
    sections: Tuple[LegacyWorksheetSection, ...] = Field(default_factory=tuple)
    total_activities: int = 0
    source_to_activity_map: Dict[str, Tuple[str, ...]] = Field(default_factory=dict)
    grouping_decision_traces: Tuple[GroupingDecisionTrace, ...] = Field(default_factory=tuple)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)


# ============================================================================
# 4. SCIENTIFIC DOCUMENT CONTRACTS
# ============================================================================

class LegacyScientificEvidence(BaseModel):
    """Explicit scientific evidence link preserved in legacy model."""
    model_config = ConfigDict(frozen=True)

    evidence_id: str
    evidence_text: str = ""
    relationship_id: str = ""
    source_refs: Tuple[str, ...] = Field(default_factory=tuple)


class LegacyScientificSubsection(BaseModel):
    """Scientific subsection grouping claims, evidence, and limitations."""
    model_config = ConfigDict(frozen=True)

    subsection_id: str
    title: str
    sequence_index: int = 1
    argument_ids: Tuple[str, ...] = Field(default_factory=tuple)
    claims: Tuple[str, ...] = Field(default_factory=tuple)
    evidence_items: Tuple[LegacyScientificEvidence, ...] = Field(default_factory=tuple)
    evidence_ids: Tuple[str, ...] = Field(default_factory=tuple)
    relationship_ids: Tuple[str, ...] = Field(default_factory=tuple)
    counter_considerations: Tuple[str, ...] = Field(default_factory=tuple)
    limitations: Tuple[str, ...] = Field(default_factory=tuple)
    unsupported_claims: Tuple[str, ...] = Field(default_factory=tuple)
    confidence_score: float = 1.0
    source_element_ids: Tuple[str, ...] = Field(default_factory=tuple)  # Many-to-One traceability
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LegacyKtiBabSection(BaseModel):
    """Standard KTI Chapter containing structured subsections."""
    model_config = ConfigDict(frozen=True)

    bab: KtiBab
    title: str
    sequence_index: int = 1
    subsections: Tuple[LegacyScientificSubsection, ...] = Field(default_factory=tuple)
    source_element_ids: Tuple[str, ...] = Field(default_factory=tuple)


class LegacyScientificDocument(BaseModel):
    """Legacy intermediate representation for scientific documents (KTI)."""
    model_config = ConfigDict(frozen=True)

    document_id: str
    title: str
    babs: Tuple[LegacyKtiBabSection, ...] = Field(default_factory=tuple)
    total_arguments: int = 0
    total_evidence_links: int = 0
    source_to_subsection_map: Dict[str, Tuple[str, ...]] = Field(default_factory=dict)
    evidence_traceability_graph: Dict[str, Tuple[str, ...]] = Field(default_factory=dict)
    unsupported_claims_flagged: Tuple[str, ...] = Field(default_factory=tuple)
    grouping_decision_traces: Tuple[GroupingDecisionTrace, ...] = Field(default_factory=tuple)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
