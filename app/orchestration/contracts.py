"""
Authoritative typed contracts, state enums, and data models for Production Orchestration Runtime.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ══════════════════════════════════════════════════════════════════════════════


class ArtifactLifecycleState(str, Enum):
    """Lifecycle state of an individual production artifact."""
    DECLARED = "declared"
    GENERATED = "generated"
    VALIDATED = "validated"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"
    FAILED = "failed"


class ProductionJobStatus(str, Enum):
    """High-level status of the entire production job."""
    CREATED = "created"
    RUNNING = "running"
    WAITING_FOR_REFINEMENT = "waiting_for_refinement"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StageState(str, Enum):
    """Execution state of an individual workflow stage."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"
    BLOCKED = "blocked"


class JobPriority(str, Enum):
    """Priority level for job scheduling."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class FailureCategory(str, Enum):
    """Taxonomy of failures encountered during execution."""
    INPUT = "input"
    DEPENDENCY = "dependency"
    GROUNDING = "grounding"
    QUALITY = "quality"
    CRITIC = "critic"
    REFINEMENT = "refinement"
    RENDERING = "rendering"
    ARTIFACT = "artifact"
    INTERNAL = "internal"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class FailureSeverity(str, Enum):
    """Impact severity of an execution failure."""
    WARNING = "warning"
    RECOVERABLE = "recoverable"
    FATAL = "fatal"
    CRITICAL = "critical"


class ProductionGateType(str, Enum):
    """Types of formal quality gates evaluated by the orchestrator."""
    GROUNDING_GATE = "grounding_gate"
    STRUCTURAL_QUALITY_GATE = "structural_quality_gate"
    PEDAGOGICAL_QUALITY_GATE = "pedagogical_quality_gate"
    CRITIC_GATE = "critic_gate"
    ARTIFACT_GEOMETRY_GATE = "artifact_geometry_gate"
    FINAL_RELEASE_GATE = "final_release_gate"


class GateDecisionEnum(str, Enum):
    """Decision outcome emitted by a production gate."""
    PASS = "pass"
    PASS_WITH_WARNINGS = "pass_with_warnings"
    RETRY = "retry"
    REFINE = "refine"
    BLOCK = "block"
    FAIL = "fail"


class WorkflowStageType(str, Enum):
    """Canonical stage identifiers."""
    VALIDATION = "validation"
    DIRECTING = "directing"
    PERSONALIZATION = "personalization"
    GROUNDING = "grounding"
    BLUEPRINT_GENERATION = "blueprint_generation"
    COMPOSITION = "composition"
    PRE_RENDER_QUALITY = "pre_render_quality"
    CRITIC_REVIEW = "critic_review"
    REFINEMENT = "refinement"
    RENDERING = "rendering"
    ARTIFACT_VALIDATION = "artifact_validation"
    FINALIZATION = "finalization"


# ══════════════════════════════════════════════════════════════════════════════
# DATA CONTRACTS
# ══════════════════════════════════════════════════════════════════════════════


class JobMetadata(BaseModel):
    """Contextual metadata attached to a production job."""
    domain: str = "general"
    audience_level: str = "general"
    target_format: str = "a4_portrait"
    target_artifact: str = "document"
    profile: str = "standard"
    seed: int = 42
    created_at: str = ""
    extra: dict[str, Any] = Field(default_factory=dict)


class ProductionJobRequest(BaseModel):
    """Inbound request specification for producing a material artifact."""
    job_id: str
    raw_input: str
    source_hint: str = "material_request.txt"
    priority: JobPriority = JobPriority.NORMAL
    metadata: JobMetadata = Field(default_factory=JobMetadata)
    idempotency_key: str | None = None


class ProductionFailure(BaseModel):
    """Structured record of a failure or fatal error."""
    stage_id: str
    category: FailureCategory
    severity: FailureSeverity
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    retryable: bool = False


class ProductionGateResult(BaseModel):
    """Outcome of a formal gate evaluation."""
    gate_type: ProductionGateType
    decision: GateDecisionEnum
    score: float = 1.0
    threshold: float = 0.75
    reasoning: str = ""
    findings: list[str] = Field(default_factory=list)
    recommended_next_stage: str | None = None


class StageExecutionResult(BaseModel):
    """Typed result emitted upon stage completion."""
    stage_id: str
    state: StageState
    output: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    failure: ProductionFailure | None = None
    duration_ms: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProductionJobContext(BaseModel):
    """Shared execution context passed across workflow stages."""
    job_id: str
    request: ProductionJobRequest
    stage_results: dict[str, StageExecutionResult] = Field(default_factory=dict)
    shared_data: dict[str, Any] = Field(default_factory=dict)
    gate_results: list[ProductionGateResult] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    refinement_iterations: int = 0
    retries_count: dict[str, int] = Field(default_factory=dict)


class ProductionJobResult(BaseModel):
    """Authoritative result returned by ProductionOrchestrator."""
    job_id: str
    status: ProductionJobStatus
    success: bool
    output_artifacts: list[str] = Field(default_factory=list)
    pdf_path: str | None = None
    gate_results: list[ProductionGateResult] = Field(default_factory=list)
    stage_history: list[str] = Field(default_factory=list)
    failures: list[ProductionFailure] = Field(default_factory=list)
    execution_duration_ms: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)
