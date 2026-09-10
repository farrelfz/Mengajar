"""
Universal Document Intelligence System V5 — Failure Correlation Engine.

Phase 3B: Deterministic, multi-dimensional proximity scoring across spatial,
structural, semantic, lineage, and failure-pattern dimensions.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.causal.config import CausalIntelligenceConfig, DEFAULT_CAUSAL_CONFIG
from app.quality.causal.context import QualityCorrelationContext
from app.quality.causal.contracts import QualitySignal
from app.quality.causal.correlation_graph import (
    CorrelationEdge,
    CorrelationGraph,
    CorrelationRelationshipType,
    CorrelationScoreBreakdown,
)


class CorrelationResult(BaseModel):
    """Container holding the complete outcome of failure correlation analysis."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    graph: CorrelationGraph
    correlated_groups: List[List[str]] = Field(default_factory=list)
    correlation_edges: List[CorrelationEdge] = Field(default_factory=list)
    isolated_signals: List[str] = Field(default_factory=list)
    correlation_rationale: Dict[str, Any] = Field(default_factory=dict)


class FailureCorrelationEngine:
    """Deterministic correlation engine executing indexed candidate generation and multi-dimensional scoring."""

    # High-compatibility co-occurrence pairs
    PATTERN_COMPATIBILITY_TABLE: Dict[Tuple[str, str], float] = {
        ("TEXT_CLIPPING", "TEXT_TOO_SMALL"): 0.95,
        ("TEXT_TOO_SMALL", "DENSITY_OVERLOAD"): 0.95,
        ("TEXT_CLIPPING", "ELEMENT_COLLISION"): 0.95,
        ("ELEMENT_COLLISION", "CARD_OVERLOAD"): 0.90,
        ("DENSITY_OVERLOAD", "COGNITIVE_LOAD_OVERFLOW"): 0.95,
        ("WALL_OF_TEXT", "DENSITY_OVERLOAD"): 0.95,
        ("INQUIRY_FLOW_BREAK", "WORKSHEET_SPOILING_FAILURE"): 0.90,
        ("WORKSHEET_WORKSPACE_FAILURE", "WORKSHEET_QUIZ_COLLAPSE"): 0.85,
        ("WORKSHEET_WORKSPACE_INSUFFICIENT", "ELEMENT_COLLISION"): 0.85,
        ("SCIENTIFIC_CITATION_INVISIBLE", "EVIDENCE_DISCIPLINE_FAILURE"): 0.95,
        ("UNSUPPORTED_CLAIM", "SOURCE_GROUNDING_FAILURE"): 0.95,
        ("SCIENTIFIC_EVIDENCE_DETACHED", "TRACEABILITY_BREAK"): 0.90,
        ("LAYOUT_MONOTONY", "REPETITION_STREAK"): 0.95,
        ("LAYOUT_SEMANTIC_MISMATCH", "LAYOUT_CAPACITY_MISMATCH"): 0.90,
        ("PAGE_BOUNDARY_VIOLATION", "TEXT_CLIPPING"): 0.95,
    }

    def __init__(self, config: Optional[CausalIntelligenceConfig] = None):
        self.config = config or DEFAULT_CAUSAL_CONFIG

    def correlate(self, signals: Sequence[QualitySignal]) -> CorrelationResult:
        """Executes end-to-end deterministic correlation on a sequence of QualitySignals."""
        graph = CorrelationGraph()
        if not signals:
            return CorrelationResult(graph=graph)

        # 1. Populate nodes and build contexts
        contexts: Dict[str, QualityCorrelationContext] = {}
        for sig in sorted(signals, key=lambda s: s.signal_id):
            graph.add_signal(sig)
            contexts[sig.signal_id] = QualityCorrelationContext.from_quality_signal(sig)

        # 2. Generate candidate pairs via multi-index inverted lookups
        candidate_pairs = self._generate_candidate_pairs(signals, contexts)

        # 3. Score candidate pairs across the 5 dimensions
        edges: List[CorrelationEdge] = []
        rationales: Dict[str, Any] = {}

        for sig_a_id, sig_b_id in sorted(candidate_pairs):
            sig_a = graph.nodes[sig_a_id]
            sig_b = graph.nodes[sig_b_id]
            ctx_a = contexts[sig_a_id]
            ctx_b = contexts[sig_b_id]

            breakdown, rel_type, evidence_list, dims = self._score_pair(sig_a, sig_b, ctx_a, ctx_b)

            if breakdown.total_score >= self.config.min_correlation_threshold:
                edge = CorrelationEdge(
                    signal_a_id=sig_a_id,
                    signal_b_id=sig_b_id,
                    score=round(breakdown.total_score, 4),
                    breakdown=breakdown,
                    relationship_type=rel_type,
                    evidence=tuple(evidence_list),
                    dimensions=tuple(dims),
                )
                graph.add_edge(edge)
                edges.append(edge)
                rationales[f"{sig_a_id}:{sig_b_id}"] = {
                    "total_score": edge.score,
                    "breakdown": breakdown.to_dict(),
                    "relationship_type": rel_type.value,
                    "evidence": evidence_list,
                }

        # 4. Extract connected components and isolated signals
        raw_components = graph.find_connected_components(min_score=self.config.min_correlation_threshold)
        correlated_groups = [sorted(list(comp)) for comp in raw_components]
        isolated = graph.get_isolated_signals(min_score=self.config.min_correlation_threshold)

        return CorrelationResult(
            graph=graph,
            correlated_groups=correlated_groups,
            correlation_edges=edges,
            isolated_signals=isolated,
            correlation_rationale=rationales,
        )

    def _generate_candidate_pairs(
        self,
        signals: Sequence[QualitySignal],
        contexts: Dict[str, QualityCorrelationContext],
    ) -> Set[Tuple[str, str]]:
        """Constrains search space using spatial, structural, and semantic inverted indexes."""
        by_page: Dict[int, Set[str]] = defaultdict(set)
        by_bp: Dict[str, Set[str]] = defaultdict(set)
        by_ku: Dict[str, Set[str]] = defaultdict(set)
        by_sec: Dict[str, Set[str]] = defaultdict(set)

        for sig in signals:
            sid = sig.signal_id
            ctx = contexts[sid]
            if ctx.page_number is not None:
                by_page[ctx.page_number].add(sid)
            if ctx.blueprint_element_id:
                by_bp[ctx.blueprint_element_id].add(sid)
            if ctx.section_id:
                by_sec[ctx.section_id].add(sid)
            for ku in ctx.knowledge_unit_ids:
                by_ku[ku].add(sid)

        candidates: Set[Tuple[str, str]] = set()

        def add_pairs(group: Set[str]):
            s_list = sorted(group)
            for i in range(len(s_list)):
                for j in range(i + 1, len(s_list)):
                    candidates.add((s_list[i], s_list[j]))

        # Index overlaps
        for grp in by_page.values():
            add_pairs(grp)
        for grp in by_bp.values():
            add_pairs(grp)
        for grp in by_sec.values():
            add_pairs(grp)
        for grp in by_ku.values():
            add_pairs(grp)

        # Adjacent page pairings
        sorted_pages = sorted(by_page.keys())
        for i in range(len(sorted_pages) - 1):
            p1, p2 = sorted_pages[i], sorted_pages[i + 1]
            if abs(p1 - p2) == 1:
                for s1 in by_page[p1]:
                    for s2 in by_page[p2]:
                        pair = (min(s1, s2), max(s1, s2))
                        candidates.add(pair)

        # Fallback for small signal sets (<= 20): check all pairs to guarantee complete recall
        if len(signals) <= 20:
            all_sids = sorted(s.signal_id for s in signals)
            for i in range(len(all_sids)):
                for j in range(i + 1, len(all_sids)):
                    candidates.add((all_sids[i], all_sids[j]))

        return candidates

    def _score_pair(
        self,
        sig_a: QualitySignal,
        sig_b: QualitySignal,
        ctx_a: QualityCorrelationContext,
        ctx_b: QualityCorrelationContext,
    ) -> Tuple[CorrelationScoreBreakdown, CorrelationRelationshipType, List[str], List[str]]:
        """Calculates dimensional component scores for two signals."""
        w = self.config.weights
        evidence: List[str] = []
        dimensions: List[str] = []

        # A. Spatial Proximity
        spatial_score = 0.0
        if ctx_a.element_id and ctx_a.element_id == ctx_b.element_id:
            spatial_score = 1.0
            evidence.append(f"Same element target '{ctx_a.element_id}'")
            dimensions.append("SPATIAL_SAME_ELEMENT")
        elif ctx_a.page_number is not None and ctx_a.page_number == ctx_b.page_number:
            spatial_score = 0.90
            evidence.append(f"Co-located on page {ctx_a.page_number}")
            dimensions.append("SPATIAL_SAME_PAGE")
        elif (
            ctx_a.page_number is not None
            and ctx_b.page_number is not None
            and abs(ctx_a.page_number - ctx_b.page_number) == 1
        ):
            spatial_score = 0.50
            evidence.append(f"Adjacent pages {ctx_a.page_number} and {ctx_b.page_number}")
            dimensions.append("SPATIAL_ADJACENT_PAGE")
        elif ctx_a.section_id and ctx_a.section_id == ctx_b.section_id:
            spatial_score = 0.40
            evidence.append(f"Co-located in section {ctx_a.section_id}")
            dimensions.append("SPATIAL_SAME_SECTION")

        # B. Structural Proximity
        structural_score = 0.0
        if ctx_a.blueprint_element_id and ctx_a.blueprint_element_id == ctx_b.blueprint_element_id:
            structural_score = 1.0
            evidence.append(f"Shared blueprint element '{ctx_a.blueprint_element_id}'")
            dimensions.append("STRUCTURAL_SAME_BLUEPRINT")
        elif ctx_a.element_id and ctx_a.element_id == ctx_b.element_id:
            structural_score = 0.90
            evidence.append(f"Shared element target '{ctx_a.element_id}'")
            dimensions.append("STRUCTURAL_SAME_ELEMENT")
        elif ctx_a.parent_container and ctx_a.parent_container == ctx_b.parent_container:
            structural_score = 0.85
            evidence.append(f"Shared container '{ctx_a.parent_container}'")
            dimensions.append("STRUCTURAL_SAME_CONTAINER")
        elif ctx_a.layout_type and ctx_a.layout_type == ctx_b.layout_type:
            structural_score = 0.50
            evidence.append(f"Same layout type '{ctx_a.layout_type}'")
            dimensions.append("STRUCTURAL_SAME_LAYOUT")

        # C. Semantic Proximity
        semantic_score = 0.0
        shared_kus = set(ctx_a.knowledge_unit_ids).intersection(set(ctx_b.knowledge_unit_ids))
        if shared_kus:
            semantic_score = 1.0
            evidence.append(f"Shared knowledge units: {list(shared_kus)}")
            dimensions.append("SEMANTIC_SHARED_KNOWLEDGE_UNITS")
        elif ctx_a.semantic_role and ctx_a.semantic_role == ctx_b.semantic_role:
            semantic_score = 0.80
            evidence.append(f"Shared semantic role '{ctx_a.semantic_role}'")
            dimensions.append("SEMANTIC_SAME_ROLE")
        elif ctx_a.section_id and ctx_a.section_id == ctx_b.section_id:
            semantic_score = 0.50
            dimensions.append("SEMANTIC_SAME_SECTION")

        # D. Lineage Proximity
        lineage_score = 0.0
        if ctx_a.source_stage and ctx_a.source_stage == ctx_b.source_stage:
            lineage_score = 0.80
            dimensions.append("LINEAGE_SAME_STAGE")
        if ctx_a.render_stage and ctx_a.render_stage == ctx_b.render_stage:
            lineage_score = max(lineage_score, 0.70)
            dimensions.append("LINEAGE_SAME_RENDER_STAGE")
        if structural_score >= 0.85 and spatial_score >= 0.90:
            lineage_score = max(lineage_score, 0.90)
            dimensions.append("LINEAGE_CO_LOCATED_ELEMENT")

        # E. Failure Pattern Compatibility
        pattern_score = 0.10
        code_a = sig_a.failure_code.value
        code_b = sig_b.failure_code.value
        pair_key = (min(code_a, code_b), max(code_a, code_b))

        for (k1, k2), score_val in self.PATTERN_COMPATIBILITY_TABLE.items():
            check_key = (min(k1, k2), max(k1, k2))
            if pair_key == check_key:
                pattern_score = score_val
                evidence.append(f"Pattern compatibility match ({code_a} + {code_b})")
                dimensions.append("PATTERN_COMPATIBLE")
                break

        # If identical defect code in nearby context
        if code_a == code_b and spatial_score > 0:
            pattern_score = max(pattern_score, 0.80)
            dimensions.append("PATTERN_IDENTICAL_CODE")

        # Compute weighted total score
        total_score = (
            w.spatial * spatial_score
            + w.structural * structural_score
            + w.semantic * semantic_score
            + w.lineage * lineage_score
            + w.pattern * pattern_score
        )

        breakdown = CorrelationScoreBreakdown(
            total_score=min(1.0, max(0.0, total_score)),
            spatial=spatial_score,
            structural=structural_score,
            semantic=semantic_score,
            lineage=lineage_score,
            pattern=pattern_score,
        )

        # Determine dominant relationship type
        rel_type = CorrelationRelationshipType.PATTERN_COMPATIBLE
        if structural_score >= 0.85:
            rel_type = CorrelationRelationshipType.STRUCTURALLY_RELATED
        elif spatial_score >= 0.90:
            rel_type = CorrelationRelationshipType.CO_LOCATED
        elif semantic_score >= 0.80:
            rel_type = CorrelationRelationshipType.SEMANTICALLY_RELATED
        elif lineage_score >= 0.80:
            rel_type = CorrelationRelationshipType.LINEAGE_RELATED
        elif pattern_score >= 0.85 and total_score >= 0.75:
            rel_type = CorrelationRelationshipType.CAUSALLY_SUGGESTIVE

        return breakdown, rel_type, evidence, dimensions
