"""
Universal Document Intelligence System V5 — Fidelity Contracts.

Phase 2C: Explicit separation of Fidelity from Quality.
Fidelity Validation answers: "Did semantic intent survive the pipeline?"
- semantic_preservation
- structural_preservation
- traceability_preservation
- artifact_contract_preservation
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field


class ArtifactFidelityReport(BaseModel):
    """Authoritative fidelity evaluation report for an artifact.
    
    Measures pipeline contract compliance:
    - Zero dropped source elements
    - Correct page / slide / section bounds
    - Complete traceability links
    - Execution without catastrophic failure
    
    CRITICAL RULE:
    High fidelity MUST NOT automatically imply high quality.
    """
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    semantic_preservation: float = Field(ge=0.0, le=1.0)
    structural_preservation: float = Field(ge=0.0, le=1.0)
    traceability_preservation: float = Field(ge=0.0, le=1.0)
    artifact_contract_preservation: float = Field(ge=0.0, le=1.0)
    execution_reliability: float = Field(default=1.0, ge=0.0, le=1.0)
    overall_fidelity_score: float = Field(ge=0.0, le=1.0)
    is_passing: bool = True
    violations: Tuple[str, ...] = Field(default_factory=tuple)
    warnings: Tuple[str, ...] = Field(default_factory=tuple)
    traceability_stats: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    evaluated_at: float = Field(default_factory=time.time)

    @classmethod
    def compute(
        cls,
        artifact_type: str,
        semantic_preservation: float,
        structural_preservation: float,
        traceability_preservation: float,
        artifact_contract_preservation: float,
        execution_reliability: float = 1.0,
        violations: List[str] | None = None,
        warnings: List[str] | None = None,
        traceability_stats: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> ArtifactFidelityReport:
        v_list = list(violations or [])
        w_list = list(warnings or [])
        
        # Weighted overall fidelity
        overall = round(
            (
                semantic_preservation * 0.30
                + structural_preservation * 0.20
                + traceability_preservation * 0.20
                + artifact_contract_preservation * 0.20
                + execution_reliability * 0.10
            ),
            3,
        )
        is_passing = overall >= 0.85 and len(v_list) == 0

        return cls(
            artifact_type=artifact_type,
            semantic_preservation=round(semantic_preservation, 3),
            structural_preservation=round(structural_preservation, 3),
            traceability_preservation=round(traceability_preservation, 3),
            artifact_contract_preservation=round(artifact_contract_preservation, 3),
            execution_reliability=round(execution_reliability, 3),
            overall_fidelity_score=overall,
            is_passing=is_passing,
            violations=tuple(v_list),
            warnings=tuple(w_list),
            traceability_stats=traceability_stats or {},
            metadata=metadata or {},
        )
