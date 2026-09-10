"""
Universal Document Intelligence System V5 — Finding Correlation & Double-Counting Engine.

Phase 3A.1: Discovers spatial and causal correlations between quality signals across
different evaluators (render, calibration, fidelity, legacy) to prevent double-counting
and identify singular root causes.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Set, Tuple

from app.quality.contracts.findings import FindingCluster, QualityFinding
from app.quality.contracts.signals import QualitySignal, SignalSeverity
from app.quality.contracts.taxonomy_mapping import (
    map_to_canonical_code,
    map_to_canonical_dimension,
    map_to_canonical_domain,
)


class FindingCorrelationEngine:
    """Correlates co-occurring quality defects and suppresses redundant penalties."""

    # Causal pairs where first code is root cause of second code
    CAUSAL_CORRELATIONS: Dict[str, Set[str]] = {
        "COGNITIVE_OVERLOAD": {"TEXT_CLIPPING", "TEXT_OVERFLOW", "ELEMENT_COLLISION", "FONT_TOO_SMALL"},
        "LAYOUT_MONOTONY": {"TYPOGRAPHIC_COLLAPSE", "VISUAL_HIERARCHY_CONFUSION"},
        "ANTI_SPOILING_BREACH": {"INQUIRY_ARC_BROKEN", "PEDAGOGICAL_STRUCTURE_COLLAPSE"},
        "UNSUPPORTED_SCIENTIFIC_CLAIM": {"MISATTRIBUTED_EVIDENCE", "CONTRADICTORY_CLAIMS"},
        "STRUCTURAL_HIERARCHY_INVERSION": {"NARRATIVE_FRAGMENTATION"},
        "ELEMENT_COLLISION": {"TEXT_CLIPPING"},
    }

    @classmethod
    def correlate_signals(
        cls, signals: List[QualitySignal]
    ) -> Tuple[Tuple[QualityFinding, ...], Tuple[FindingCluster, ...]]:
        """Group co-occurring signals into clusters, deduplicate, and create findings."""
        if not signals:
            return (), ()

        # 1. Group signals by spatial coordinate (page/slide index or element ID or global)
        spatial_groups: Dict[str, List[QualitySignal]] = defaultdict(list)
        for sig in signals:
            key = cls._compute_spatial_key(sig)
            spatial_groups[key].append(sig)

        clusters: List[FindingCluster] = []
        all_canonical_findings: List[QualityFinding] = []

        for key, group in spatial_groups.items():
            if len(group) == 1:
                # Single signal -> single finding and trivial cluster
                sig = group[0]
                fnd = cls._signal_to_finding(sig)
                cluster = FindingCluster(
                    canonical_finding=fnd,
                    correlated_findings=(),
                    contributing_signals=(sig,),
                    affected_pages=sig.location.page_indices,
                    severity=sig.severity,
                    evidence_sources=(sig.source_engine,),
                    correlation_strength=1.0,
                    rationale=f"Isolated finding from {sig.source_engine}",
                )
                clusters.append(cluster)
                all_canonical_findings.append(fnd)
            else:
                # Multiple signals at same location -> correlate and suppress double counting
                cluster = cls._build_cluster(group)
                clusters.append(cluster)
                all_canonical_findings.append(cluster.canonical_finding)

        return tuple(all_canonical_findings), tuple(clusters)

    @classmethod
    def _compute_spatial_key(cls, sig: QualitySignal) -> str:
        """Derives group key based on spatial location and artifact scope."""
        loc = sig.location
        if loc.element_id:
            return f"elem_{loc.element_id}"
        pages = loc.page_indices
        if pages:
            return f"page_{pages[0]}"
        return f"global_{sig.canonical_code}"

    @classmethod
    def _build_cluster(cls, group: List[QualitySignal]) -> FindingCluster:
        """Constructs a correlated cluster from multiple co-occurring signals."""
        # Find dominant signal: highest severity or known root cause
        dominant = group[0]
        for sig in group[1:]:
            # Check if sig has higher severity
            if sig.severity > dominant.severity:
                dominant = sig
            elif sig.severity == dominant.severity:
                # Check causal precedence
                if sig.canonical_code in cls.CAUSAL_CORRELATIONS:
                    dominant = sig

        canonical_finding = cls._signal_to_finding(dominant)
        correlated_findings: List[QualityFinding] = []
        for s in group:
            if s.signal_id != dominant.signal_id:
                correlated_findings.append(cls._signal_to_finding(s))

        all_pages: Set[int] = set()
        evidence_sources: Set[str] = set()
        for s in group:
            all_pages.update(s.location.page_indices)
            evidence_sources.add(s.source_engine)

        return FindingCluster(
            canonical_finding=canonical_finding,
            correlated_findings=tuple(correlated_findings),
            contributing_signals=tuple(group),
            affected_pages=tuple(sorted(all_pages)),
            severity=dominant.severity,
            evidence_sources=tuple(sorted(evidence_sources)),
            correlation_strength=0.9,
            rationale=f"Correlated {len(group)} co-occurring signals at {canonical_finding.affected_section or 'target location'}; primary cause: {dominant.canonical_code}",
        )

    @classmethod
    def _signal_to_finding(cls, sig: QualitySignal) -> QualityFinding:
        """Convert a QualitySignal into a canonical QualityFinding."""
        # Base penalty from severity
        base_penalty = 0.0
        if sig.severity == SignalSeverity.BLOCKING:
            base_penalty = 0.40
        elif sig.severity == SignalSeverity.ERROR:
            base_penalty = 0.25
        elif sig.severity == SignalSeverity.WARNING:
            base_penalty = 0.10
        elif sig.severity == SignalSeverity.INFO:
            base_penalty = 0.02

        pages = sig.location.page_indices
        if sig.location.artifact_type.upper() == "PRESENTATION" or sig.location.slide_index is not None:
            slide_idx = sig.location.slide_index if sig.location.slide_index is not None else (pages[0] if pages else None)
            page_str = f"Slide {slide_idx}" if slide_idx is not None else None
        else:
            page_str = f"Page {pages[0]}" if pages else None

        dim = map_to_canonical_dimension(sig.canonical_code)

        return QualityFinding(
            failure_code=sig.canonical_code,
            domain=sig.domain,
            dimension=dim.value,
            severity=sig.severity,
            artifact_type=sig.location.artifact_type,
            message=sig.description,
            affected_pages=pages,
            affected_elements=(sig.location.element_id,) if sig.location.element_id else (),
            affected_section=page_str,
            repairability=True,
            originating_signal_ids=(sig.signal_id,),
            score_impact=-base_penalty,
            confidence=sig.confidence.numeric_value,
            evidence=sig.raw_metadata,
        )
