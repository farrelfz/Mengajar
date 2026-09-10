"""
Universal Document Intelligence System V5 — Golden Benchmark Contracts.

Phase 5: Immutable, machine-readable contracts governing the Golden Corpus,
benchmark references, invariant models, expected characteristics, forbidden failures,
adversarial variants, and certification policies.
"""

from __future__ import annotations

import hashlib
import time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field


class VariationPolicy(str, Enum):
    """Explicit model of acceptable variation from the golden reference."""
    EXACT = "EXACT"
    TOLERANT = "TOLERANT"
    FUNCTIONAL_EQUIVALENCE = "FUNCTIONAL_EQUIVALENCE"
    OPEN_VARIATION = "OPEN_VARIATION"


class CertificationStatus(str, Enum):
    """Lifecycle status of a golden artifact reference."""
    DRAFT = "DRAFT"
    CURATED = "CURATED"
    REVIEWED = "REVIEWED"
    CERTIFIED = "CERTIFIED"
    DEPRECATED = "DEPRECATED"


class CertificationDecision(str, Enum):
    """Outcomes of a benchmark evaluation certification."""
    CERTIFIED_EXCELLENT = "CERTIFIED_EXCELLENT"
    CERTIFIED_ACCEPTABLE = "CERTIFIED_ACCEPTABLE"
    CERTIFIED_WITH_WARNINGS = "CERTIFIED_WITH_WARNINGS"
    BENCHMARK_REGRESSION = "BENCHMARK_REGRESSION"
    BENCHMARK_INSUFFICIENT = "BENCHMARK_INSUFFICIENT"
    MANUAL_BENCHMARK_REVIEW_REQUIRED = "MANUAL_BENCHMARK_REVIEW_REQUIRED"


class ExpectedInvariants(BaseModel):
    """Binary hard invariants that must not be violated."""
    model_config = ConfigDict(frozen=True)

    no_fabricated_claims: bool = True
    no_unsupported_evidence: bool = True
    no_traceability_break: bool = True
    no_text_clipping: bool = True
    no_element_collision: bool = True
    artifact_type_preserved: bool = True
    source_grounding_preserved: bool = True
    no_answer_leak: bool = True  # specific to Worksheet
    citation_integrity_preserved: bool = True  # specific to Scientific


class ExpectedCharacteristics(BaseModel):
    """Structured architectural expectations that distinguish quality without pixel locking."""
    model_config = ConfigDict(frozen=True)

    must_have: Tuple[str, ...] = Field(default_factory=tuple)
    must_not_have: Tuple[str, ...] = Field(default_factory=tuple)
    preferred: Tuple[str, ...] = Field(default_factory=tuple)
    acceptable_variation: Tuple[str, ...] = Field(default_factory=tuple)


class ForbiddenFailures(BaseModel):
    """Canonical failure codes forbidden for this artifact reference."""
    model_config = ConfigDict(frozen=True)

    forbidden_failure_codes: Tuple[str, ...] = Field(default_factory=tuple)


class AdversarialVariant(BaseModel):
    """A paired adversarial mutant fixture proving validator sensitivity."""
    model_config = ConfigDict(frozen=True)

    variant_id: str
    artifact_type: str
    mutation_type: str
    expected_failure_code: str
    description: str = ""
    payload: Dict[str, Any] = Field(default_factory=dict)


class GoldenArtifactReference(BaseModel):
    """A benchmark reference for a specific artifact type within a Golden Case."""
    model_config = ConfigDict(frozen=True)

    artifact_id: str
    artifact_type: str
    source_case_id: str
    
    artifact_file_reference: str
    
    semantic_expectations: Dict[str, Any] = Field(default_factory=dict)
    structural_expectations: Dict[str, Any] = Field(default_factory=dict)
    visual_expectations: Dict[str, Any] = Field(default_factory=dict)
    pedagogical_expectations: Dict[str, Any] = Field(default_factory=dict)
    scientific_expectations: Dict[str, Any] = Field(default_factory=dict)
    
    hard_invariants: ExpectedInvariants = Field(default_factory=ExpectedInvariants)
    acceptable_variations: Dict[str, VariationPolicy] = Field(default_factory=dict)
    quality_annotations: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Phase 5 Extensions
    expected_characteristics: Optional[ExpectedCharacteristics] = None
    forbidden_failures: Optional[ForbiddenFailures] = None
    adversarial_variants: List[AdversarialVariant] = Field(default_factory=list)
    
    reference_provenance: str = ""
    created_at: float = Field(default_factory=time.time)
    version: str = "1.0.0"
    review_status: CertificationStatus = CertificationStatus.DRAFT


class GoldenCase(BaseModel):
    """A complete benchmark case comprising source material and its references."""
    model_config = ConfigDict(frozen=True)

    case_id: str
    source_path: str
    source_hash: str
    corpus_category: str
    difficulty_level: str
    
    references: Dict[str, GoldenArtifactReference] = Field(default_factory=dict)
    
    # Phase 5 Extensions
    taxonomy_category: Optional[str] = None
    adversarial_cases: Dict[str, Any] = Field(default_factory=dict)
    

class GoldenCorpusVersion(BaseModel):
    """Immutable version tracking for the Golden Corpus."""
    model_config = ConfigDict(frozen=True)

    version: str
    parent_version: Optional[str] = None
    change_summary: str = ""
    created_at: float = Field(default_factory=time.time)
    created_by: str = ""
    review_provenance: str = ""
    content_digest: str = ""


class GoldenCorpus(BaseModel):
    """The root of the Golden Corpus."""
    model_config = ConfigDict(frozen=True)

    corpus_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    cases: Dict[str, GoldenCase] = Field(default_factory=dict)
    current_version: GoldenCorpusVersion


class DimensionResult(BaseModel):
    """Result of evaluating a specific quality dimension against the golden reference."""
    model_config = ConfigDict(frozen=True)

    dimension: str
    raw_measurements: Dict[str, Any]
    normalized_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    applicability: float = Field(ge=0.0, le=1.0)
    evidence: str = ""
    comparison_mode: VariationPolicy = VariationPolicy.EXACT


class BenchmarkEvaluation(BaseModel):
    """Complete evaluation result comparing a generated artifact to a Golden Reference."""
    model_config = ConfigDict(frozen=True)
    
    evaluation_id: str
    artifact_id: str
    golden_reference_id: str
    corpus_version: str
    benchmark_protocol_version: str
    
    dimension_results: Dict[str, DimensionResult] = Field(default_factory=dict)
    hard_invariant_results: Dict[str, bool] = Field(default_factory=dict)
    variation_interpretations: Dict[str, str] = Field(default_factory=dict)
    reference_alignment: float = Field(ge=0.0, le=1.0)
    regression_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    certification_decision: CertificationDecision
    reproducibility_metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
