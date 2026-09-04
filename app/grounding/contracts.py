"""
Authoritative typed contracts and data models for Knowledge Grounding & Evidence Intelligence.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ══════════════════════════════════════════════════════════════════════════════


class KnowledgeSourceType(str, Enum):
    """Origin category of the knowledge asset."""
    LOCAL_DOCUMENT = "local_document"
    STRUCTURED_DATASET = "structured_dataset"
    ACADEMIC_PAPER = "academic_paper"
    TEXTBOOK = "textbook"
    INTERNAL_KNOWLEDGE = "internal_knowledge"
    VECTOR_STORE = "vector_store"
    WEB_SOURCE = "web_source"
    API_SOURCE = "api_source"
    MANUAL_REFERENCE = "manual_reference"
    GENERATED_REFERENCE = "generated_reference"


class SourceAuthority(str, Enum):
    """Authority and epistemic trustworthiness of the source."""
    PRIMARY = "primary"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class EvidenceType(str, Enum):
    """Cognitive or empirical form of the evidence snippet."""
    DIRECT_STATEMENT = "direct_statement"
    DEFINITION = "definition"
    EXPLANATION = "explanation"
    DATA_POINT = "data_point"
    EXPERIMENT_RESULT = "experiment_result"
    DERIVATION = "derivation"
    EXAMPLE = "example"
    STATISTICAL_RESULT = "statistical_result"
    METHODOLOGY = "methodology"
    THEORETICAL_MODEL = "theoretical_model"


class ClaimType(str, Enum):
    """Categorical type of assertion requiring potential grounding."""
    FACTUAL = "factual"
    DEFINITIONAL = "definitional"
    CAUSAL = "causal"
    QUANTITATIVE = "quantitative"
    PROCEDURAL = "procedural"
    INTERPRETIVE = "interpretive"
    PEDAGOGICAL = "pedagogical"
    COMPARATIVE = "comparative"


class SupportRelation(str, Enum):
    """Logical relationship between a claim and retrieved evidence."""
    SUPPORTS = "supports"
    PARTIALLY_SUPPORTS = "partially_supports"
    CONTRADICTS = "contradicts"
    RELATED = "related"
    INSUFFICIENT = "insufficient"
    UNKNOWN = "unknown"


class GroundingStatus(str, Enum):
    """Grounding state of a claim or document."""
    GROUNDED = "grounded"
    PARTIALLY_GROUNDED = "partially_grounded"
    UNGROUNDED = "ungrounded"
    CONTRADICTED = "contradicted"
    NOT_REQUIRED = "not_required"


class FreshnessStatus(str, Enum):
    """Temporal validity of the knowledge."""
    CURRENT = "current"
    STALE = "stale"
    UNKNOWN = "unknown"
    TIME_INSENSITIVE = "time_insensitive"


# ══════════════════════════════════════════════════════════════════════════════
# CORE DATA CONTRACTS
# ══════════════════════════════════════════════════════════════════════════════


class KnowledgeSource(BaseModel):
    """High-level knowledge container metadata."""
    source_id: str
    source_type: KnowledgeSourceType = KnowledgeSourceType.LOCAL_DOCUMENT
    title: str
    authority: SourceAuthority = SourceAuthority.HIGH
    domain: str = "general"
    publisher: str = ""
    authors: list[str] = Field(default_factory=list)
    publication_date: str = ""
    access_date: str = ""
    version: str = "1.0"
    uri: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeDocument(BaseModel):
    """A document containing structured or unformatted textual knowledge."""
    document_id: str
    source_id: str
    title: str
    content: str
    domain: str = "general"
    language: str = "en"
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeChunk(BaseModel):
    """A segment or passage extracted from a KnowledgeDocument."""
    chunk_id: str
    document_id: str
    source_id: str
    content: str
    position: int = 0
    section: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    """An atomic snippet of retrieved evidence with epistemic properties."""
    evidence_id: str
    source_id: str
    chunk_id: str | None = None
    evidence_type: EvidenceType = EvidenceType.DIRECT_STATEMENT
    content: str
    authority: SourceAuthority = SourceAuthority.HIGH
    relevance_score: float = 1.0
    freshness: FreshnessStatus = FreshnessStatus.TIME_INSENSITIVE
    domain: str = "general"
    metadata: dict[str, Any] = Field(default_factory=dict)


class Claim(BaseModel):
    """An explicit semantic assertion extracted from the material."""
    claim_id: str
    content: str
    claim_type: ClaimType = ClaimType.FACTUAL
    importance: float = 1.0  # 0.0 (decorative) to 1.0 (core foundational)
    source_location: str = ""  # blueprint/block id
    domain: str = "general"
    requires_grounding: bool = True
    grounding_status: GroundingStatus = GroundingStatus.UNGROUNDED


class ClaimEvidenceLink(BaseModel):
    """A verified link between an asserted claim and supporting/contradicting evidence."""
    claim_id: str
    evidence_id: str
    relation: SupportRelation = SupportRelation.SUPPORTS
    support_score: float = 1.0
    semantic_similarity: float = 1.0
    explanation: str = ""


class CitationProvenance(BaseModel):
    """Machine-readable traceability chain linking Claim -> Evidence -> Document -> Source."""
    citation_id: str
    claim_id: str
    evidence_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    trace_path: str = ""


class GroundingScore(BaseModel):
    """Multi-dimensional explainable grounding score."""
    coverage: float = Field(ge=0.0, le=1.0)
    support_strength: float = Field(ge=0.0, le=1.0)
    authority: float = Field(ge=0.0, le=1.0)
    freshness: float = Field(ge=0.0, le=1.0)
    consistency: float = Field(ge=0.0, le=1.0)
    overall_score: float = Field(ge=0.0, le=1.0)


class GroundingFinding(BaseModel):
    """Diagnostic issue or validation warning identified during grounding evaluation."""
    severity: str = "warning"  # info, warning, error, critical
    category: str = "unsupported_claim"  # unsupported_claim, contradiction, low_authority, stale
    message: str
    claim_id: str | None = None
    evidence_id: str | None = None
    recommendation: str = ""


class GroundingTrace(BaseModel):
    """Explainability record capturing retrieval and linking decisions."""
    trace_id: str
    query: str = ""
    sources_considered: list[str] = Field(default_factory=list)
    evidence_candidates_count: int = 0
    evidence_selected_count: int = 0
    claims_analyzed: int = 0
    links_created: int = 0
    decisions: list[str] = Field(default_factory=list)
    timestamps: dict[str, str] = Field(default_factory=dict)


class GroundingReport(BaseModel):
    """Authoritative diagnostic report emitted by KnowledgeGroundingEngine."""
    claims_total: int = 0
    claims_grounded: int = 0
    claims_partial: int = 0
    claims_unsupported: int = 0
    claims_contradicted: int = 0
    score: GroundingScore
    findings: list[GroundingFinding] = Field(default_factory=list)
    trace: GroundingTrace


class GroundedMaterialContext(BaseModel):
    """Complete grounded artifact bundle ready for downstream consumption."""
    material_id: str
    claims: list[Claim] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    links: list[ClaimEvidenceLink] = Field(default_factory=list)
    citations: list[CitationProvenance] = Field(default_factory=list)
    report: GroundingReport
