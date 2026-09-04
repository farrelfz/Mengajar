"""
Knowledge Grounding & Evidence Intelligence Package Exports.
"""

from app.grounding.claims import ClaimExtractor, HeuristicClaimExtractor
from app.grounding.consistency import ContradictionDetector
from app.grounding.contracts import (
    CitationProvenance,
    Claim,
    ClaimEvidenceLink,
    ClaimType,
    Evidence,
    EvidenceType,
    FreshnessStatus,
    GroundedMaterialContext,
    GroundingFinding,
    GroundingReport,
    GroundingScore,
    GroundingStatus,
    GroundingTrace,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeSource,
    KnowledgeSourceType,
    SourceAuthority,
    SupportRelation,
)
from app.grounding.engine import KnowledgeGroundingEngine
from app.grounding.evidence_ranker import EvidenceRanker
from app.grounding.graph import EvidenceGraph
from app.grounding.linker import ClaimEvidenceLinker
from app.grounding.policies import DomainGroundingPolicy, DomainGroundingPolicyRegistry
from app.grounding.provenance import ProvenanceTracer
from app.grounding.providers import (
    InMemoryKnowledgeProvider,
    KnowledgeProvider,
    KnowledgeProviderRegistry,
    KnowledgeQuery,
    LocalDocumentKnowledgeProvider,
)
from app.grounding.retrieval import RetrievalEngine, RetrievedEvidence
from app.grounding.scoring import GroundingScoreCalculator
from app.grounding.source_evaluator import DomainAwareFreshnessPolicy, SourceAuthorityEvaluator
from app.grounding.trace import GroundingTraceAuditor
from app.grounding.unsupported import UnsupportedClaimDetector

__all__ = [
    "KnowledgeSourceType",
    "SourceAuthority",
    "EvidenceType",
    "ClaimType",
    "SupportRelation",
    "GroundingStatus",
    "FreshnessStatus",
    "KnowledgeSource",
    "KnowledgeDocument",
    "KnowledgeChunk",
    "Evidence",
    "Claim",
    "ClaimEvidenceLink",
    "CitationProvenance",
    "GroundingScore",
    "GroundingFinding",
    "GroundingTrace",
    "GroundingReport",
    "GroundedMaterialContext",
    "KnowledgeProvider",
    "KnowledgeQuery",
    "InMemoryKnowledgeProvider",
    "LocalDocumentKnowledgeProvider",
    "KnowledgeProviderRegistry",
    "RetrievalEngine",
    "RetrievedEvidence",
    "ClaimExtractor",
    "HeuristicClaimExtractor",
    "EvidenceRanker",
    "ContradictionDetector",
    "ClaimEvidenceLinker",
    "SourceAuthorityEvaluator",
    "DomainAwareFreshnessPolicy",
    "UnsupportedClaimDetector",
    "GroundingScoreCalculator",
    "DomainGroundingPolicy",
    "DomainGroundingPolicyRegistry",
    "ProvenanceTracer",
    "EvidenceGraph",
    "KnowledgeGroundingEngine",
    "GroundingTraceAuditor",
]
