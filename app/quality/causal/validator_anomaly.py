"""
Universal Document Intelligence System V5 — Validator False Positive Detection.

Phase 3B: Conservative detection of conflicting inspector signals to identify
potential validator measurement anomalies without suppressing valid defects.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.causal.causal_taxonomy import (
    CausalArchitecturalLayer,
    CausalConfidenceLevel,
    HypothesisStatus,
    RootCauseCategory,
)
from app.quality.causal.contracts import FailureCluster, RootCauseHypothesis


class ValidatorAnomalyDetector:
    """Detects when contradictory physical inspection evidence suggests a validator anomaly."""

    @classmethod
    def detect_anomaly_hypothesis(
        cls,
        cluster: FailureCluster,
    ) -> Optional[RootCauseHypothesis]:
        """Examines evidence for explicit contradictions indicating a validator defect."""
        contradictions: List[str] = []

        # Check evidence across signals for conflicting engine measurements
        signals_by_engine: Dict[str, List[str]] = {}
        for s in cluster.signals:
            signals_by_engine.setdefault(s.source_engine, []).append(s.failure_code.value)

        # Discrepancy pattern: PyMuPDF reports text clipping or font size defect, but raster shows clean density
        has_raster_evidence = any(
            any("raster" in ev.lower() or "ocr" in ev.lower() for ev in s.raw_metadata.get("evidence", {}))
            for s in cluster.signals
        )
        has_geometry_failure = any(
            s.failure_code.value in ("TEXT_TOO_SMALL", "TEXT_CLIPPING") for s in cluster.signals
        )

        for s in cluster.signals:
            raw_meta = s.raw_metadata or {}
            # Explicit contradiction flags in diagnostic metadata
            if raw_meta.get("conflicting_dom_size") or raw_meta.get("raster_legible_override"):
                contradictions.append(
                    f"Signal '{s.signal_id}' ({s.failure_code.value}) contradicted by DOM/Raster measurement."
                )

        if not contradictions:
            return None

        # Formulate a competitive hypothesis for VALIDATOR_FALSE_POSITIVE
        confidence = 0.70
        return RootCauseHypothesis(
            cause_code=RootCauseCategory.VALIDATOR_FALSE_POSITIVE.value,
            cause_layer=CausalArchitecturalLayer.VALIDATION.value,
            confidence_score=confidence,
            confidence_level=CausalConfidenceLevel.MEDIUM,
            supporting_evidence=tuple(contradictions),
            contradicting_evidence=("Physical geometry inspector initially flagged boundary breach.",),
            affected_scope=cluster.scope,
            repair_authority=CausalArchitecturalLayer.VALIDATION.value,
            confidence_components={
                "overall": confidence,
                "contradiction_proof": 0.85,
            },
            causal_path="Validator threshold or bounding-box heuristic miscalibrated on complex canvas",
            status=HypothesisStatus.CANDIDATE.value,
            explains_signal_ids=tuple(s.signal_id for s in cluster.signals),
        )
