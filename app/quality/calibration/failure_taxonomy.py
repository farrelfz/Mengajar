"""
Universal Document Intelligence System V5 — Quality Failure Taxonomy.

Phase 2C: Universal taxonomy of quality failure modes and severity grading.
Every detected quality flaw maps to this standardized taxonomy.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class FailureCategory(str, Enum):
    """Universal categories of quality failure modes."""
    STRUCTURAL_FAILURE = "STRUCTURAL_FAILURE"
    SEMANTIC_LAYOUT_FAILURE = "SEMANTIC_LAYOUT_FAILURE"
    READABILITY_FAILURE = "READABILITY_FAILURE"
    COMPOSITION_FAILURE = "COMPOSITION_FAILURE"
    REPETITION_FAILURE = "REPETITION_FAILURE"
    DENSITY_FAILURE = "DENSITY_FAILURE"
    FLOW_FAILURE = "FLOW_FAILURE"
    PEDAGOGICAL_FAILURE = "PEDAGOGICAL_FAILURE"
    SCIENTIFIC_INTEGRITY_FAILURE = "SCIENTIFIC_INTEGRITY_FAILURE"
    TRACEABILITY_FAILURE = "TRACEABILITY_FAILURE"
    ARTIFACT_SPECIFIC_FAILURE = "ARTIFACT_SPECIFIC_FAILURE"


class FailureSeverity(str, Enum):
    """Severity calibration for quality failures."""
    INFO = "INFO"           # Informational advisory, no score impact
    WARNING = "WARNING"     # Moderate design/pedagogical issue, export allowed
    ERROR = "ERROR"         # Substantial defect, requires refinement
    CRITICAL = "CRITICAL"   # Fatal integrity/readability defect, blocks export


class QualityFailure(BaseModel):
    """Structured diagnostic failure report mapping directly to the taxonomy."""
    model_config = ConfigDict(frozen=True)

    category: FailureCategory
    severity: FailureSeverity
    metric_name: str
    observed_value: Any
    expected_threshold: str
    target_elements: tuple[str, ...] = Field(default_factory=tuple)
    summary: str
    details: str = ""
    is_blocking: bool = False

    @classmethod
    def create(
        cls,
        category: FailureCategory,
        severity: FailureSeverity,
        metric_name: str,
        observed_value: Any,
        expected_threshold: str,
        summary: str,
        target_elements: list[str] | None = None,
        details: str = "",
    ) -> QualityFailure:
        is_blocking = severity == FailureSeverity.CRITICAL
        return cls(
            category=category,
            severity=severity,
            metric_name=metric_name,
            observed_value=observed_value,
            expected_threshold=expected_threshold,
            target_elements=tuple(target_elements or []),
            summary=summary,
            details=details,
            is_blocking=is_blocking,
        )
