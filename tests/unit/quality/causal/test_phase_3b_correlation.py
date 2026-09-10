"""
Universal Document Intelligence System V5 — Phase 3B Failure Correlation Unit Tests.

Tests 1 to 10:
- Spatial proximity scoring (bounding box overlap vs distance)
- Structural proximity (same section/slide/slot)
- Semantic proximity (shared source unit ID)
- Lineage proximity (blueprint element to render element mapping)
- Failure pattern co-occurrence table scoring
- Composite correlation score calculation
- Threshold cutoff behavior
- Determinism across input permutations
- Candidate generation efficiency
- Empty signals list handling
"""

import pytest
from app.quality.causal.contracts import QualityLocation, QualitySignal
from app.quality.causal.correlation_engine import FailureCorrelationEngine
from app.quality.causal.correlation_graph import (
    CorrelationGraph,
    CorrelationRelationshipType,
    CorrelationScoreBreakdown,
)
from app.quality.causal.taxonomy import CanonicalFailureCode, CanonicalFailureDomain, CanonicalSeverity


def _make_signal(
    sig_id: str,
    code: CanonicalFailureCode,
    domain: CanonicalFailureDomain = CanonicalFailureDomain.PHYSICAL_RENDER,
    page: int = 1,
    element_id: str = "elem_1",
    bbox=(10.0, 10.0, 50.0, 50.0),
    source_units=("unit_bio_1",),
    blueprint_elements=("bp_card_1",),
    render_elements=("rnd_box_1",),
    section_index=1,
) -> QualitySignal:
    return QualitySignal(
        signal_id=sig_id,
        source_engine="test_engine",
        failure_domain=domain,
        failure_code=code,
        severity=CanonicalSeverity.MAJOR,
        location=QualityLocation(
            artifact_type="PRESENTATION",
            page_index=page,
            element_id=element_id,
            bounding_box=bbox,
            source_unit_ids=tuple(source_units),
            blueprint_element_ids=tuple(blueprint_elements),
            render_element_ids=tuple(render_elements),
            section_index=section_index,
        ),
        description=f"Test defect {code.value}",
    )


def test_01_spatial_proximity_overlapping_vs_distant():
    """Test 1: Spatial proximity scores higher for overlapping or close bounding boxes than distant ones."""
    engine = FailureCorrelationEngine()
    
    # Overlapping signals on page 1
    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING, page=1, bbox=(10.0, 10.0, 50.0, 50.0))
    s2 = _make_signal("s2", CanonicalFailureCode.TEXT_TOO_SMALL, page=1, bbox=(20.0, 20.0, 60.0, 60.0))
    
    # Distant signals on page 1
    s3 = _make_signal("s3", CanonicalFailureCode.TEXT_TOO_SMALL, page=1, bbox=(800.0, 800.0, 900.0, 900.0), element_id="elem_distant")

    res_close = engine.correlate([s1, s2])
    res_distant = engine.correlate([s1, s3])

    edge_close = res_close.graph.get_edge("s1", "s2")
    edge_distant = res_distant.graph.get_edge("s1", "s3")

    assert edge_close is not None
    assert edge_close.breakdown.spatial > (edge_distant.breakdown.spatial if edge_distant else 0.0)


def test_02_structural_proximity_same_section_and_slot():
    """Test 2: Structural proximity awards bonus for shared blueprint slot and section."""
    engine = FailureCorrelationEngine()
    
    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING, section_index=2, blueprint_elements=("slot_a",), element_id="el_1")
    s2 = _make_signal("s2", CanonicalFailureCode.ELEMENT_COLLISION, section_index=2, blueprint_elements=("slot_a",), element_id="el_2")
    s3 = _make_signal("s3", CanonicalFailureCode.ELEMENT_COLLISION, section_index=5, blueprint_elements=("slot_z",), element_id="el_3")

    res_same = engine.correlate([s1, s2])
    res_diff = engine.correlate([s1, s3])

    edge_same = res_same.graph.get_edge("s1", "s2")
    edge_diff = res_diff.graph.get_edge("s1", "s3")

    assert edge_same is not None
    assert edge_same.breakdown.structural >= 0.80
    if edge_diff:
        assert edge_same.breakdown.structural > edge_diff.breakdown.structural


def test_03_semantic_proximity_shared_source_units():
    """Test 3: Semantic proximity reflects shared source knowledge units."""
    engine = FailureCorrelationEngine()

    s1 = _make_signal("s1", CanonicalFailureCode.UNSUPPORTED_CLAIM, domain=CanonicalFailureDomain.SEMANTIC_TRACEABILITY, source_units=("k_concept_photosynthesis",))
    s2 = _make_signal("s2", CanonicalFailureCode.SOURCE_GROUNDING_FAILURE, domain=CanonicalFailureDomain.SEMANTIC_TRACEABILITY, source_units=("k_concept_photosynthesis",))
    
    res = engine.correlate([s1, s2])
    edge = res.graph.get_edge("s1", "s2")

    assert edge is not None
    assert edge.breakdown.semantic == 1.0


def test_04_lineage_proximity_blueprint_to_render_mapping():
    """Test 4: Lineage proximity links upstream blueprint elements with rendered element IDs."""
    engine = FailureCorrelationEngine()

    s1 = _make_signal("s1", CanonicalFailureCode.BLUEPRINT_CAPACITY_MISMATCH, domain=CanonicalFailureDomain.BLUEPRINT_INTEGRITY, blueprint_elements=("card_hero",))
    s2 = _make_signal("s2", CanonicalFailureCode.TEXT_CLIPPING, blueprint_elements=("card_hero",))

    res = engine.correlate([s1, s2])
    edge = res.graph.get_edge("s1", "s2")

    assert edge is not None
    assert edge.breakdown.lineage >= 0.80


def test_05_failure_pattern_co_occurrence():
    """Test 5: Known high-affinity failure pairs (e.g. TEXT_CLIPPING + TEXT_TOO_SMALL) receive high pattern score."""
    engine = FailureCorrelationEngine()

    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING)
    s2 = _make_signal("s2", CanonicalFailureCode.TEXT_TOO_SMALL)

    res = engine.correlate([s1, s2])
    edge = res.graph.get_edge("s1", "s2")

    assert edge is not None
    assert edge.breakdown.pattern >= 0.90


def test_06_composite_correlation_score_calculation():
    """Test 6: Composite score is a normalized weighted sum across all 5 dimensions."""
    engine = FailureCorrelationEngine()

    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING, page=1)
    s2 = _make_signal("s2", CanonicalFailureCode.TEXT_TOO_SMALL, page=1)

    res = engine.correlate([s1, s2])
    edge = res.graph.get_edge("s1", "s2")
    assert edge is not None

    b = edge.breakdown
    w = engine.config.weights
    expected_score = round(
        w.spatial * b.spatial
        + w.structural * b.structural
        + w.semantic * b.semantic
        + w.lineage * b.lineage
        + w.pattern * b.pattern,
        4,
    )
    assert abs(edge.score - expected_score) < 1e-4


def test_07_threshold_cutoff_rejects_unrelated_signals():
    """Test 7: Weak correlations below min_correlation_threshold do not create edges."""
    engine = FailureCorrelationEngine()

    # Distant pages, different domains, completely disjoint identifiers
    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING, page=1, element_id="el_1", section_index=1, source_units=("u1",), blueprint_elements=("b1",), render_elements=("r1",))
    s2 = _make_signal("s2", CanonicalFailureCode.PDF_CONFORMANCE_VIOLATION, domain=CanonicalFailureDomain.EXPORT_PACKAGING, page=99, element_id="el_99", section_index=99, source_units=("u99",), blueprint_elements=("b99",), render_elements=("r99",))

    res = engine.correlate([s1, s2])
    assert res.graph.get_edge("s1", "s2") is None
    assert "s1" in res.isolated_signals
    assert "s2" in res.isolated_signals


def test_08_determinism_across_input_order():
    """Test 8: Correlation graph edges and scores are strictly identical regardless of input order."""
    engine = FailureCorrelationEngine()

    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING, page=1)
    s2 = _make_signal("s2", CanonicalFailureCode.TEXT_TOO_SMALL, page=1)
    s3 = _make_signal("s3", CanonicalFailureCode.ELEMENT_COLLISION, page=1)

    res_123 = engine.correlate([s1, s2, s3])
    res_321 = engine.correlate([s3, s2, s1])
    res_213 = engine.correlate([s2, s1, s3])

    edges_123 = {(e.signal_a_id, e.signal_b_id): e.score for e in res_123.correlation_edges}
    edges_321 = {(e.signal_a_id, e.signal_b_id): e.score for e in res_321.correlation_edges}
    edges_213 = {(e.signal_a_id, e.signal_b_id): e.score for e in res_213.correlation_edges}

    assert edges_123 == edges_321 == edges_213


def test_09_candidate_generation_indexing():
    """Test 9: Multi-index lookups partition signals so completely disjoint pages/sections are not all-pairs evaluated."""
    engine = FailureCorrelationEngine()

    signals = [
        _make_signal(
            f"sig_p{p}",
            CanonicalFailureCode.TEXT_CLIPPING,
            page=p,
            element_id=f"el_p{p}",
            section_index=p,
            source_units=(f"u_{p}",),
            blueprint_elements=(f"b_{p}",),
            render_elements=(f"r_{p}",),
        )
        for p in range(1, 20)
    ]

    res = engine.correlate(signals)
    # Since every signal is on a different page and has different units/elements/sections, candidate pairs are sparse
    assert len(res.correlation_edges) == 0
    assert len(res.isolated_signals) == 19


def test_10_empty_signals_list_returns_empty_result():
    """Test 10: Correlating an empty list safely returns an empty graph and empty lists."""
    engine = FailureCorrelationEngine()
    res = engine.correlate([])

    assert len(res.graph.nodes) == 0
    assert len(res.graph.edges) == 0
    assert len(res.correlated_groups) == 0
    assert len(res.isolated_signals) == 0
