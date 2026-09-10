"""
Universal Document Intelligence System V5 — Quality Dimension Normalizer.

Phase 3A.1: Aggregates signals into canonical dimensions across all 4 truth layers,
normalizes metrics using calibrated scales, computes weighted scores, and detects
score degeneracy (universal 1.0 or zero variance).
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Set, Tuple

from app.quality.authority.profiles import ArtifactQualityProfile
from app.quality.contracts.dimensions import CanonicalQualityDimension, QualityDimensionScore
from app.quality.contracts.findings import FindingCluster, QualityFinding
from app.quality.contracts.signals import QualityDomain, QualitySignal, SignalSeverity
from app.quality.contracts.taxonomy_mapping import map_to_canonical_dimension


class QualityDimensionNormalizer:
    """Normalizes metrics and aggregates scores across the four truth layers."""

    LAYER_DIMENSIONS: Dict[str, Tuple[CanonicalQualityDimension, ...]] = {
        "semantic_integrity": (
            CanonicalQualityDimension.SEMANTIC_GROUNDING,
            CanonicalQualityDimension.CLAIM_VERACITY,
            CanonicalQualityDimension.KNOWLEDGE_TRACEABILITY,
        ),
        "artifact_fidelity": (
            CanonicalQualityDimension.BLUEPRINT_FIDELITY,
            CanonicalQualityDimension.ELEMENT_SURVIVAL,
            CanonicalQualityDimension.CONTRACT_COMPLIANCE,
        ),
        "artifact_quality": (
            CanonicalQualityDimension.NARRATIVE_FLOW,
            CanonicalQualityDimension.COGNITIVE_LOAD,
            CanonicalQualityDimension.INQUIRY_STRUCTURE,
            CanonicalQualityDimension.SCIENTIFIC_RIGOR,
            CanonicalQualityDimension.STYLE_DESIGN,
        ),
        "rendered_quality": (
            CanonicalQualityDimension.READABILITY,
            CanonicalQualityDimension.PHYSICAL_GEOMETRY,
            CanonicalQualityDimension.VISUAL_DENSITY,
            CanonicalQualityDimension.PAGE_BALANCE,
        ),
    }

    @classmethod
    def normalize_scale(
        cls,
        raw_val: float,
        min_val: float,
        max_val: float,
        higher_is_better: bool = True,
    ) -> float:
        """Normalizes a raw measurement to [0.0, 1.0] with directional calibration."""
        if math.isclose(min_val, max_val):
            return 1.0
        clamped = max(min_val, min(max_val, raw_val))
        ratio = (clamped - min_val) / (max_val - min_val)
        return ratio if higher_is_better else (1.0 - ratio)

    @classmethod
    def compute_dimension_scores(
        cls,
        signals: Sequence[QualitySignal],
        findings: Sequence[QualityFinding],
        clusters: Sequence[FindingCluster],
        profile: ArtifactQualityProfile,
    ) -> Tuple[Dict[str, QualityDimensionScore], Dict[str, float], float, Dict[str, Any]]:
        """
        Computes all dimension scores, domain scores, overall composite score,
        and runs degeneracy detection.
        """
        # Map findings to canonical dimensions
        dim_findings: Dict[str, List[QualityFinding]] = {dim.value: [] for dim in CanonicalQualityDimension}
        dim_signals: Dict[str, List[QualitySignal]] = {dim.value: [] for dim in CanonicalQualityDimension}

        for fnd in findings:
            dim = fnd.dimension if isinstance(fnd.dimension, str) else getattr(fnd.dimension, "value", str(fnd.dimension))
            if dim in dim_findings:
                dim_findings[dim].append(fnd)
            else:
                c_dim = map_to_canonical_dimension(fnd.failure_code)
                dim_findings[c_dim.value].append(fnd)

        for sig in signals:
            c_dim = map_to_canonical_dimension(sig.canonical_code)
            dim_signals[c_dim.value].append(sig)

        dim_scores: Dict[str, QualityDimensionScore] = {}
        for dim_enum in CanonicalQualityDimension:
            dim_name = dim_enum.value
            f_list = dim_findings.get(dim_name, [])
            s_list = dim_signals.get(dim_name, [])

            # Base score deduction with double-counting suppression
            total_impact = 0.0
            for f in f_list:
                total_impact += abs(f.score_impact)

            score = max(0.0, min(1.0, round(1.0 - total_impact, 3)))
            weight = profile.dimension_weights.get(dim_name, 1.0)
            contributing_sigs = tuple(s.signal_id for s in s_list)
            contributing_fnds = tuple(f.finding_id for f in f_list)

            dim_scores[dim_name] = QualityDimensionScore(
                dimension=dim_name,
                score=score,
                confidence=1.0,
                contributing_signals=contributing_sigs,
                findings=contributing_fnds,
                weight=weight,
                rationale=f"{len(f_list)} findings, {len(s_list)} signals",
            )

        # Compute Domain (Truth Layer) Scores
        domain_scores: Dict[str, float] = {}
        for layer_name, dims in cls.LAYER_DIMENSIONS.items():
            scores = [dim_scores[d.value].score for d in dims if d.value in dim_scores]
            domain_scores[layer_name] = round(sum(scores) / max(1, len(scores)), 3)

        # Compute Overall Weighted Score
        total_weight = 0.0
        weighted_sum = 0.0
        for dim_name, ds in dim_scores.items():
            weighted_sum += ds.score * ds.weight
            total_weight += ds.weight

        overall_score = round(weighted_sum / max(0.001, total_weight), 3)

        # Degeneracy Detection
        degeneracy_info = cls._detect_degeneracy(overall_score, dim_scores, signals, findings)

        return dim_scores, domain_scores, overall_score, degeneracy_info

    @classmethod
    def _detect_degeneracy(
        cls,
        overall_score: float,
        dim_scores: Dict[str, QualityDimensionScore],
        signals: Sequence[QualitySignal],
        findings: Sequence[QualityFinding],
    ) -> Dict[str, Any]:
        """Identifies pathological scoring conditions (universal 1.0 or zero variance)."""
        has_critical_or_blocking = any(
            s.severity in (SignalSeverity.BLOCKING, SignalSeverity.ERROR)
            for s in signals
        ) or any(f.is_blocking() for f in findings)

        has_any_defects = len(signals) > 0 or len(findings) > 0

        # Condition 1: Universal 1.0 with defects present
        universal_one_detected = math.isclose(overall_score, 1.0) and has_any_defects

        # Condition 2: Zero variance across dimensions despite findings
        scores = [ds.score for ds in dim_scores.values()]
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        zero_variance_detected = has_any_defects and math.isclose(variance, 0.0, abs_tol=1e-5)

        return {
            "is_degenerate": universal_one_detected or zero_variance_detected,
            "universal_one": universal_one_detected,
            "zero_variance": zero_variance_detected,
            "score_variance": round(variance, 6),
            "defect_count": len(findings),
        }
