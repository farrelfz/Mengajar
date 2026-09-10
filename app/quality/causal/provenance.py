"""
Universal Document Intelligence System V5 — Quality Evidence Provenance Contract.

Phase 3A.2: Machine-readable evidence references and provenance tracking
for all diagnostic quality signals.
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_validator


class EvidenceSourceType(str, Enum):
    """Supported machine-readable evidence source mechanisms."""
    PYMUPDF_GEOMETRY = "PYMUPDF_GEOMETRY"
    RASTER_ANALYSIS = "RASTER_ANALYSIS"
    BLUEPRINT_METRIC = "BLUEPRINT_METRIC"
    SEMANTIC_GRAPH = "SEMANTIC_GRAPH"
    FIDELITY_REPORT = "FIDELITY_REPORT"
    LEGACY_GATE = "LEGACY_GATE"
    DOM_INSPECTION = "DOM_INSPECTION"
    CALIBRATION_METRIC = "CALIBRATION_METRIC"


class EvidenceReference(BaseModel):
    """Immutable, machine-readable evidence reference backing a quality signal."""
    model_config = ConfigDict(frozen=True)

    evidence_id: str = Field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:8]}")
    source_type: EvidenceSourceType
    description: str
    measurement: Optional[str] = None
    measurement_unit: Optional[str] = None
    raw_value: Optional[Any] = None
    threshold: Optional[Any] = None
    comparison_operator: Optional[str] = None  # e.g. "<", ">", "<=", ">=", "==", "!="
    artifact_path: Optional[str] = None
    page_or_slide: Optional[int] = None
    element_selector: Optional[str] = None
    bounding_box: Optional[Tuple[float, float, float, float]] = None  # (x0, y0, x1, y1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)

    @field_validator("bounding_box")
    @classmethod
    def validate_bounding_box(cls, v: Optional[Tuple[float, float, float, float]]) -> Optional[Tuple[float, float, float, float]]:
        if v is None:
            return None
        if len(v) != 4:
            raise ValueError("Bounding box must be a tuple of 4 floats (x0, y0, x1, y1)")
        x0, y0, x1, y1 = v
        if x0 > x1 or y0 > y1:
            raise ValueError(f"Invalid bounding box coordinates: x0({x0}) > x1({x1}) or y0({y0}) > y1({y1})")
        return v
