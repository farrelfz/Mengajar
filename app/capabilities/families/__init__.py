"""
KIR AI Document Generation System — Capability Families.

Exports the Capability Family architecture, contracts, templates, registry, and factory.
"""

from app.capabilities.families.contracts import (
    BaseFamilySpec,
    CollectionItem,
    CollectionSpec,
    ComparisonItem,
    ComparisonSpec,
    FamilyTemplate,
    FamilyTopology,
    HierarchyNode,
    HierarchySpec,
    ProcessSpec,
    ProcessStage,
    ProgressionSpec,
    ProgressionStage,
    QuantitativeSpec,
    ReasoningElement,
    ReasoningSpec,
    RelationshipEdge,
    RelationshipNode,
    RelationshipSpec,
    TransformationStep,
)
from app.capabilities.families.factory import (
    FamilyTemplateRendererAdapter,
    create_family_capability,
    register_family_capability,
)
from app.capabilities.families.registry import (
    FamilyTemplateRegistry,
    get_default_family_registry,
)
from app.capabilities.families.templates import (
    CardCollectionTemplate,
    EvidenceChainTemplate,
    HierarchyTreeTemplate,
    LinearProcessTemplate,
    MatrixComparisonTemplate,
    ProgressionLadderTemplate,
    QuantitativeDerivationTemplate,
    RelationshipMapTemplate,
)

__all__ = [
    "BaseFamilySpec",
    "FamilyTopology",
    "ProcessStage",
    "ProcessSpec",
    "ComparisonItem",
    "ComparisonSpec",
    "RelationshipNode",
    "RelationshipEdge",
    "RelationshipSpec",
    "HierarchyNode",
    "HierarchySpec",
    "ReasoningElement",
    "ReasoningSpec",
    "TransformationStep",
    "QuantitativeSpec",
    "CollectionItem",
    "CollectionSpec",
    "ProgressionStage",
    "ProgressionSpec",
    "FamilyTemplate",
    "LinearProcessTemplate",
    "MatrixComparisonTemplate",
    "HierarchyTreeTemplate",
    "EvidenceChainTemplate",
    "ProgressionLadderTemplate",
    "QuantitativeDerivationTemplate",
    "RelationshipMapTemplate",
    "CardCollectionTemplate",
    "FamilyTemplateRegistry",
    "get_default_family_registry",
    "FamilyTemplateRendererAdapter",
    "create_family_capability",
    "register_family_capability",
]
