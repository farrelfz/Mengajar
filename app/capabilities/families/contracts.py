"""
KIR AI Document Generation System — Capability Family Contracts.

Defines the core abstractions for Capability Families:
- BaseFamilySpec and family-specific parameter models
- Structural validation rules (cycle detection, node-edge integrity)
- FamilyTemplate protocol for layout and markup generation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field, field_validator, model_validator

from app.capabilities.contracts import CapabilityOutput, CapabilitySpec, RenderTarget
from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)


class FamilyTopology(str, Enum):
    """Structural topologies supported across capability families."""
    LINEAR = "linear"
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    BRANCHING = "branching"
    CYCLIC = "cyclic"
    PIPELINE = "pipeline"
    TREE = "tree"
    LAYERED = "layered"
    MATRIX = "matrix"
    BINARY = "binary"
    LADDER = "ladder"
    NETWORK = "network"


class BaseFamilySpec(CapabilitySpec):
    """Base parameter specification for all capability families."""
    title: str = ""
    subtitle: str | None = None
    theme: str = "default"  # e.g., 'scientific', 'pedagogy', 'analytical', 'mathematics'
    density: DensityProfile = DensityProfile.FOCUSED


# --- 1. Process Family Parameters ---

class ProcessStage(BaseModel):
    id: str
    label: str
    description: str = ""
    badge: str | None = None
    status: str | None = None  # e.g., 'primary', 'active', 'checkpoint'
    meta_info: dict[str, Any] = Field(default_factory=dict)


class ProcessSpec(BaseFamilySpec):
    topology: FamilyTopology = FamilyTopology.LINEAR
    stages: list[ProcessStage] = Field(default_factory=list)
    direction: str = "horizontal"  # 'horizontal' | 'vertical'
    emphasis_index: int | None = None
    show_connectors: bool = True

    @field_validator("stages")
    @classmethod
    def validate_stages_non_empty(cls, v: list[ProcessStage]) -> list[ProcessStage]:
        if not v:
            raise ValueError("ProcessSpec must contain at least 1 stage.")
        return v


# --- 2. Comparison Family Parameters ---

class ComparisonItem(BaseModel):
    id: str
    name: str
    attributes: dict[str, str] = Field(default_factory=dict)
    tag: str | None = None
    highlight: bool = False
    color_role: str | None = None


class ComparisonSpec(BaseFamilySpec):
    topology: FamilyTopology = FamilyTopology.MATRIX
    axes: list[str] = Field(default_factory=list)  # e.g., ['Definition', 'Application', 'Limitation']
    items: list[ComparisonItem] = Field(default_factory=list)
    highlight_dimension: str | None = None

    @field_validator("items")
    @classmethod
    def validate_items_non_empty(cls, v: list[ComparisonItem]) -> list[ComparisonItem]:
        if not v:
            raise ValueError("ComparisonSpec must contain at least 1 comparison item.")
        return v


# --- 3. Relationship Family Parameters ---

class RelationshipNode(BaseModel):
    id: str
    label: str
    category: str = "default"  # e.g. 'independent', 'dependent', 'control'
    description: str = ""


class RelationshipEdge(BaseModel):
    source_id: str
    target_id: str
    label: str = ""
    relation_type: str = "direct"  # 'direct', 'causal', 'correlational', 'inhibits'


class RelationshipSpec(BaseFamilySpec):
    topology: FamilyTopology = FamilyTopology.NETWORK
    nodes: list[RelationshipNode] = Field(default_factory=list)
    edges: list[RelationshipEdge] = Field(default_factory=list)
    directed: bool = True

    @model_validator(mode="after")
    def validate_node_edge_integrity(self) -> RelationshipSpec:
        if not self.nodes:
            raise ValueError("RelationshipSpec must contain at least 1 node.")
        node_ids = {n.id for n in self.nodes}
        for edge in self.edges:
            if edge.source_id not in node_ids:
                raise ValueError(f"Edge source '{edge.source_id}' does not exist in nodes.")
            if edge.target_id not in node_ids:
                raise ValueError(f"Edge target '{edge.target_id}' does not exist in nodes.")
        return self


# --- 4. Hierarchy Family Parameters ---

class HierarchyNode(BaseModel):
    id: str
    label: str
    description: str = ""
    parent_id: str | None = None
    level: int = 1
    badge: str | None = None


class HierarchySpec(BaseFamilySpec):
    topology: FamilyTopology = FamilyTopology.TREE
    nodes: list[HierarchyNode] = Field(default_factory=list)
    root_id: str | None = None

    @model_validator(mode="after")
    def validate_no_cycles(self) -> HierarchySpec:
        if not self.nodes:
            raise ValueError("HierarchySpec must contain at least 1 node.")
        
        node_map = {n.id: n for n in self.nodes}
        # Detect circular references
        for node in self.nodes:
            visited = set()
            curr = node
            while curr and curr.parent_id:
                if curr.id in visited:
                    raise ValueError(f"Circular dependency detected in hierarchy at node '{curr.id}'.")
                visited.add(curr.id)
                if curr.parent_id not in node_map:
                    raise ValueError(f"Parent '{curr.parent_id}' for node '{curr.id}' not found.")
                curr = node_map[curr.parent_id]
        return self


# --- 5. Reasoning Family Parameters ---

class ReasoningElement(BaseModel):
    id: str
    role: str  # 'premise', 'claim', 'evidence', 'warrant', 'conclusion'
    statement: str
    citation_or_data: str | None = None
    badge: str | None = None


class ReasoningSpec(BaseFamilySpec):
    topology: FamilyTopology = FamilyTopology.LINEAR
    elements: list[ReasoningElement] = Field(default_factory=list)
    inference_type: str = "deductive"  # 'deductive', 'inductive', 'falsification'

    @field_validator("elements")
    @classmethod
    def validate_elements_non_empty(cls, v: list[ReasoningElement]) -> list[ReasoningElement]:
        if not v:
            raise ValueError("ReasoningSpec must contain at least 1 reasoning element.")
        return v


# --- 6. Quantitative Family Parameters ---

class TransformationStep(BaseModel):
    step_number: int
    operation: str
    formula: str
    explanation: str = ""


class QuantitativeSpec(BaseFamilySpec):
    topology: FamilyTopology = FamilyTopology.LINEAR
    initial_formula: str
    variables: dict[str, str] = Field(default_factory=dict)
    steps: list[TransformationStep] = Field(default_factory=list)
    final_result: str | None = None


# --- 7. Collection Family Parameters ---

class CollectionItem(BaseModel):
    id: str
    title: str
    content: str
    category: str | None = None
    icon: str | None = None


class CollectionSpec(BaseFamilySpec):
    topology: FamilyTopology = FamilyTopology.MATRIX
    items: list[CollectionItem] = Field(default_factory=list)
    columns: int = 2

    @field_validator("items")
    @classmethod
    def validate_items_non_empty(cls, v: list[CollectionItem]) -> list[CollectionItem]:
        if not v:
            raise ValueError("CollectionSpec must contain at least 1 item.")
        return v


# --- 8. Progression Family Parameters ---

class ProgressionStage(BaseModel):
    level: int
    title: str
    prompt_or_question: str
    cognitive_dimension: str = "recall"  # 'recall', 'conceptual', 'analytical', 'synthesis'
    answer_or_guidance: str | None = None


class ProgressionSpec(BaseFamilySpec):
    topology: FamilyTopology = FamilyTopology.LADDER
    stages: list[ProgressionStage] = Field(default_factory=list)
    progression_type: str = "cognitive_ladder"

    @field_validator("stages")
    @classmethod
    def validate_stages_non_empty(cls, v: list[ProgressionStage]) -> list[ProgressionStage]:
        if not v:
            raise ValueError("ProgressionSpec must contain at least 1 stage.")
        return v


# --- Family Template Contract ---

TSpec = TypeVar("TSpec", bound=BaseFamilySpec)


class FamilyTemplate(ABC, Generic[TSpec]):
    """
    Abstract Base Class for Generative Family Templates.
    
    A FamilyTemplate knows how to render any capability that complies with its
    family parameter specification into valid HTML or SVG assets.
    """
    template_id: str
    family: CapabilityFamily
    spec_model: type[TSpec]
    preferred_render_target: RenderTarget = RenderTarget.HTML

    def validate_spec(self, spec: TSpec) -> bool:
        """Validate structural soundness of spec."""
        return isinstance(spec, self.spec_model)

    @abstractmethod
    def render_html(self, spec: TSpec, context: dict[str, Any] | None = None) -> str:
        """Render structural HTML for this template."""
        pass

    def render_svg(self, spec: TSpec, context: dict[str, Any] | None = None) -> str:
        """Render SVG if supported, or raise NotImplementedError."""
        raise NotImplementedError(f"Template {self.template_id} does not support raw SVG rendering.")

    def render(self, spec: TSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        """Execute template rendering pipeline."""
        cap_id = context.get("capability_id", f"family.{self.template_id}") if context else f"family.{self.template_id}"
        if self.preferred_render_target == RenderTarget.PYTHON_VISUAL:
            svg = self.render_svg(spec, context)
            return CapabilityOutput(
                capability_id=cap_id,
                output_format="svg",
                rendered_content=svg,
                metadata={"family": self.family.value, "template_id": self.template_id},
            )
        else:
            markup = self.render_html(spec, context)
            return CapabilityOutput(
                capability_id=cap_id,
                output_format="html",
                rendered_content=markup,
                metadata={"family": self.family.value, "template_id": self.template_id},
            )
