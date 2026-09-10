"""Versioned contracts for the Phase 7 observational job read model.

These contracts deliberately store values *as observed*.  They do not contain
quality, export, benchmark, or repair decision logic.
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

READ_MODEL_SCHEMA_VERSION = "7.0"


class ObservedProjection(BaseModel):
    model_config = ConfigDict(frozen=True)
    observed_value: Any = None
    source: str
    timestamp: float
    schema_version: str = READ_MODEL_SCHEMA_VERSION


class JobIdentity(BaseModel):
    model_config = ConfigDict(frozen=True)
    job_id: str
    artifact_type: str | None = None
    created_at: float


class JobMetadata(ObservedProjection):
    title: str | None = None
    model: str | None = None
    source_hint: str | None = None


class JobStateProjection(ObservedProjection):
    current_state: str
    transitions: tuple[dict[str, Any], ...] = ()
    terminal: bool = False


class QualityProjection(ObservedProjection):
    overall_quality_score: float | None = None
    domain_scores: dict[str, float] = Field(default_factory=dict)
    dimension_scores: dict[str, Any] = Field(default_factory=dict)
    hard_blockers: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    findings: tuple[dict[str, Any], ...] = ()
    decision: str | None = None
    export_eligible: bool | None = None


class RepairProjection(ObservedProjection):
    iterations: tuple[dict[str, Any], ...] = ()


class ConvergenceProjection(ObservedProjection):
    state: str | None = None
    current_iteration: int = 0
    iteration_budget: int | None = None
    diagnostics: dict[str, Any] = Field(default_factory=dict)


class BenchmarkProjection(ObservedProjection):
    corpus_version: str | None = None
    corpus_digest: str | None = None
    certification_decision: str | None = None
    regression_result: str | None = None
    baseline_provenance: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class ReviewProjection(ObservedProjection):
    case_id: str | None = None
    state: str | None = None
    reason: str | None = None
    directives: tuple[dict[str, Any], ...] = ()


class ArtifactProjection(ObservedProjection):
    inventory: tuple[dict[str, Any], ...] = ()


class ObservabilityProjection(ObservedProjection):
    stage_durations: dict[str, float] = Field(default_factory=dict)
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


class ProjectionDiagnostic(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: str
    message: str
    severity: str = "WARNING"
    timestamp: float


class JobSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)
    schema_version: str = READ_MODEL_SCHEMA_VERSION
    snapshot_number: int
    timestamp: float
    identity: JobIdentity
    metadata: JobMetadata
    state: JobStateProjection
    quality: QualityProjection
    repair: RepairProjection
    convergence: ConvergenceProjection
    benchmark: BenchmarkProjection
    review: ReviewProjection
    artifacts: ArtifactProjection
    observability: ObservabilityProjection
    diagnostics: tuple[ProjectionDiagnostic, ...] = ()


class SnapshotManifest(BaseModel):
    model_config = ConfigDict(frozen=True)
    schema_version: str = READ_MODEL_SCHEMA_VERSION
    job_id: str
    snapshot_count: int = 0
    latest_snapshot: str | None = None
    snapshots: tuple[dict[str, Any], ...] = ()
