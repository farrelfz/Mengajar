"""
Universal Document Intelligence System V5 — Benchmark & Generalization Contracts.

Phase 4.1: Immutable, machine-readable contracts governing benchmark metadata,
execution outcomes, generalization metrics, applicability envelopes, and integrity auditing.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.benchmarking.taxonomy import (
    CorpusCategory,
    CorpusSplit,
    EvidenceStrength,
    GeneralizationFailureType,
)


class StructuralSignature(BaseModel):
    """Quantified structural attributes of a benchmark source document."""
    model_config = ConfigDict(frozen=True)

    token_count: int = Field(ge=0)
    character_count: int = Field(ge=0)
    section_count: int = Field(ge=0)
    max_heading_depth: int = Field(ge=1, le=6)
    table_count: int = Field(default=0, ge=0)
    formula_count: int = Field(default=0, ge=0)
    has_code_blocks: bool = False
    has_mixed_languages: bool = False
    card_estimate: int = Field(default=0, ge=0)


class BenchmarkFixtureMetadata(BaseModel):
    """Machine-readable metadata descriptor accompanying every benchmark fixture."""
    model_config = ConfigDict(frozen=True)

    fixture_id: str
    source_path: str
    corpus_category: CorpusCategory
    domain: str
    difficulty_level: str = "INTERMEDIATE"  # BEGINNER, INTERMEDIATE, ADVANCED, PATHOLOGICAL
    structural_signature: StructuralSignature
    semantic_density: float = Field(default=0.5, ge=0.0, le=1.0)
    formula_density: float = Field(default=0.5, ge=0.0, le=1.0)
    table_density: float = Field(default=0.5, ge=0.0, le=1.0)
    narrative_complexity: float = Field(default=0.5, ge=0.0, le=1.0)
    inquiry_complexity: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence_complexity: float = Field(default=0.5, ge=0.0, le=1.0)
    expected_artifact_types: Tuple[str, ...] = ("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT")
    known_pathologies: Tuple[str, ...] = ()
    split: CorpusSplit = CorpusSplit.UNSEEN_GENERALIZATION
    provenance: str = "Phase 4.1 Benchmark Corpus"
    content_hash: str = ""

    @classmethod
    def compute_hash(cls, raw_content: str) -> str:
        return hashlib.sha256(raw_content.encode("utf-8")).hexdigest()[:16]


class BenchmarkExecutionTarget(BaseModel):
    """Target job specification for the benchmark runner."""
    model_config = ConfigDict(frozen=True)

    fixture_id: str
    artifact_type: str
    metadata: BenchmarkFixtureMetadata
    raw_source: str


class BenchmarkExecutionOutcome(BaseModel):
    """Detailed execution result for an individual fixture and artifact format."""
    model_config = ConfigDict(frozen=True)

    job_id: str
    fixture_id: str
    artifact_type: str
    corpus_category: CorpusCategory
    split: CorpusSplit
    success: bool
    final_state: str
    decision: str
    overall_quality_score: float
    total_iterations: int
    elapsed_seconds: float
    hard_blockers_count: int
    hard_blockers: Tuple[str, ...] = ()
    findings_count: int = 0
    operators_attempted: Tuple[str, ...] = ()
    operators_committed: Tuple[str, ...] = ()
    operators_rolled_back: Tuple[str, ...] = ()
    zero_effect_operators: Tuple[str, ...] = ()
    has_export_package: bool = False
    has_failure_report: bool = False
    generalization_failure: Optional[GeneralizationFailureType] = None
    notes: str = ""


class GeneralizationMetrics(BaseModel):
    """Comprehensive corpus-level generalization metrics."""
    model_config = ConfigDict(frozen=True)

    total_jobs: int
    known_jobs: int
    unseen_jobs: int
    pathological_jobs: int

    repair_generalization_rate: float = Field(ge=0.0, le=1.0)  # RGR
    repair_regression_rate: float = Field(ge=0.0, le=1.0)      # RRG
    false_repair_rate: float = Field(ge=0.0, le=1.0)           # FRR
    causal_resolution_rate: float = Field(ge=0.0, le=1.0)      # CRR
    zero_effect_rate: float = Field(ge=0.0, le=1.0)            # ZER

    known_corpus_mean_score: float = Field(ge=0.0, le=1.0)
    unseen_corpus_mean_score: float = Field(ge=0.0, le=1.0)
    generalization_gap: float                                  # known - unseen
    generalization_warning: bool = False                       # True if gap > 0.08 or unseen regressions
    worst_case_score: float = Field(ge=0.0, le=1.0)
    unseen_blocker_retention_rate: float = Field(ge=0.0, le=1.0)
    mean_iterations_to_convergence: float = Field(ge=0.0)


class OperatorApplicabilityEnvelope(BaseModel):
    """Empirical performance profile defining where an operator is certified to work."""
    model_config = ConfigDict(frozen=True)

    operator_id: str
    supported_artifact_types: Tuple[str, ...]
    supported_root_causes: Tuple[str, ...]
    validated_structural_signatures: Tuple[str, ...]
    unsupported_signatures: Tuple[str, ...]
    evidence_strength: EvidenceStrength
    unseen_success_rate: float = Field(ge=0.0, le=1.0)
    regression_rate: float = Field(ge=0.0, le=1.0)
    fixture_diversity_count: int = Field(ge=0)
    notes: str = ""


class BenchmarkIntegrityReport(BaseModel):
    """Integrity verification results for the benchmark run."""
    model_config = ConfigDict(frozen=True)

    fixtures_immutable: bool = True
    mutated_fixture_ids: Tuple[str, ...] = ()
    leakage_detected: bool = False
    leakage_details: Tuple[str, ...] = ()
    reproducibility_verified: bool = True
    timestamp: float = Field(default_factory=time.time)
