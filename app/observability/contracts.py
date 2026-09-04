"""
Observability contracts, enums, data models, and schemas.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class ObservationLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventType(str, Enum):
    RUN_STARTED = "run_started"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"

    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    STAGE_FAILED = "stage_failed"

    SPAN_STARTED = "span_started"
    SPAN_COMPLETED = "span_completed"
    SPAN_FAILED = "span_failed"

    CAPABILITY_RESOLVED = "capability_resolved"
    FORMAT_RESOLVED = "format_resolved"
    KNOWLEDGE_RETRIEVED = "knowledge_retrieved"
    PERSONALIZATION_APPLIED = "personalization_applied"

    QUALITY_EVALUATED = "quality_evaluated"
    CRITIQUE_GENERATED = "critique_generated"
    REFINEMENT_ITERATION = "refinement_iteration"

    ARTIFACT_RENDERED = "artifact_rendered"
    ARTIFACT_VALIDATED = "artifact_validated"

    METRIC_RECORDED = "metric_recorded"
    DIAGNOSTIC_EMITTED = "diagnostic_emitted"


class ObservationContext(BaseModel):
    run_id: str
    trace_id: str
    parent_span_id: Optional[str] = None
    span_id: Optional[str] = None
    stage: Optional[str] = None
    component: Optional[str] = None
    timestamp: float


class ObservabilityEvent(BaseModel):
    event_id: str
    event_type: EventType
    timestamp: float
    level: ObservationLevel
    context: ObservationContext
    message: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class SpanRecord(BaseModel):
    span_id: str
    parent_span_id: Optional[str] = None
    name: str
    component: Optional[str] = None
    stage: Optional[str] = None
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    status: str = "running"  # running, succeeded, failed
    attributes: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class MetricRecord(BaseModel):
    name: str
    value: float
    unit: str
    timestamp: float
    context: ObservationContext
    tags: dict[str, str] = Field(default_factory=dict)


class ErrorRecord(BaseModel):
    exception_type: str
    message: str
    component: Optional[str] = None
    stage: Optional[str] = None
    traceback_summary: str
    recoverable: bool = False
    context: ObservationContext


class ArtifactLineageRecord(BaseModel):
    artifact_id: str
    artifact_path: str
    artifact_type: str
    source_run_id: str
    trace_id: str
    format_id: Optional[str] = None
    page_count: Optional[int] = None
    parent_artifacts: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RunSummary(BaseModel):
    run_id: str
    trace_id: str
    status: str  # created, running, completed, failed
    started_at: float
    completed_at: Optional[float] = None
    duration_ms: Optional[float] = None
    stage_count: int = 0
    span_count: int = 0
    error_count: int = 0
    artifact_count: int = 0


class FailureDiagnostic(BaseModel):
    failure_id: str
    run_id: str
    trace_id: str
    stage: Optional[str] = None
    component: Optional[str] = None
    exception_type: str
    message: str
    causal_context: list[str] = Field(default_factory=list)
    completed_stages: list[str] = Field(default_factory=list)
    partial_outputs: dict[str, Any] = Field(default_factory=dict)
    timestamp: float


class ObservabilityReport(BaseModel):
    run_summary: RunSummary
    events: list[ObservabilityEvent] = Field(default_factory=list)
    spans: list[SpanRecord] = Field(default_factory=list)
    metrics: list[MetricRecord] = Field(default_factory=list)
    errors: list[ErrorRecord] = Field(default_factory=list)
    artifact_lineage: list[ArtifactLineageRecord] = Field(default_factory=list)
    diagnostics: Optional[FailureDiagnostic] = None
