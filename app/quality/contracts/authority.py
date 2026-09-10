"""
Universal Document Intelligence System V5 — Unified Quality Authority Report Contract.

Phase 3A.1: Master consolidated quality report issued exclusively by the
UnifiedQualityAuthority aggregating all 4 truth layers with explicit provenance.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.decisions import ExportDecision, UnifiedQualityDecision
from app.quality.contracts.dimensions import QualityDimensionScore
from app.quality.contracts.findings import FindingCluster, QualityFinding
from app.quality.contracts.provenance import QualityProvenanceGraph


class UnifiedQualityReport(BaseModel):
    """Authoritative consolidated diagnostic report aggregating all 4 truth layers."""
    model_config = ConfigDict(frozen=True)

    report_id: str = Field(default_factory=lambda: f"uqr_{uuid.uuid4().hex[:8]}")
    artifact_type: str
    decision: ExportDecision
    can_export: bool
    repair_required: bool
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    domain_scores: Dict[str, float] = Field(default_factory=dict)
    
    # 4 Orthogonal Truth Layers
    semantic_integrity: Dict[str, Any] = Field(default_factory=dict)
    artifact_fidelity: Dict[str, Any] = Field(default_factory=dict)
    artifact_quality: Dict[str, Any] = Field(default_factory=dict)
    rendered_quality: Dict[str, Any] = Field(default_factory=dict)

    # Detailed Dimension Breakdown
    dimension_scores: Dict[str, QualityDimensionScore] = Field(default_factory=dict)
    
    # Structured Findings & Clusters
    findings: Tuple[QualityFinding, ...] = Field(default_factory=tuple)
    finding_clusters: Tuple[FindingCluster, ...] = Field(default_factory=tuple)
    causal_diagnoses: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    
    # Statistical Diagnostics
    score_distribution: Dict[str, float] = Field(default_factory=dict)
    provenance: QualityProvenanceGraph = Field(default_factory=QualityProvenanceGraph)
    hard_blockers: Tuple[str, ...] = Field(default_factory=tuple)
    warnings: Tuple[str, ...] = Field(default_factory=tuple)
    summary: str = ""
    timestamp: float = Field(default_factory=time.time)
