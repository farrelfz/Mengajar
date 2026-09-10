"""
Universal Document Intelligence System V5 — Quality Provenance & Lineage Graph.

Phase 3A.1: End-to-end explainability graph linking:
Decision -> Finding -> Signal -> Evaluator -> Raw Evidence -> Page/Element.
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field


class EvidenceSourceType(str, Enum):
    """Originating mechanism of empirical diagnostic evidence."""
    PYMUPDF_GEOMETRY = "PYMUPDF_GEOMETRY"
    RASTER_ANALYSIS = "RASTER_ANALYSIS"
    BLUEPRINT_METRIC = "BLUEPRINT_METRIC"
    SEMANTIC_GRAPH = "SEMANTIC_GRAPH"
    FIDELITY_REPORT = "FIDELITY_REPORT"
    LEGACY_GATE = "LEGACY_GATE"
    DOM_INSPECTION = "DOM_INSPECTION"
    CALIBRATION_METRIC = "CALIBRATION_METRIC"
    LEGACY_DOCUMENT_EVALUATOR = "LEGACY_DOCUMENT_EVALUATOR"


class EvidenceReference(BaseModel):
    """Machine-readable evidence reference backing a signal or finding."""
    model_config = ConfigDict(frozen=True)

    evidence_id: str = Field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:8]}")
    source_type: EvidenceSourceType
    description: str
    measurement: Optional[str] = None
    measurement_unit: Optional[str] = None
    raw_value: Optional[Any] = None
    threshold: Optional[Any] = None
    comparison_operator: Optional[str] = None
    page_or_slide: Optional[int] = None
    bounding_box: Optional[Tuple[float, float, float, float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QualityProvenanceGraph(BaseModel):
    """Explainable directed provenance graph tracing decisions to ground physical facts."""
    model_config = ConfigDict(frozen=True)

    signals_by_id: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    findings_by_id: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    finding_to_signals: Dict[str, List[str]] = Field(default_factory=dict)
    decision_record: Dict[str, Any] = Field(default_factory=dict)

    def record_signal(self, signal: Dict[str, Any]) -> None:
        sid = signal.get("signal_id", f"sig_{len(self.signals_by_id)}")
        self.signals_by_id[sid] = signal

    def record_cluster(self, cluster_id: str, signal_ids: List[str]) -> None:
        self.finding_to_signals[cluster_id] = list(signal_ids)

    def record_finding(self, finding: Dict[str, Any]) -> None:
        fid = finding.get("finding_id", f"fnd_{len(self.findings_by_id)}")
        self.findings_by_id[fid] = finding
        if "originating_signal_ids" in finding and finding["originating_signal_ids"]:
            self.finding_to_signals[fid] = list(finding["originating_signal_ids"])

    def record_decision(self, decision: Dict[str, Any]) -> None:
        self.decision_record.clear()
        self.decision_record.update(decision)

    @property
    def signals(self) -> Dict[str, Dict[str, Any]]:
        return self.signals_by_id

    @property
    def findings(self) -> Dict[str, Dict[str, Any]]:
        return self.findings_by_id

    @property
    def decision(self) -> Dict[str, Any]:
        return self.decision_record

    def trace_finding(self, finding_id: str) -> Dict[str, Any]:
        """Traces a finding back to its originating signals, evaluators, and raw measurements."""
        finding = self.findings_by_id.get(finding_id, {})
        signal_ids = self.finding_to_signals.get(finding_id, [])
        contributing_signals = [self.signals_by_id.get(sid, {}) for sid in signal_ids]

        return {
            "finding_id": finding_id,
            "failure_code": finding.get("failure_code"),
            "severity": finding.get("severity"),
            "message": finding.get("message"),
            "causal_hypothesis": finding.get("causal_hypothesis"),
            "contributing_signals": contributing_signals,
            "raw_measurements": [
                {
                    "metric_name": s.get("metric_name"),
                    "raw_value": s.get("raw_value"),
                    "source_provider": s.get("source_provider"),
                    "location": s.get("location"),
                }
                for s in contributing_signals
            ],
        }

    def trace_decision(self) -> Dict[str, Any]:
        """Traces the executive decision back to blocking findings and contributing evidence."""
        blockers = self.decision_record.get("hard_blockers", [])
        return {
            "decision": self.decision_record.get("decision"),
            "can_export": self.decision_record.get("can_export"),
            "rationale": self.decision_record.get("rationale"),
            "blocker_traces": [self.trace_finding(f_id) for f_id in blockers if f_id in self.findings_by_id],
        }
