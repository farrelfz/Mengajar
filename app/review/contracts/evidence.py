"""
Universal Document Intelligence System V5 — Review Evidence Contracts.

Phase 6: Multi-modal evidence package aggregating render snapshots, geometry,
semantic traceability, and repair history for expert review.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.review.contracts.enums import EvidenceSufficiencyLevel, ReviewTrigger


class EvidenceSufficiencyResult(BaseModel):
    """Assessment of evidence completeness across 5 key dimensions."""
    model_config = ConfigDict(frozen=True)

    overall_sufficiency: EvidenceSufficiencyLevel
    geometric_evidence: bool = True
    semantic_evidence: bool = True
    traceability_evidence: bool = True
    repair_history_evidence: bool = True
    provenance_completeness: bool = True
    missing_evidence_details: Tuple[str, ...] = Field(default_factory=tuple)
    explanation: str = ""


class ReviewEvidencePackage(BaseModel):
    """Complete, self-contained forensic evidence package presented to reviewers."""
    model_config = ConfigDict(frozen=True)

    package_id: str = Field(default_factory=lambda: f"evpkg_{uuid.uuid4().hex[:8]}")
    case_id: str
    artifact_id: str
    artifact_type: str
    trigger: ReviewTrigger
    current_state: str
    quality_decision: str
    hard_blockers: Tuple[str, ...] = Field(default_factory=tuple)
    findings: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    signals: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    raw_measurements: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    render_snapshot_paths: Tuple[str, ...] = Field(default_factory=tuple)
    bounding_boxes: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    semantic_traceability: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    repair_history: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    failed_strategies: Tuple[str, ...] = Field(default_factory=tuple)
    root_cause_analysis: Dict[str, Any] = Field(default_factory=dict)
    causal_reach: Dict[str, Any] = Field(default_factory=dict)
    convergence_history: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    benchmark_comparison: Optional[Dict[str, Any]] = None
    historical_baseline: Optional[Dict[str, float]] = None
    relevant_safety_invariants: Tuple[str, ...] = Field(default_factory=tuple)
    sufficiency: EvidenceSufficiencyResult
    assembled_at: float = Field(default_factory=time.time)
