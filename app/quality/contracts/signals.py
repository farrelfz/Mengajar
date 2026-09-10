"""
Universal Document Intelligence System V5 — Canonical Quality Signal Contract.

Phase 3A.1: Immutable, normalized quality signal representing an empirical observation
from any specialized evaluator across Semantic, Fidelity, Artifact, and Rendered domains.
Preserves raw physical measurements alongside normalized scores.
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class QualityDomain(str, Enum):
    """The four orthogonal truth layers of document intelligence."""
    SEMANTIC = "SEMANTIC"      # Layer 1: Knowledge transformation correctness
    FIDELITY = "FIDELITY"      # Layer 2: Blueprint & element survival across adapters
    ARTIFACT = "ARTIFACT"      # Layer 3: Pedagogical, structural, cognitive ergonomics
    RENDERED = "RENDERED"      # Layer 4: Physical output geometry on actual canvas


class SignalSeverity(str, Enum):
    """Canonical severity ranking for quality signals and findings."""
    INFO = "INFO"
    WARNING = "WARNING"
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    BLOCKING = "BLOCKING"

    def _rank(self) -> int:
        ranks = {
            SignalSeverity.INFO: 0,
            SignalSeverity.WARNING: 1,
            SignalSeverity.MINOR: 1,
            SignalSeverity.MAJOR: 2,
            SignalSeverity.ERROR: 2,
            SignalSeverity.CRITICAL: 3,
            SignalSeverity.BLOCKING: 4,
        }
        return ranks.get(self, 0)

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, SignalSeverity):
            return self._rank() < other._rank()
        return NotImplemented

    def __le__(self, other: Any) -> bool:
        if isinstance(other, SignalSeverity):
            return self._rank() <= other._rank()
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, SignalSeverity):
            return self._rank() > other._rank()
        return NotImplemented

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, SignalSeverity):
            return self._rank() >= other._rank()
        return NotImplemented


class SignalConfidence(str, Enum):
    """Measurement certainty level."""
    DEFINITIVE = "DEFINITIVE"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    @property
    def numeric_value(self) -> float:
        if self.value in ("DEFINITIVE", "HIGH"):
            return 1.0
        if self.value == "MEDIUM":
            return 0.7
        return 0.4


class QualityLocation(BaseModel):
    """Spatial and structural coordinate of a defect or metric."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str = "UNKNOWN"
    page_index: Optional[int] = None
    slide_index: Optional[int] = None
    chapter_index: Optional[int] = None
    section_index: Optional[int] = None
    activity_index: Optional[int] = None
    element_id: Optional[str] = None
    element_ids: Tuple[str, ...] = Field(default_factory=tuple)
    bounding_box: Optional[Tuple[float, float, float, float]] = None  # (x0, y0, x1, y1)
    source_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)
    blueprint_element_ids: Tuple[str, ...] = Field(default_factory=tuple)
    render_element_ids: Tuple[str, ...] = Field(default_factory=tuple)

    @property
    def page_indices(self) -> Tuple[int, ...]:
        """Normalized page/slide indices."""
        if self.slide_index is not None:
            return (self.slide_index,)
        if self.page_index is not None:
            return (self.page_index,)
        return ()


class QualitySignal(BaseModel):
    """Canonical normalized signal emitted by any specialized quality evaluator."""
    model_config = ConfigDict(frozen=True)

    signal_id: str = Field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:8]}")
    artifact_type: str = "UNKNOWN"
    domain: QualityDomain = QualityDomain.ARTIFACT
    dimension: str = "STYLE_DESIGN"
    metric_name: str = "UNKNOWN_METRIC"
    raw_value: Any = 0.0                     # Empirical raw metric (e.g. 7.5pt, 140 words, 0.42)
    normalized_value: float = Field(default=1.0, ge=0.0, le=1.0)  # Standardized 0.0 (fail) to 1.0 (perfect)
    threshold: Optional[float] = None
    measurement: Optional[str] = None
    expected_range: Optional[Tuple[float, float]] = None
    severity: SignalSeverity = SignalSeverity.INFO
    confidence: SignalConfidence = SignalConfidence.HIGH
    source_provider: str = "unknown_evaluator" # Name of evaluator (e.g. 'PDFGeometryInspector')
    provenance: Dict[str, Any] = Field(default_factory=dict)
    location: QualityLocation = Field(default_factory=QualityLocation)
    page_indices: Tuple[int, ...] = Field(default_factory=tuple)
    element_ids: Tuple[str, ...] = Field(default_factory=tuple)
    evidence: Tuple[Any, ...] = Field(default_factory=tuple)
    description: str = ""
    timestamp: float = Field(default_factory=time.time)

    @model_validator(mode="before")
    @classmethod
    def pre_normalize(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # source_provider alias
        if "source_provider" not in data and "source_engine" in data:
            data["source_provider"] = data["source_engine"]
        elif "source_provider" not in data:
            data["source_provider"] = "unknown_evaluator"

        # metric_name alias
        if "metric_name" not in data:
            for key in ("canonical_code", "failure_code", "code", "measurement"):
                if key in data:
                    data["metric_name"] = str(data[key])
                    break
            else:
                data["metric_name"] = "UNKNOWN_METRIC"

        # artifact_type alias
        if "artifact_type" not in data:
            loc = data.get("location")
            if isinstance(loc, dict) and "artifact_type" in loc:
                data["artifact_type"] = loc["artifact_type"]
            elif hasattr(loc, "artifact_type"):
                data["artifact_type"] = getattr(loc, "artifact_type")
            else:
                data["artifact_type"] = "UNKNOWN"

        # dimension alias
        if "dimension" not in data:
            data["dimension"] = "STYLE_DESIGN"

        # raw_value and normalized_value defaults
        if "raw_value" not in data:
            data["raw_value"] = 0.0
        if "normalized_value" not in data:
            sev = data.get("severity", SignalSeverity.INFO)
            sev_str = str(getattr(sev, "value", sev)).upper()
            if "BLOCK" in sev_str or "CRIT" in sev_str:
                data["normalized_value"] = 0.0
            elif "ERR" in sev_str or "MAJOR" in sev_str:
                data["normalized_value"] = 0.2
            elif "WARN" in sev_str:
                data["normalized_value"] = 0.6
            else:
                data["normalized_value"] = 1.0

        # provenance alias
        if "provenance" not in data and "raw_metadata" in data:
            data["provenance"] = data["raw_metadata"]

        return data

    # Backward compatibility aliases
    @property
    def canonical_code(self) -> str:
        return self.metric_name

    @property
    def failure_domain(self) -> QualityDomain:
        return self.domain

    @property
    def failure_code(self) -> str:
        return self.metric_name

    @property
    def source_engine(self) -> str:
        return self.source_provider

    @property
    def raw_metadata(self) -> Dict[str, Any]:
        return self.provenance

