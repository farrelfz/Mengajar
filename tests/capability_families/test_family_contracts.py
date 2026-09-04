"""
Tests for Capability Family parameter specifications and structural validation rules.
"""

import pytest
from pydantic import ValidationError

from app.capabilities.families.contracts import (
    BaseFamilySpec,
    CollectionItem,
    CollectionSpec,
    ComparisonItem,
    ComparisonSpec,
    FamilyTopology,
    HierarchyNode,
    HierarchySpec,
    ProcessSpec,
    ProcessStage,
    ProgressionSpec,
    ProgressionStage,
    ReasoningElement,
    ReasoningSpec,
    RelationshipEdge,
    RelationshipNode,
    RelationshipSpec,
)


def test_process_spec_validation():
    # Valid process
    spec = ProcessSpec(
        title="Scientific Method",
        stages=[
            ProcessStage(id="s1", label="Observation"),
            ProcessStage(id="s2", label="Hypothesis"),
        ],
    )
    assert len(spec.stages) == 2
    assert spec.topology == FamilyTopology.LINEAR

    # Empty stages should raise ValueError
    with pytest.raises(ValidationError):
        ProcessSpec(title="Empty Process", stages=[])


def test_comparison_spec_validation():
    # Valid comparison
    spec = ComparisonSpec(
        title="Qualitative vs Quantitative",
        axes=["Definition", "Data Type"],
        items=[
            ComparisonItem(id="qual", name="Qualitative", attributes={"Definition": "Thematic"}),
            ComparisonItem(id="quant", name="Quantitative", attributes={"Definition": "Numerical"}),
        ],
    )
    assert len(spec.items) == 2

    # Empty items should raise ValidationError
    with pytest.raises(ValidationError):
        ComparisonSpec(title="Empty Comparison", items=[])


def test_relationship_spec_integrity_validation():
    # Valid graph
    spec = RelationshipSpec(
        title="Photosynthesis Variable Map",
        nodes=[
            RelationshipNode(id="n1", label="Light Intensity", category="independent"),
            RelationshipNode(id="n2", label="Growth Rate", category="dependent"),
        ],
        edges=[
            RelationshipEdge(source_id="n1", target_id="n2", label="stimulates"),
        ],
    )
    assert len(spec.nodes) == 2
    assert len(spec.edges) == 1

    # Edge referencing nonexistent node should fail
    with pytest.raises(ValidationError):
        RelationshipSpec(
            title="Broken Graph",
            nodes=[RelationshipNode(id="n1", label="Node 1")],
            edges=[RelationshipEdge(source_id="n1", target_id="n_missing", label="links")],
        )


def test_hierarchy_spec_circular_dependency_rejection():
    # Valid hierarchy
    valid_spec = HierarchySpec(
        title="Biological Taxonomy",
        nodes=[
            HierarchyNode(id="domain", label="Domain", level=1),
            HierarchyNode(id="kingdom", label="Kingdom", parent_id="domain", level=2),
            HierarchyNode(id="phylum", label="Phylum", parent_id="kingdom", level=3),
        ],
    )
    assert len(valid_spec.nodes) == 3

    # Circular dependency A -> B -> A should fail
    with pytest.raises(ValidationError):
        HierarchySpec(
            title="Circular Tree",
            nodes=[
                HierarchyNode(id="node_a", label="A", parent_id="node_b"),
                HierarchyNode(id="node_b", label="B", parent_id="node_a"),
            ],
        )

    # Missing parent should fail
    with pytest.raises(ValidationError):
        HierarchySpec(
            title="Orphan Tree",
            nodes=[
                HierarchyNode(id="node_a", label="A", parent_id="nonexistent_parent"),
            ],
        )


def test_reasoning_spec_validation():
    spec = ReasoningSpec(
        title="Torque Rule",
        elements=[
            ReasoningElement(id="e1", role="premise", statement="Force applied perpendicularly maximizes torque."),
            ReasoningElement(id="e2", role="conclusion", statement="Parallel force creates zero torque."),
        ],
    )
    assert len(spec.elements) == 2

    with pytest.raises(ValidationError):
        ReasoningSpec(title="Empty Reasoning", elements=[])
