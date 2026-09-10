"""
Unit tests for UniversalKnowledgeGraph, DependencyGraphView, and cycle diagnostics.
"""

from app.intelligence.graph import (
    CycleResolutionStrategy,
    DependencyCycleDiagnostic,
    DependencyGraphView,
    UniversalKnowledgeGraph,
)
from app.intelligence.schemas import (
    ConceptPayload,
    ContentType,
    IntrinsicImportance,
    KnowledgeCategory,
    KnowledgeProvenance,
    KnowledgeRelationship,
    KnowledgeUnit,
    RelationshipEvidence,
    RelationshipOrigin,
    RelationshipType,
)


def _make_unit(unit_id: str, title: str) -> KnowledgeUnit:
    return KnowledgeUnit(
        id=unit_id,
        title=title,
        content_type=ContentType.CONCEPT,
        category=KnowledgeCategory.CORE_CONCEPT,
        intrinsic_importance=IntrinsicImportance.FOUNDATIONAL,
        provenance=KnowledgeProvenance(
            source_document_id="doc1",
            source_section_id="sec1",
            source_section_title="Sec 1",
            raw_snippet=title,
        ),
        payload=ConceptPayload(formal_definition=title),
    )


def test_core_graph_permits_cycles():
    u1 = _make_unit("ku_1", "Classical Physics")
    u2 = _make_unit("ku_2", "Quantum Physics")

    rel1 = KnowledgeRelationship(
        source_unit_id="ku_1",
        target_unit_id="ku_2",
        relationship=RelationshipType.CONTRASTED_WITH,
        evidence=RelationshipEvidence(origin=RelationshipOrigin.EXPLICIT_SOURCE, confidence=1.0),
    )
    rel2 = KnowledgeRelationship(
        source_unit_id="ku_2",
        target_unit_id="ku_1",
        relationship=RelationshipType.CONTRASTED_WITH,
        evidence=RelationshipEvidence(origin=RelationshipOrigin.EXPLICIT_SOURCE, confidence=1.0),
    )

    graph = UniversalKnowledgeGraph(nodes={"ku_1": u1, "ku_2": u2}, edges=[rel1, rel2])
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 2
    assert len(graph.get_outgoing("ku_1")) == 1
    assert len(graph.get_outgoing("ku_2")) == 1


def test_dependency_graph_view_acyclic_sorting():
    u1 = _make_unit("ku_1", "Base Concept")
    u2 = _make_unit("ku_2", "Intermediate Concept")
    u3 = _make_unit("ku_3", "Advanced Concept")

    r1 = KnowledgeRelationship(
        source_unit_id="ku_1",
        target_unit_id="ku_2",
        relationship=RelationshipType.PREREQUISITE_OF,
        evidence=RelationshipEvidence(origin=RelationshipOrigin.DETERMINISTIC_RULE, confidence=0.9),
    )
    r2 = KnowledgeRelationship(
        source_unit_id="ku_2",
        target_unit_id="ku_3",
        relationship=RelationshipType.PREREQUISITE_OF,
        evidence=RelationshipEvidence(origin=RelationshipOrigin.DETERMINISTIC_RULE, confidence=0.9),
    )

    graph = UniversalKnowledgeGraph(nodes={"ku_1": u1, "ku_2": u2, "ku_3": u3}, edges=[r1, r2])
    view = DependencyGraphView.build_from_graph(graph)

    assert len(view.diagnostics) == 0
    assert view.topological_sort_order.index("ku_1") < view.topological_sort_order.index("ku_2")
    assert view.topological_sort_order.index("ku_2") < view.topological_sort_order.index("ku_3")


def test_dependency_graph_view_cycle_detection_excludes_ai_edge_and_logs_diagnostic():
    u1 = _make_unit("ku_1", "Concept A")
    u2 = _make_unit("ku_2", "Concept B")

    # Cycle: ku_1 -> ku_2 (deterministic) and ku_2 -> ku_1 (AI inferred low confidence)
    r1 = KnowledgeRelationship(
        source_unit_id="ku_1",
        target_unit_id="ku_2",
        relationship=RelationshipType.PREREQUISITE_OF,
        evidence=RelationshipEvidence(origin=RelationshipOrigin.EXPLICIT_SOURCE, confidence=1.0),
    )
    r2 = KnowledgeRelationship(
        source_unit_id="ku_2",
        target_unit_id="ku_1",
        relationship=RelationshipType.PREREQUISITE_OF,
        evidence=RelationshipEvidence(origin=RelationshipOrigin.AI_INFERRED, confidence=0.6),
    )

    graph = UniversalKnowledgeGraph(nodes={"ku_1": u1, "ku_2": u2}, edges=[r1, r2])
    
    # Verify core graph is unchanged
    assert len(graph.edges) == 2

    # Build view
    view = DependencyGraphView.build_from_graph(graph)

    # Core graph MUST remain unchanged
    assert len(graph.edges) == 2

    # View should have detected cycle, excluded ku_2->ku_1 edge, and logged diagnostic
    assert len(view.diagnostics) == 1
    assert view.diagnostics[0].resolution_strategy == CycleResolutionStrategy.EXCLUDE_AI_INFERRED
    assert "ku_2->ku_1" in view.diagnostics[0].excluded_edges
    assert len(view.prerequisite_edges) == 1
    assert view.prerequisite_edges[0].source_unit_id == "ku_1"
