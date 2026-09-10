"""
Universal Knowledge Core — 9-Stage Compilation Pipeline Package.
"""

from app.intelligence.pipeline.structural_extractor import StructuralExtractor, StructuralSection, StructuralTree
from app.intelligence.pipeline.unit_normalizer import CandidateUnit, UnitNormalizer
from app.intelligence.pipeline.local_classifier import LocalClassifier, RuleClassifiedUnit
from app.intelligence.pipeline.ambiguity_resolver import (
    AmbiguityResolver,
    OfflineMockResolutionProvider,
    ResolvedUnit,
    SemanticResolutionProvider,
)
from app.intelligence.pipeline.payload_builder import PayloadBuilder
from app.intelligence.pipeline.claim_evidence_extractor import ClaimEvidenceAssociations, ClaimEvidenceExtractor
from app.intelligence.pipeline.relationship_inferencer import RelationshipInferencer
from app.intelligence.pipeline.importance_analyzer import ImportanceAnalyzer
from app.intelligence.pipeline.manifest_assembler import ManifestAssembler, ManifestAssemblyError
from app.intelligence.pipeline.compiler import KnowledgeCompiler

__all__ = [
    "StructuralExtractor",
    "StructuralSection",
    "StructuralTree",
    "CandidateUnit",
    "UnitNormalizer",
    "LocalClassifier",
    "RuleClassifiedUnit",
    "AmbiguityResolver",
    "OfflineMockResolutionProvider",
    "ResolvedUnit",
    "SemanticResolutionProvider",
    "PayloadBuilder",
    "ClaimEvidenceExtractor",
    "ClaimEvidenceAssociations",
    "RelationshipInferencer",
    "ImportanceAnalyzer",
    "ManifestAssembler",
    "ManifestAssemblyError",
    "KnowledgeCompiler",
]
