"""
Universal Document Intelligence System V5 — Phase 3B Failure Clustering Unit Tests.

Tests 11 to 18:
- Connected component partitioning
- Deterministic cluster IDs
- Isolated signal handling
- Dominant failure pattern extraction
- Scope determination: LOCAL
- Scope determination: CLUSTER
- Scope determination: SYSTEMIC
- Scope determination: ARTIFACT_WIDE
"""

import pytest
from app.quality.causal.cluster_builder import FailureClusterBuilder
from app.quality.causal.contracts import QualityLocation, QualitySignal
from app.quality.causal.correlation_engine import FailureCorrelationEngine
from app.quality.causal.taxonomy import (
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalSeverity,
    FailureScope,
)


def _make_signal(
    sig_id: str,
    code: CanonicalFailureCode,
    domain: CanonicalFailureDomain = CanonicalFailureDomain.PHYSICAL_RENDER,
    page: int = 1,
    element_id: str = "elem_1",
    bbox=(10.0, 10.0, 50.0, 50.0),
    source_units=("unit_1",),
    blueprint_elements=("bp_1",),
    render_elements=("rnd_1",),
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


def test_11_connected_component_partitioning():
    """Test 11: Two disjoint groups of correlated signals partition into exactly two distinct clusters."""
    corr_engine = FailureCorrelationEngine()
    builder = FailureClusterBuilder()

    # Group 1 on page 1
    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING, page=1, element_id="el_p1_a")
    s2 = _make_signal("s2", CanonicalFailureCode.TEXT_TOO_SMALL, page=1, element_id="el_p1_b")

    # Group 2 on page 5
    s3 = _make_signal("s3", CanonicalFailureCode.UNSUPPORTED_CLAIM, domain=CanonicalFailureDomain.SEMANTIC_TRACEABILITY, page=5, element_id="el_p5_a", source_units=("u5",), blueprint_elements=("b5",), render_elements=("r5",), section_index=5)
    s4 = _make_signal("s4", CanonicalFailureCode.SOURCE_GROUNDING_FAILURE, domain=CanonicalFailureDomain.SEMANTIC_TRACEABILITY, page=5, element_id="el_p5_b", source_units=("u5",), blueprint_elements=("b5",), render_elements=("r5",), section_index=5)

    corr_res = corr_engine.correlate([s1, s2, s3, s4])
    clusters = builder.build_clusters(corr_res, total_pages=10, artifact_type="PRESENTATION")

    assert len(clusters) == 2
    c_p1 = next(c for c in clusters if 1 in c.affected_pages)
    c_p5 = next(c for c in clusters if 5 in c.affected_pages)

    assert set(s.signal_id for s in c_p1.signals) == {"s1", "s2"}
    assert set(s.signal_id for s in c_p5.signals) == {"s3", "s4"}


def test_12_deterministic_cluster_ids():
    """Test 12: Cluster IDs are cryptographically hashed from sorted member signals and remain identical across runs."""
    corr_engine = FailureCorrelationEngine()
    builder = FailureClusterBuilder()

    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING, page=1)
    s2 = _make_signal("s2", CanonicalFailureCode.TEXT_TOO_SMALL, page=1)

    clusters_run1 = builder.build_clusters(corr_engine.correlate([s1, s2]), total_pages=5)
    clusters_run2 = builder.build_clusters(corr_engine.correlate([s2, s1]), total_pages=5)

    assert clusters_run1[0].cluster_id == clusters_run2[0].cluster_id
    assert clusters_run1[0].cluster_id.startswith("clust_")


def test_13_isolated_signals_become_singleton_clusters():
    """Test 13: Signals that do not correlate with any others become clean singleton clusters."""
    corr_engine = FailureCorrelationEngine()
    builder = FailureClusterBuilder()

    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING, page=1, element_id="el1", source_units=("u1",), blueprint_elements=("b1",), render_elements=("r1",), section_index=1)
    s2 = _make_signal("s2", CanonicalFailureCode.METADATA_CORRUPTION, domain=CanonicalFailureDomain.EXPORT_PACKAGING, page=10, element_id="el10", source_units=("u10",), blueprint_elements=("b10",), render_elements=("r10",), section_index=10)

    corr_res = corr_engine.correlate([s1, s2])
    assert len(corr_res.isolated_signals) == 2

    clusters = builder.build_clusters(corr_res, total_pages=10)
    assert len(clusters) == 2
    assert all(len(c.signals) == 1 for c in clusters)


def test_14_dominant_failure_patterns_extraction():
    """Test 14: Dominant failure patterns are extracted and ranked by frequency."""
    corr_engine = FailureCorrelationEngine()
    builder = FailureClusterBuilder()

    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING, page=1, element_id="e1")
    s2 = _make_signal("s2", CanonicalFailureCode.TEXT_CLIPPING, page=1, element_id="e2")
    s3 = _make_signal("s3", CanonicalFailureCode.TEXT_TOO_SMALL, page=1, element_id="e3")

    corr_res = corr_engine.correlate([s1, s2, s3])
    clusters = builder.build_clusters(corr_res, total_pages=5)

    assert len(clusters) == 1
    assert clusters[0].dominant_failure_patterns[0] == "TEXT_CLIPPING"


def test_15_scope_determination_local():
    """Test 15: Defects isolated to 1 page in a 10-page document resolve to LOCAL scope."""
    corr_engine = FailureCorrelationEngine()
    builder = FailureClusterBuilder()

    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING, page=2)
    s2 = _make_signal("s2", CanonicalFailureCode.TEXT_TOO_SMALL, page=2)

    clusters = builder.build_clusters(corr_engine.correlate([s1, s2]), total_pages=10, artifact_type="PRESENTATION")
    assert clusters[0].scope == FailureScope.LOCAL


def test_16_scope_determination_cluster_streak():
    """Test 16: Consecutive streak of 3-4 slides resolves to CLUSTER scope."""
    corr_engine = FailureCorrelationEngine()
    builder = FailureClusterBuilder()

    # Correlated across pages 3, 4, 5 sharing section and source unit
    signals = [
        _make_signal(f"s_{p}", CanonicalFailureCode.LAYOUT_MONOTONY, domain=CanonicalFailureDomain.STYLE_DESIGN, page=p, element_id=f"el_{p}", source_units=("unit_main",), blueprint_elements=("bp_main",), render_elements=("rnd_main",), section_index=2)
        for p in (3, 4, 5)
    ]

    clusters = builder.build_clusters(corr_engine.correlate(signals), total_pages=12, artifact_type="PRESENTATION")
    assert clusters[0].scope == FailureScope.CLUSTER


def test_17_scope_determination_systemic():
    """Test 17: Defects spanning > 50% of document pages resolve to SYSTEMIC scope."""
    corr_engine = FailureCorrelationEngine()
    builder = FailureClusterBuilder()

    signals = [
        _make_signal(f"s_{p}", CanonicalFailureCode.TEXT_TOO_SMALL, page=p, element_id=f"el_{p}", source_units=("unit_global",), blueprint_elements=("bp_global",), render_elements=("rnd_global",), section_index=1)
        for p in (1, 2, 3, 4, 5, 6, 7)
    ]

    clusters = builder.build_clusters(corr_engine.correlate(signals), total_pages=10, artifact_type="PRESENTATION")
    assert clusters[0].scope == FailureScope.SYSTEMIC


def test_18_scope_determination_artifact_wide_global_invariant():
    """Test 18: Global invariant codes (e.g. SCIENTIFIC_CITATION_INVISIBLE or WORKSHEET_SPOILING_FAILURE) resolve unconditionally to ARTIFACT_WIDE scope."""
    corr_engine = FailureCorrelationEngine()
    builder = FailureClusterBuilder()

    s1 = _make_signal(
        "s1",
        CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE,
        domain=CanonicalFailureDomain.SCIENTIFIC_RIGOR,
        page=1,
    )

    corr_res = corr_engine.correlate([s1])
    # Include in groups
    corr_res.correlated_groups = [["s1"]]
    clusters = builder.build_clusters(corr_res, total_pages=20, artifact_type="SCIENTIFIC_DOCUMENT")

    assert clusters[0].scope == FailureScope.ARTIFACT_WIDE
