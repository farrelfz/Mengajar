"""
Universal Document Intelligence System V5 — Canonical Quality Finding Contract.

Phase 3A.1: Structured finding and finding cluster contracts representing
actionable, causally classified quality defects with complete backward compatibility.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.quality.contracts.signals import QualityDomain, QualitySignal, SignalSeverity


class QualityFinding(BaseModel):
    """Canonical quality defect or non-conformance finding."""
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    finding_id: str = Field(default_factory=lambda: f"fnd_{uuid.uuid4().hex[:8]}")
    failure_code: str = ""
    domain: QualityDomain = QualityDomain.ARTIFACT
    dimension: Any = ""
    severity: Any = SignalSeverity.INFO
    artifact_type: str = "main"
    message: str = ""
    causal_hypothesis: Optional[str] = None
    affected_pages: Tuple[int, ...] = Field(default_factory=tuple)
    affected_elements: Tuple[str, ...] = Field(default_factory=tuple)
    affected_section: Optional[str] = None
    repairability: bool = True
    repair_class: str = "NONE"
    evidence_refs: Tuple[str, ...] = Field(default_factory=tuple)
    originating_signal_ids: Tuple[str, ...] = Field(default_factory=tuple)
    
    # Legacy compatibility fields
    recommendation: str = ""
    score_impact: float = 0.0
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    is_deterministic: bool = True
    evidence: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)

    @model_validator(mode="before")
    @classmethod
    def pre_normalize_legacy(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        
        # Support legacy aliases
        if "id" in data and "finding_id" not in data:
            data["finding_id"] = data["id"]
        if "finding" in data and "message" not in data:
            data["message"] = data["finding"]
        if "affected_artifact" in data and "artifact_type" not in data:
            data["artifact_type"] = data["affected_artifact"]
            
        return data

    @property
    def id(self) -> str:
        return self.finding_id

    @property
    def finding(self) -> str:
        return self.message

    @property
    def affected_artifact(self) -> str:
        return self.artifact_type

    @classmethod
    def from_legacy(cls, legacy_finding: Any) -> QualityFinding:
        """Construct CanonicalQualityFinding from a legacy QualityFinding object."""
        if isinstance(legacy_finding, cls):
            return legacy_finding
        
        # Convert legacy attributes
        finding_id = getattr(legacy_finding, "id", None) or f"fnd_{uuid.uuid4().hex[:8]}"
        dim = getattr(legacy_finding, "dimension", "")
        sev = getattr(legacy_finding, "severity", SignalSeverity.INFO)
        msg = getattr(legacy_finding, "finding", "") or getattr(legacy_finding, "message", "")
        rec = getattr(legacy_finding, "recommendation", "")
        score_imp = getattr(legacy_finding, "score_impact", 0.0)
        ev = getattr(legacy_finding, "evidence", {})
        art = getattr(legacy_finding, "affected_artifact", "main")
        sec = getattr(legacy_finding, "affected_section", None)
        
        # Map severity to SignalSeverity if possible
        sev_mapped = sev
        if hasattr(sev, "name"):
            name = sev.name.upper()
            if name in ("CRITICAL", "BLOCKING"):
                sev_mapped = SignalSeverity.BLOCKING
            elif name == "ERROR":
                sev_mapped = SignalSeverity.ERROR
            elif name == "WARNING":
                sev_mapped = SignalSeverity.WARNING
            elif name == "INFO":
                sev_mapped = SignalSeverity.INFO
                
        return cls(
            finding_id=finding_id,
            dimension=dim,
            severity=sev_mapped,
            message=msg,
            recommendation=rec,
            score_impact=score_imp,
            evidence=ev,
            artifact_type=art,
            affected_section=sec,
        )

    def is_blocking(self) -> bool:
        """True if finding unconditionally halts document export."""
        sev_str = self.severity.value if hasattr(self.severity, "value") else str(self.severity).lower()
        return sev_str.upper() in ("BLOCKING", "CRITICAL") or sev_str in ("critical", "blocking")


CanonicalQualityFinding = QualityFinding


class FindingCluster(BaseModel):
    """Cluster of co-occurring, correlated findings on shared pages/elements."""
    model_config = ConfigDict(frozen=True)

    cluster_id: str = Field(default_factory=lambda: f"fclust_{uuid.uuid4().hex[:8]}")
    canonical_finding: QualityFinding
    correlated_findings: Tuple[QualityFinding, ...] = Field(default_factory=tuple)
    contributing_signals: Tuple[QualitySignal, ...] = Field(default_factory=tuple)
    affected_pages: Tuple[int, ...] = Field(default_factory=tuple)
    severity: SignalSeverity = SignalSeverity.INFO
    evidence_sources: Tuple[str, ...] = Field(default_factory=tuple)
    correlation_strength: float = 0.0
    rationale: str = ""
