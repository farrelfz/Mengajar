"""
KIR AI Document Intelligence — Intelligence Domain Schemas.

This module defines the complete Pydantic data model for Batch 2:
content units, semantic classification, research traceability,
importance scoring, visual intent, and blueprint proposals.

Schema version: 2.0
  - Extends Batch 1 schema with DocumentGenre, ResearchTraceability
  - Adds full KTI BAB 1–5 semantic roles

All enums are string-typed for JSON serialization compatibility.
All models use strict field types — no untyped dict fields in core paths.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from app.intelligence.schemas.content_type import ContentType

# ══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ══════════════════════════════════════════════════════════════════════════════


class DocumentGenre(str, Enum):
    """Top-level genre of the source document."""

    TUTORIAL = "tutorial"
    RESEARCH_REPORT = "research_report"
    PRESENTATION = "presentation"
    GENERAL = "general"


class KtiBab(str, Enum):
    """KTI chapter enumeration for research traceability coverage."""

    BAB_1 = "BAB_1"  # Pendahuluan
    BAB_2 = "BAB_2"  # Tinjauan Pustaka
    BAB_3 = "BAB_3"  # Metodologi Penelitian
    BAB_4 = "BAB_4"  # Hasil dan Pembahasan
    BAB_5 = "BAB_5"  # Kesimpulan dan Saran


class DocumentMode(str, Enum):
    """Target output document mode."""

    A4_PORTRAIT = "a4-portrait"
    A4_LANDSCAPE = "a4-landscape"
    A4_TUTORIAL = "a4-tutorial"
    PRESENTATION_16_9 = "presentation-16-9"



class VisualIntent(str, Enum):
    """Semantic visual intent for a ContentUnit.

    Does NOT map directly to CSS or design components — only
    represents what type of visual treatment the content suggests.
    """

    TEXT_FOCUSED = "text_focused"
    HIERARCHICAL = "hierarchical"
    SEQUENTIAL = "sequential"
    COMPARATIVE = "comparative"
    PROCESS_FLOW = "process_flow"
    DATA_TREND = "data_trend"
    DATA_COMPARISON = "data_comparison"
    DATA_DISTRIBUTION = "data_distribution"
    RELATIONSHIP = "relationship"
    CAUSE_EFFECT = "cause_effect"
    TIMELINE = "timeline"
    CHECKLIST = "checklist"
    STEP_BY_STEP = "step_by_step"
    EVIDENCE_GALLERY = "evidence_gallery"
    QUOTE_HIGHLIGHT = "quote_highlight"
    KEY_MESSAGE = "key_message"
    SUMMARY = "summary"
    DECISION = "decision"
    REFERENCE = "reference"


class VisualizationPurpose(str, Enum):
    """Semantic purpose of a proposed visualization."""

    TREND = "trend"
    COMPARISON = "comparison"
    DISTRIBUTION = "distribution"
    RELATIONSHIP = "relationship"
    COMPOSITION = "composition"
    PROCESS = "process"
    SEQUENCE = "sequence"
    HIERARCHY = "hierarchy"
    EVIDENCE = "evidence"
    MEASUREMENT = "measurement"


class ContentDensity(str, Enum):
    """Estimated information density of a content group."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    OVERLOADED = "overloaded"


class ConfidenceLevel(str, Enum):
    """Confidence level of an AI-derived result."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class RelationshipType(str, Enum):
    """Semantic relationship between two ContentUnits."""

    ADDRESSES = "addresses"
    SUPPORTS = "supports"
    DERIVED_FROM = "derived_from"
    MEASURED_BY = "measured_by"
    PRODUCED_BY = "produced_by"
    ANALYZED_BY = "analyzed_by"
    INTERPRETS = "interprets"
    COMPARES_WITH = "compares_with"
    CONNECTED_TO = "connected_to"
    ANSWERS = "answers"
    CONCLUDES_FROM = "concludes_from"
    BASED_ON = "based_on"
    RECOMMENDS = "recommends"
    EXTENDS = "extends"
    LIMITS = "limits"


class BlueprintCandidateType(str, Enum):
    """Semantic blueprint candidate type.

    This is design-independent — it does NOT map to HTML/CSS components.
    The design batch will map these to concrete page types.
    """

    TITLE_BLOCK = "title_block"
    SECTION_INTRODUCTION = "section_introduction"
    CONCEPT_EXPLANATION = "concept_explanation"
    PROCESS_SEQUENCE = "process_sequence"
    COMPARISON_BLOCK = "comparison_block"
    DATA_EVIDENCE_BLOCK = "data_evidence_block"
    RESEARCH_RESULT_BLOCK = "research_result_block"
    DISCUSSION_BLOCK = "discussion_block"
    THEORY_CONNECTION_BLOCK = "theory_connection_block"
    KEY_FINDING_BLOCK = "key_finding_block"
    CONCLUSION_BLOCK = "conclusion_block"
    RECOMMENDATION_BLOCK = "recommendation_block"
    SUMMARY_BLOCK = "summary_block"
    REFERENCE_BLOCK = "reference_block"
    GENERIC_CONTENT = "generic_content"


class TraceabilityWarning(str, Enum):
    """Known traceability warning types for research documents."""

    FINDING_WITHOUT_INTERPRETATION = "FINDING_WITHOUT_INTERPRETATION"
    DATA_WITHOUT_FINDING = "DATA_WITHOUT_FINDING"
    CONCLUSION_WITHOUT_OBJECTIVE_TRACE = "CONCLUSION_WITHOUT_OBJECTIVE_TRACE"
    RECOMMENDATION_WITHOUT_BASIS = "RECOMMENDATION_WITHOUT_BASIS"
    HYPOTHESIS_WITHOUT_EVALUATION = "HYPOTHESIS_WITHOUT_EVALUATION"
    MISSING_BAB_COVERAGE = "MISSING_BAB_COVERAGE"
    INTERPRETATION_WITHOUT_SOURCE = "INTERPRETATION_WITHOUT_SOURCE"
    DISCUSSION_WITHOUT_THEORY = "DISCUSSION_WITHOUT_THEORY"


class FailureCategory(str, Enum):
    """Pipeline failure categories for logging and recovery routing."""

    INPUT_FAILURE = "input_failure"
    NORMALIZATION_FAILURE = "normalization_failure"
    SEGMENTATION_FAILURE = "segmentation_failure"
    CLASSIFICATION_FAILURE = "classification_failure"
    STRUCTURED_OUTPUT_FAILURE = "structured_output_failure"
    RELATIONSHIP_CONFLICT = "relationship_conflict"
    MODEL_TIMEOUT = "model_timeout"
    MODEL_UNAVAILABLE = "model_unavailable"
    LOW_CONFIDENCE = "low_confidence"
    SOURCE_FIDELITY_RISK = "source_fidelity_risk"
    BLUEPRINT_INCONSISTENCY = "blueprint_inconsistency"


# ══════════════════════════════════════════════════════════════════════════════
# CORE CONTENT UNIT
# ══════════════════════════════════════════════════════════════════════════════


class ContentUnit(BaseModel):
    """Atomic unit of information extracted from source material.

    A ContentUnit represents the smallest independently meaningful
    piece of content. It preserves the original order, parent
    relationship, and raw text alongside the classified semantic role.

    Fields
    ------
    unit_id : str
        UUID v4 identifier. Auto-generated if not provided.
    source_order : int
        Zero-based index of this unit in the original document.
    parent_id : str | None
        unit_id of the parent unit (e.g., section → subsection).
    raw_text : str
        Original text exactly as extracted from source (not modified).
    normalized_text : str
        Cleaned version of raw_text after whitespace normalization.
    title : str | None
        Heading or label associated with this unit, if any.
    depth : int
        Nesting depth (0 = top-level, 1 = section, 2 = subsection, etc.).
    content_type : ContentType
        Primary semantic classification.
    research_role : ContentType | None
        Specific KTI research role if document_genre is RESEARCH_REPORT.
    kti_bab : KtiBab | None
        BAB this unit belongs to (only for RESEARCH_REPORT genre).
    is_core_component : bool
        Whether this is a CORE (required) KTI component.
    density_score : float
        Estimated information density [0.0, 1.0].
    word_count : int
        Word count of normalized_text.
    metadata : dict[str, Any]
        Additional metadata (source format, page hint, etc.).
    """

    unit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_order: int = Field(default=0, ge=0)
    parent_id: str | None = None
    raw_text: str
    normalized_text: str
    title: str | None = None
    source_heading: str | None = None
    depth: int = Field(default=0, ge=0)
    content_type: ContentType = ContentType.OTHER
    research_role: ContentType | None = None
    kti_bab: KtiBab | None = None
    is_core_component: bool = False
    density_score: float = Field(default=0.5, ge=0.0, le=1.0)
    word_count: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("raw_text")
    @classmethod
    def raw_text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("raw_text must not be empty after stripping whitespace")
        return v

    @model_validator(mode="after")
    def compute_word_count(self) -> ContentUnit:
        if self.word_count == 0 and self.normalized_text:
            self.word_count = len(self.normalized_text.split())
        return self


# ══════════════════════════════════════════════════════════════════════════════
# RELATIONSHIP
# ══════════════════════════════════════════════════════════════════════════════


class ContentRelationship(BaseModel):
    """Directed semantic relationship between two ContentUnits.

    Fields
    ------
    source_unit_id : str
        unit_id of the source ContentUnit.
    target_unit_id : str
        unit_id of the target ContentUnit.
    relationship_type : RelationshipType
        The semantic relationship label.
    confidence : ConfidenceLevel
        Confidence of the detected relationship.
    is_required : bool
        Whether this relationship is required for traceability validity.
    notes : str | None
        Optional explanation of the relationship.
    """

    source_unit_id: str
    target_unit_id: str
    relationship_type: RelationshipType
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    is_required: bool = False
    notes: str | None = None


# ══════════════════════════════════════════════════════════════════════════════
# IMPORTANCE SCORING
# ══════════════════════════════════════════════════════════════════════════════


class ImportanceScore(BaseModel):
    """Importance score for a ContentUnit.

    Purpose: estimate presentation importance, NOT scientific truth.

    Factors
    -------
    structural_score : float
        Weight from document position and heading level.
    semantic_score : float
        Weight from content type significance in the document genre.
    relationship_score : float
        Weight from how many other units depend on this one.
    evidence_score : float
        Weight from the presence of evidence, data, or citations.
    emphasis_score : float
        Weight from user-provided emphasis signals (caps, bold, markers).
    final_score : float
        Weighted combination of all factors [0.0, 1.0].
    confidence : ConfidenceLevel
        Confidence in this score.
    reasons : list[str]
        Human-readable explanations for the assigned score.
    """

    structural_score: float = Field(ge=0.0, le=1.0)
    semantic_score: float = Field(ge=0.0, le=1.0)
    relationship_score: float = Field(ge=0.0, le=1.0)
    evidence_score: float = Field(ge=0.0, le=1.0)
    emphasis_score: float = Field(ge=0.0, le=1.0)
    final_score: float = Field(ge=0.0, le=1.0)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    reasons: list[str] = Field(default_factory=list)


# ══════════════════════════════════════════════════════════════════════════════
# VISUAL INTENT RESULT
# ══════════════════════════════════════════════════════════════════════════════


class VisualizationCandidate(BaseModel):
    """A proposed visualization for a ContentUnit or group of units.

    This is a semantic proposal only — no chart library, CSS, or
    rendering decision is made here.

    Fields
    ------
    purpose : VisualizationPurpose
        The semantic reason for visualizing this data.
    data_description : str
        Description of what data would be visualized.
    is_data_visualization : bool
        True if this is a data visualization; False if decorative.
    source_unit_ids : list[str]
        unit_ids that provide the data for this visualization.
    """

    purpose: VisualizationPurpose
    data_description: str
    is_data_visualization: bool = True
    source_unit_ids: list[str] = Field(default_factory=list)


class VisualIntentResult(BaseModel):
    """Visual intent classification for a ContentUnit.

    Fields
    ------
    unit_id : str
        The ContentUnit this result applies to.
    primary_intent : VisualIntent
        The most appropriate visual treatment.
    secondary_intents : list[VisualIntent]
        Additional visual treatments that may apply.
    confidence : ConfidenceLevel
        Confidence in the primary intent classification.
    reasons : list[str]
        Explanations for the assigned intents.
    visualization_candidate : VisualizationCandidate | None
        If data visualization is appropriate, the candidate details.
    """

    unit_id: str
    primary_intent: VisualIntent = VisualIntent.TEXT_FOCUSED
    secondary_intents: list[VisualIntent] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    reasons: list[str] = Field(default_factory=list)
    visualization_candidate: VisualizationCandidate | None = None


# ══════════════════════════════════════════════════════════════════════════════
# RESEARCH TRACEABILITY
# ══════════════════════════════════════════════════════════════════════════════


class ResearchTraceability(BaseModel):
    """Research traceability map for RESEARCH_REPORT documents.

    Represents which critical research components were detected
    and flags missing or broken traceability links.

    Fields
    ------
    has_research_problem : bool
    has_research_question : bool
    has_research_objective : bool
    has_hypothesis : bool
    has_theoretical_foundation : bool
    has_prior_research : bool
    has_research_method : bool
    has_results : bool
    has_discussion : bool
    has_conclusion : bool
    has_recommendation : bool
    detected_bab_coverage : list[KtiBab]
        BABs detected in source material.
    missing_critical_components : list[str]
        CORE components not detected.
    traceability_warnings : list[TraceabilityWarning]
        Known broken traceability patterns.
    conclusion_traces : list[ConclusionTrace]
        Maps each conclusion unit to the question/objective it answers.
    recommendation_bases : list[RecommendationBasis]
        Maps each recommendation to its supporting finding/limitation.
    """

    has_research_problem: bool = False
    has_research_question: bool = False
    has_research_objective: bool = False
    has_hypothesis: bool = False
    has_theoretical_foundation: bool = False
    has_prior_research: bool = False
    has_research_method: bool = False
    has_results: bool = False
    has_discussion: bool = False
    has_conclusion: bool = False
    has_recommendation: bool = False
    detected_bab_coverage: list[KtiBab] = Field(default_factory=list)
    missing_critical_components: list[str] = Field(default_factory=list)
    traceability_warnings: list[TraceabilityWarning] = Field(default_factory=list)
    conclusion_traces: list[ConclusionTrace] = Field(default_factory=list)
    recommendation_bases: list[RecommendationBasis] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_bab_coverage(self) -> ResearchTraceability:
        if (
            self.has_results
            and not self.has_conclusion
            and TraceabilityWarning.MISSING_BAB_COVERAGE not in self.traceability_warnings
        ):
            self.traceability_warnings.append(TraceabilityWarning.MISSING_BAB_COVERAGE)
        return self


class ConclusionTrace(BaseModel):
    """Maps a conclusion unit to the research question/objective it answers."""

    conclusion_unit_id: str
    answers_question_unit_id: str | None = None
    achieves_objective_unit_id: str | None = None
    based_on_finding_unit_ids: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


class RecommendationBasis(BaseModel):
    """Maps a recommendation to its supporting evidence."""

    recommendation_unit_id: str
    based_on_finding_unit_ids: list[str] = Field(default_factory=list)
    based_on_limitation_unit_ids: list[str] = Field(default_factory=list)
    based_on_implication_unit_ids: list[str] = Field(default_factory=list)
    is_grounded: bool = False  # True if at least one basis exists
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS RESULT
# ══════════════════════════════════════════════════════════════════════════════


class AnalysisResult(BaseModel):
    """Complete output of the Content Intelligence pipeline.

    This is the primary structured contract passed from
    Content Intelligence to the Document Planner agent.

    Fields
    ------
    schema_version : str
        Schema version identifier. Current: "2.0".
    job_id : str
        UUID of the pipeline job that produced this result.
    source_file : str
        Relative path or identifier of the source input.
    content_units : list[ContentUnit]
        All extracted and classified content units.
    relationships : list[ContentRelationship]
        Detected semantic relationships between units.
    importance_scores : dict[str, ImportanceScore]
        Keyed by unit_id.
    visual_intents : dict[str, VisualIntentResult]
        Keyed by unit_id.
    total_word_count : int
        Total word count across all units.
    dominant_content_type : ContentType
        The most frequently occurring content type.
    complexity_score : float
        Estimated complexity of the source material [0.0, 1.0].
    recommended_mode : DocumentMode
        Suggested output mode based on content analysis.
    document_genre : DocumentGenre
        Detected genre of the source document.
    research_traceability : ResearchTraceability | None
        Populated only when document_genre == RESEARCH_REPORT.
    degraded_mode : bool
        True if pipeline ran in degraded/fallback mode.
    fallback_used : str | None
        Name of the fallback provider used, if any.
    pipeline_warnings : list[str]
        Non-fatal warnings accumulated during processing.
    analyzed_at : str
        ISO-8601 timestamp of analysis completion.
    """

    schema_version: str = "2.0"
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_file: str
    content_units: list[ContentUnit] = Field(default_factory=list)
    relationships: list[ContentRelationship] = Field(default_factory=list)
    importance_scores: dict[str, ImportanceScore] = Field(default_factory=dict)
    visual_intents: dict[str, VisualIntentResult] = Field(default_factory=dict)
    total_word_count: int = Field(default=0, ge=0)
    dominant_content_type: ContentType = ContentType.OTHER
    complexity_score: float = Field(default=0.5, ge=0.0, le=1.0)
    recommended_mode: DocumentMode = DocumentMode.A4_TUTORIAL
    document_genre: DocumentGenre = DocumentGenre.GENERAL
    research_traceability: ResearchTraceability | None = None
    degraded_mode: bool = False
    fallback_used: str | None = None
    pipeline_warnings: list[str] = Field(default_factory=list)
    analyzed_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )

    @field_validator("content_units")
    @classmethod
    def units_not_empty_in_production(cls, v: list[ContentUnit]) -> list[ContentUnit]:
        # Allow empty during pipeline construction, enforce at boundary
        return v

    @model_validator(mode="after")
    def compute_totals(self) -> AnalysisResult:
        if self.content_units and self.total_word_count == 0:
            self.total_word_count = sum(u.word_count for u in self.content_units)
        return self


# ══════════════════════════════════════════════════════════════════════════════
# BLUEPRINT PROPOSAL
# ══════════════════════════════════════════════════════════════════════════════


class ContentGroup(BaseModel):
    """A semantically coherent group of ContentUnits.

    Groups are formed by semantic continuity, topic similarity,
    or research relationship — not by text length alone.
    """

    group_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str | None = None
    unit_ids: list[str] = Field(default_factory=list)
    blueprint_candidate: BlueprintCandidateType = BlueprintCandidateType.GENERIC_CONTENT
    primary_visual_intent: VisualIntent = VisualIntent.TEXT_FOCUSED
    density: ContentDensity = ContentDensity.MEDIUM
    importance_rank: int = Field(default=0, ge=0)
    continuation_required: bool = False
    previous_group_dependency: str | None = None
    next_group_dependency: str | None = None
    standalone_allowed: bool = True
    kti_bab: KtiBab | None = None
    notes: str | None = None


class BlueprintProposal(BaseModel):
    """Blueprint-ready content model produced by the Content-to-Blueprint algorithm.

    This is the primary output of Batch 2 and the primary input to
    Batch 3 (Design System + Page Composition).

    It is deliberately design-independent: no CSS, no page coordinates,
    no component implementations.

    Fields
    ------
    proposal_id : str
        UUID of this proposal.
    source_analysis_id : str
        job_id of the AnalysisResult that produced this.
    document_title : str
        Proposed document title.
    document_genre : DocumentGenre
        Genre of the source document.
    recommended_mode : DocumentMode
        Recommended output mode.
    content_groups : list[ContentGroup]
        Ordered sequence of content groups ready for page assignment.
    total_estimated_density : ContentDensity
        Overall content density estimate.
    research_traceability : ResearchTraceability | None
        Preserved from AnalysisResult for BAB validation in design layer.
    traceability_warnings : list[str]
        Any broken traceability chains detected during proposal.
    blueprint_warnings : list[str]
        Structural or density warnings for the design layer.
    proposed_at : str
        ISO-8601 timestamp.
    """

    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_analysis_id: str
    document_title: str
    document_genre: DocumentGenre = DocumentGenre.GENERAL
    recommended_mode: DocumentMode = DocumentMode.A4_TUTORIAL
    content_groups: list[ContentGroup] = Field(default_factory=list)
    total_estimated_density: ContentDensity = ContentDensity.MEDIUM
    research_traceability: ResearchTraceability | None = None
    traceability_warnings: list[str] = Field(default_factory=list)
    blueprint_warnings: list[str] = Field(default_factory=list)
    proposed_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE JOB STATE
# ══════════════════════════════════════════════════════════════════════════════


class JobState(str, Enum):
    """State of a pipeline job."""

    PENDING = "pending"
    RUNNING = "running"
    DEGRADED = "degraded"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineJob(BaseModel):
    """Represents an active or completed intelligence pipeline job."""

    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_file: str
    document_mode: DocumentMode
    state: JobState = JobState.PENDING
    failure_category: FailureCategory | None = None
    failure_message: str | None = None
    analysis_result: AnalysisResult | None = None
    blueprint_proposal: BlueprintProposal | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str | None = None


# ══════════════════════════════════════════════════════════════════════════════
# STRUCTURED AI OUTPUT CONTRACTS
# ══════════════════════════════════════════════════════════════════════════════


class AIClassificationOutput(BaseModel):
    """Structured output contract for the semantic classification agent.

    The LLM must produce JSON conforming to this schema.
    All fields are validated before entering the pipeline.
    """

    unit_id: str
    content_type: ContentType
    research_role: ContentType | None = None
    kti_bab: KtiBab | None = None
    is_core_component: bool = False
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    reasons: list[str] = Field(default_factory=list)
    source_fidelity_flags: list[str] = Field(default_factory=list)


class AIRelationshipOutput(BaseModel):
    """Structured output contract for the relationship extraction agent."""

    relationships: list[ContentRelationship] = Field(default_factory=list)
    extraction_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    notes: str | None = None


class AIVisualIntentOutput(BaseModel):
    """Structured output contract for the visual intent detection agent."""

    intents: list[VisualIntentResult] = Field(default_factory=list)
    detection_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


class AIDocumentPlanOutput(BaseModel):
    """Structured output contract for the document planner agent."""

    document_title: str
    document_genre: DocumentGenre
    recommended_mode: DocumentMode
    content_groups: list[ContentGroup] = Field(default_factory=list)
    planning_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    planning_notes: str | None = None


class AIQualityCritiqueOutput(BaseModel):
    """Structured output contract for the quality critic agent."""

    is_acceptable: bool
    critical_issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    overall_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    requires_revision: bool = False


# ══════════════════════════════════════════════════════════════════════════════
# HUMAN OVERRIDE CONTRACT
# ══════════════════════════════════════════════════════════════════════════════


class HumanOverride(BaseModel):
    """Records a human correction to an AI-derived classification.

    Preserves both the original AI result and the override,
    with the source of the override for audit.

    This contract does not implement UI — it only defines
    the data structure for future override support.
    """

    unit_id: str
    override_field: str  # e.g. "content_type", "research_role", "visual_intent"
    original_ai_value: str
    override_value: str
    override_source: str  # e.g. "user:manual", "system:repair", "rule:fidelity"
    override_reason: str | None = None
    overridden_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
