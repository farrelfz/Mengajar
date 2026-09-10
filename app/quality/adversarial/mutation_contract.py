"""
Universal Document Intelligence System V5 — Adversarial Mutation Contracts.

Phase 2C: Governs controlled bad artifact mutations representing realistic failure modes.
Every mutation specifies expected failure category, target elements, signal, and severity.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.calibration.failure_taxonomy import FailureCategory, FailureSeverity


class ArtifactMutation(BaseModel):
    """Specification of an adversarial mutation applied to an artifact."""
    model_config = ConfigDict(frozen=True)

    mutation_id: str
    artifact_type: str
    failure_category: FailureCategory
    target_element_ids: Tuple[str, ...] = Field(default_factory=tuple)
    mutation_description: str
    expected_quality_signal: str
    expected_severity: FailureSeverity
    mutation_params: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create(
        cls,
        mutation_id: str,
        artifact_type: str,
        failure_category: FailureCategory,
        target_element_ids: List[str],
        mutation_description: str,
        expected_quality_signal: str,
        expected_severity: FailureSeverity,
        mutation_params: Dict[str, Any] | None = None,
    ) -> ArtifactMutation:
        return cls(
            mutation_id=mutation_id,
            artifact_type=artifact_type,
            failure_category=failure_category,
            target_element_ids=tuple(target_element_ids),
            mutation_description=mutation_description,
            expected_quality_signal=expected_quality_signal,
            expected_severity=expected_severity,
            mutation_params=mutation_params or {},
        )
