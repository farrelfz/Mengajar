"""
Universal Document Intelligence System V5 — Canonical Quality Contracts.

Phase 3A.2: Immutable contracts for QualitySignal, QualityLocation, EvidenceReference,
QualitySnapshot, and forward-compatible RootCauseHypothesis and FailureCluster.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.quality.causal.taxonomy import (
    ArchitectureLayer,
    CanonicalFailureCategory,
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalFailureSeverity,
    CanonicalRepairClass,
    CanonicalSeverity,
    CausalConfidence,
    CausalConfidenceLevel,
    DetectionConfidence,
    FailureScope,
    UnifiedDecisionStatus,
    get_domain_for_code,
)
from app.quality.causal.provenance import EvidenceReference, EvidenceSourceType


class QualityLocation(BaseModel):
    """Artifact-neutral spatial and structural coordinate for quality defects."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    page_index: Optional[int] = None
    slide_index: Optional[int] = None
    chapter_index: Optional[int] = None
    section_index: Optional[int] = None
    activity_index: Optional[int] = None
    element_id: Optional[str] = None
    bounding_box: Optional[Tuple[float, float, float, float]] = None  # (x0, y0, x1, y1)
    source_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)
    blueprint_element_ids: Tuple[str, ...] = Field(default_factory=tuple)
    render_element_ids: Tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("bounding_box")
    @classmethod
    def validate_bounding_box(cls, v: Optional[Tuple[float, float, float, float]]) -> Optional[Tuple[float, float, float, float]]:
        if v is None:
            return None
        if len(v) != 4:
            raise ValueError("Bounding box must be a tuple of 4 floats (x0, y0, x1, y1)")
        x0, y0, x1, y1 = v
        if x0 > x1 or y0 > y1:
            raise ValueError(f"Invalid bounding box: x0({x0}) > x1({x1}) or y0({y0}) > y1({y1})")
        return v

    @property
    def page_indices(self) -> Tuple[int, ...]:
        """Provides normalized page/slide indices."""
        if self.slide_index is not None:
            return (self.slide_index,)
        if self.page_index is not None:
            return (self.page_index,)
        return ()


class QualitySignal(BaseModel):
    """Detection-only quality symptom emitted by an inspection engine."""
    model_config = ConfigDict(frozen=True)

    signal_id: str = Field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:8]}")
    source_engine: str
    failure_domain: CanonicalFailureDomain
    failure_code: CanonicalFailureCode
    severity: CanonicalSeverity = CanonicalSeverity.INFO
    detection_confidence: DetectionConfidence = DetectionConfidence.HIGH
    location: QualityLocation
    evidence: Tuple[EvidenceReference, ...] = Field(default_factory=tuple)
    description: str = ""
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)

    # Backward-compatibility fields for Phase 3A.1
    source_phase: str = "PHASE_3A"
    artifact_type: str = ""
    page_indices: Tuple[int, ...] = Field(default_factory=tuple)
    dimension: str = ""
    metric_name: str = ""
    metric_value: Any = None
    threshold: str = ""
    comparison: str = ""
    diagnostic_context: Dict[str, Any] = Field(default_factory=dict)

    FORBIDDEN_CAUSAL_FIELDS: ClassVar[Tuple[str, ...]] = (
        "cause_layer",
        "cause_code",
        "repair_action",
        "root_cause_hypothesis",
        "repair_authority",
        "allowed_repair_classes",
        "causal_confidence",
    )

    @model_validator(mode="before")
    @classmethod
    def pre_validate_and_normalize(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # Check detection-only invariant
        for forbidden in cls.FORBIDDEN_CAUSAL_FIELDS:
            if forbidden in data and data[forbidden] is not None:
                raise ValueError(
                    f"QualitySignal is detection-only and cannot contain causal attribution or repair actions: '{forbidden}'"
                )

        values = dict(data)

        # Normalize location if omitted
        if "location" not in values or values["location"] is None:
            art_type = values.get("artifact_type", "UNKNOWN")
            p_indices = values.get("page_indices", ())
            first_idx = p_indices[0] if p_indices else None
            slide_idx = first_idx if art_type.upper() == "PRESENTATION" else None
            page_idx = first_idx if art_type.upper() != "PRESENTATION" else None
            values["location"] = QualityLocation(
                artifact_type=art_type,
                slide_index=slide_idx,
                page_index=page_idx,
            )

        # Normalize failure_code if omitted or string
        if "failure_code" not in values or values["failure_code"] is None:
            code_candidate = values.get("metric_name", "RENDER_SCALE_FAILURE")
            try:
                values["failure_code"] = CanonicalFailureCode(code_candidate)
            except ValueError:
                values["failure_code"] = CanonicalFailureCode.RENDER_SCALE_FAILURE
        elif isinstance(values["failure_code"], str):
            try:
                values["failure_code"] = CanonicalFailureCode(values["failure_code"])
            except ValueError:
                pass

        # Normalize failure_domain if omitted
        if "failure_domain" not in values or values["failure_domain"] is None:
            dim = values.get("dimension")
            if dim:
                values["failure_domain"] = get_domain_for_code(dim)
            else:
                values["failure_domain"] = get_domain_for_code(values["failure_code"])

        # Normalize severity if string or CanonicalFailureSeverity
        if "severity" in values and isinstance(values["severity"], str):
            sev_str = values["severity"].upper()
            try:
                values["severity"] = CanonicalSeverity(sev_str)
            except ValueError:
                values["severity"] = CanonicalSeverity.INFO

        # Normalize evidence if passed as dict, list, or synthesize from metric_value
        if "evidence" in values and values["evidence"] is not None:
            raw_ev = values["evidence"]
            if isinstance(raw_ev, dict):
                ev_ref = EvidenceReference(
                    source_type=EvidenceSourceType.CALIBRATION_METRIC,
                    description=values.get("description", "Diagnostic evidence"),
                    measurement=values.get("metric_name"),
                    raw_value=values.get("metric_value"),
                    threshold=values.get("threshold"),
                    comparison_operator=values.get("comparison"),
                    metadata=raw_ev,
                )
                values["evidence"] = (ev_ref,)
            elif isinstance(raw_ev, list):
                values["evidence"] = tuple(raw_ev)
        elif "evidence" not in values:
            if values.get("metric_value") is not None or values.get("threshold"):
                ev_ref = EvidenceReference(
                    source_type=EvidenceSourceType.CALIBRATION_METRIC,
                    description=values.get("description", "Diagnostic evidence"),
                    measurement=values.get("metric_name"),
                    raw_value=values.get("metric_value"),
                    threshold=values.get("threshold"),
                    comparison_operator=values.get("comparison"),
                )
                values["evidence"] = (ev_ref,)

        # Populate backward-compatible fields
        if not values.get("artifact_type") and "location" in values:
            loc = values["location"]
            if hasattr(loc, "artifact_type"):
                values["artifact_type"] = loc.artifact_type
            elif isinstance(loc, dict):
                values["artifact_type"] = loc.get("artifact_type", "")

        if not values.get("page_indices") and "location" in values:
            loc = values["location"]
            if hasattr(loc, "page_indices"):
                values["page_indices"] = loc.page_indices
            elif isinstance(loc, dict):
                s_idx = loc.get("slide_index")
                p_idx = loc.get("page_index")
                if s_idx is not None:
                    values["page_indices"] = (s_idx,)
                elif p_idx is not None:
                    values["page_indices"] = (p_idx,)

        if not values.get("dimension") and "failure_domain" in values:
            fd = values["failure_domain"]
            values["dimension"] = fd.value if hasattr(fd, "value") else str(fd)

        if not values.get("metric_name") and "failure_code" in values:
            fc = values["failure_code"]
            values["metric_name"] = fc.value if hasattr(fc, "value") else str(fc)

        return values

    @model_validator(mode="after")
    def validate_blocking_evidence_invariant(self) -> QualitySignal:
        if self.severity in (CanonicalSeverity.CRITICAL, CanonicalSeverity.BLOCKING):
            if not self.evidence:
                raise ValueError(
                    f"QualitySignal with severity {self.severity.value} requires non-empty evidence references."
                )
        return self

    def __hash__(self) -> int:
        return hash((self.signal_id, self.failure_code, self.location.page_indices))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, QualitySignal):
            return False
        return self.signal_id == other.signal_id


class QualitySnapshot(BaseModel):
    """In-memory, immutable serialized state of an artifact's quality signals at a given moment."""
    model_config = ConfigDict(frozen=True)

    snapshot_id: str = Field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:8]}")
    artifact_type: str
    created_at: float = Field(default_factory=time.time)
    signals: Tuple[QualitySignal, ...] = Field(default_factory=tuple)
    total_signals: int = 0
    domain_breakdown: Dict[str, int] = Field(default_factory=dict)
    severity_breakdown: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_signals(
        cls,
        artifact_type: str,
        signals: Sequence[QualitySignal],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QualitySnapshot:
        """Constructs snapshot calculating aggregates from provided signals."""
        sig_tuple = tuple(signals)
        domain_counts: Dict[str, int] = {}
        severity_counts: Dict[str, int] = {}

        for s in sig_tuple:
            dom = s.failure_domain.value if hasattr(s.failure_domain, "value") else str(s.failure_domain)
            domain_counts[dom] = domain_counts.get(dom, 0) + 1

            sev = s.severity.value if hasattr(s.severity, "value") else str(s.severity)
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return cls(
            artifact_type=artifact_type,
            signals=sig_tuple,
            total_signals=len(sig_tuple),
            domain_breakdown=domain_counts,
            severity_breakdown=severity_counts,
            metadata=metadata or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes snapshot to dictionary."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> QualitySnapshot:
        """Deserializes snapshot from dictionary."""
        return cls.model_validate(data)


# ============================================================================
# FORWARD-COMPATIBLE PLACEHOLDERS FOR PHASE 3B / BACKWARD COMPATIBILITY
# ============================================================================

class RootCauseHypothesis(BaseModel):
    """Causal hypothesis attributing a failure to an architectural layer."""
    model_config = ConfigDict(frozen=True)

    hypothesis_id: str = Field(default_factory=lambda: f"hyp_{uuid.uuid4().hex[:8]}")
    cause_code: str
    cause_layer: Any
    confidence_score: float = Field(ge=0.0, le=1.0)
    confidence_level: Any = CausalConfidence.HIGH
    supporting_evidence: Tuple[str, ...] = Field(default_factory=tuple)
    contradicting_evidence: Tuple[str, ...] = Field(default_factory=tuple)
    affected_scope: FailureScope = FailureScope.LOCAL
    repair_authority: Optional[Any] = None
    allowed_repair_classes: Tuple[CanonicalRepairClass, ...] = Field(default_factory=tuple)
    forbidden_repairs: Tuple[str, ...] = Field(default_factory=tuple)
    confidence_components: Optional[Dict[str, float]] = None
    causal_path: Optional[str] = None
    status: Optional[str] = None
    explains_signal_ids: Tuple[str, ...] = Field(default_factory=tuple)
    alternative_rank: int = 1

    @property
    def origin_layer(self) -> Any:
        return self.cause_layer

    @property
    def category(self) -> Any:
        return self.cause_code


class FailureCluster(BaseModel):
    """Group of co-occurring failures on shared pages with unified root cause attribution."""
    model_config = ConfigDict(frozen=True)

    cluster_id: str = Field(default_factory=lambda: f"clust_{uuid.uuid4().hex[:8]}")
    affected_pages: Tuple[int, ...] = Field(default_factory=tuple)
    symptoms: Tuple[CanonicalFailureCode, ...] = Field(default_factory=tuple)
    signals: Tuple[QualitySignal, ...] = Field(default_factory=tuple)
    scope: FailureScope = FailureScope.LOCAL
    dominant_failure_patterns: Tuple[str, ...] = Field(default_factory=tuple)
    affected_locations: Tuple[QualityLocation, ...] = Field(default_factory=tuple)
    shared_context: Dict[str, Any] = Field(default_factory=dict)
    correlation_strength: float = 0.0
    cluster_summary: str = ""
    cluster_evidence: Tuple[str, ...] = Field(default_factory=tuple)
    failures: Tuple[CanonicalFailure, ...] = Field(default_factory=tuple)
    primary_root_cause: Optional[RootCauseHypothesis] = None
    alternative_hypotheses: Tuple[RootCauseHypothesis, ...] = Field(default_factory=tuple)
    is_ambiguous: bool = False
    recommended_repair_class: CanonicalRepairClass = CanonicalRepairClass.NONE
    rationale: str = ""
    causal_decision: Optional[str] = None


class CanonicalFailure(BaseModel):
    """Deduplicated defect representation used in Phase 3A.1."""
    model_config = ConfigDict(frozen=True)

    failure_id: str = Field(default_factory=lambda: f"fail_{uuid.uuid4().hex[:8]}")
    failure_code: CanonicalFailureCode
    category: CanonicalFailureCategory = CanonicalFailureCategory.RENDER
    artifact_type: str
    affected_pages: Tuple[int, ...] = Field(default_factory=tuple)
    severity: CanonicalSeverity
    symptom: str
    evidence_signals: Tuple[QualitySignal, ...] = Field(default_factory=tuple)
    quality_dimension: str
    scope: FailureScope = FailureScope.LOCAL
    frequency: float = 0.0
    impact: str = ""
    detected_by: str = ""

    def __hash__(self) -> int:
        return hash((self.failure_id, self.failure_code, self.affected_pages))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CanonicalFailure):
            return False
        return self.failure_id == other.failure_id


class CanonicalQualityAssessment(BaseModel):
    """Authoritative, consolidated decision outcome issued by UnifiedQualityAuthority."""
    model_config = ConfigDict(frozen=True)

    assessment_id: str = Field(default_factory=lambda: f"qa_{uuid.uuid4().hex[:8]}")
    artifact_type: str
    rendered_pdf_path: Optional[str] = None
    page_count: int
    dimensional_scores: Dict[str, float] = Field(default_factory=dict)
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    failures: Tuple[CanonicalFailure, ...] = Field(default_factory=tuple)
    failure_clusters: Tuple[FailureCluster, ...] = Field(default_factory=tuple)
    root_cause_hypotheses: Tuple[RootCauseHypothesis, ...] = Field(default_factory=tuple)
    critical_failures_count: int = 0
    major_warnings_count: int = 0
    minor_warnings_count: int = 0
    decision: UnifiedDecisionStatus
    can_export: bool
    repair_required: bool
    manual_review_required: bool
    rationale: str
    timestamp: float = Field(default_factory=time.time)
