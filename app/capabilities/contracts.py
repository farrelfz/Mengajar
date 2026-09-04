"""
KIR AI Document Intelligence — Capability Contracts.

Defines the contract for all reusable, parameterized library capabilities.
Every capability declares its identity, input model, supported artifacts,
semantic tags, deterministic renderer, and optional decentralized parameter extractor.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar
from pydantic import BaseModel, Field

from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)
from app.design.schemas import ComponentFamily
from app.rendering.schemas import RenderTarget


class CapabilityMetadata(BaseModel):
    """Metadata describing a capability's identity, category, grammar taxonomy, and compatibility."""
    capability_id: str  # e.g., "physics.mechanics.torque_diagram"
    category: str       # e.g., "scientific_visualization", "pedagogy", "mathematics", "diagram", "presentation"
    display_name: str
    description: str
    semantic_tags: list[str] = Field(default_factory=list)
    supported_artifacts: list[str] = Field(default_factory=lambda: ["presentation", "document", "poster", "worksheet"])
    domain: str = "general"
    complexity_score: float = 1.0  # 1.0 (simple card) to 5.0 (complex multi-stage simulation/diagram)
    min_width_px: int = 400
    min_height_px: int = 200
    preferred_renderer: str = "svg"  # "svg", "html", "matplotlib", "reportlab"
    taxonomy: TaxonomySignature | None = None

    @property
    def family(self) -> CapabilityFamily:
        if self.taxonomy:
            return self.taxonomy.family
        if "physics" in self.capability_id:
            return CapabilityFamily.SPATIAL_SYSTEMS
        if "worked_example" in self.capability_id or "derivation" in self.capability_id:
            return CapabilityFamily.STEPWISE_REASONING
        if "misconception" in self.capability_id or "gap" in self.capability_id:
            return CapabilityFamily.COMPARATIVE_REASONING
        if "hero" in self.capability_id:
            return CapabilityFamily.TITLE_FRAMING
        if "concept" in self.capability_id:
            return CapabilityFamily.CONCEPT_STRUCTURE
        if "funnel" in self.capability_id or "pathway" in self.capability_id or "flow" in self.capability_id:
            return CapabilityFamily.PROCESS_VISUALIZATION
        return CapabilityFamily.CONCEPT_STRUCTURE

    @property
    def primary_intent(self) -> SemanticIntent:
        if self.taxonomy:
            return self.taxonomy.primary_intent
        if "hero" in self.capability_id:
            return SemanticIntent.HOOK
        if "misconception" in self.capability_id or "gap" in self.capability_id:
            return SemanticIntent.COMPARE
        if "derivation" in self.capability_id:
            return SemanticIntent.DERIVE
        if "funnel" in self.capability_id:
            return SemanticIntent.NARROW_SCOPE
        if "hypothesis" in self.capability_id:
            return SemanticIntent.INVESTIGATE
        return SemanticIntent.EXPLAIN

    @property
    def structure(self) -> InformationStructure:
        if self.taxonomy:
            return self.taxonomy.structure
        if "physics" in self.capability_id:
            return InformationStructure.SPATIAL_SYSTEM
        if "worked_example" in self.capability_id or "derivation" in self.capability_id:
            return InformationStructure.TRANSFORMATION
        if "misconception" in self.capability_id or "gap" in self.capability_id:
            return InformationStructure.MATRIX
        if "funnel" in self.capability_id:
            return InformationStructure.HIERARCHY
        if "pathway" in self.capability_id or "flow" in self.capability_id:
            return InformationStructure.LINEAR_SEQUENCE
        return InformationStructure.SINGLE_ENTITY

    @property
    def pedagogical_role(self) -> PedagogicalRole:
        if self.taxonomy:
            return self.taxonomy.pedagogical_role
        if "hero" in self.capability_id:
            return PedagogicalRole.HOOK
        if "concept" in self.capability_id:
            return PedagogicalRole.INTRODUCTION
        if "worked_example" in self.capability_id:
            return PedagogicalRole.WORKED_EXAMPLE
        if "misconception" in self.capability_id:
            return PedagogicalRole.MISCONCEPTION
        return PedagogicalRole.EXPLANATION

    @property
    def visual_grammar(self) -> VisualGrammar:
        if self.taxonomy:
            return self.taxonomy.visual_grammar
        if "hero" in self.capability_id:
            return VisualGrammar.HERO
        if "concept" in self.capability_id:
            return VisualGrammar.CONCEPT_PANEL
        if "physics" in self.capability_id:
            return VisualGrammar.ANNOTATED_DIAGRAM
        if "funnel" in self.capability_id:
            return VisualGrammar.FUNNEL
        if "misconception" in self.capability_id:
            return VisualGrammar.COMPARISON
        if "gap" in self.capability_id or "matrix" in self.capability_id:
            return VisualGrammar.MATRIX
        return VisualGrammar.CONCEPT_PANEL

    @property
    def density(self) -> DensityProfile:
        if self.taxonomy:
            return self.taxonomy.density
        if "hero" in self.capability_id:
            return DensityProfile.MINIMAL
        if "matrix" in self.capability_id or "methodology" in self.capability_id:
            return DensityProfile.DENSE_REFERENCE
        if "worked_example" in self.capability_id or "derivation" in self.capability_id:
            return DensityProfile.ANALYTICAL
        return DensityProfile.FOCUSED

    @property
    def component_family(self) -> ComponentFamily:
        """Derive the corresponding ComponentFamily directly from metadata."""
        if self.preferred_renderer in ("svg", "reportlab", "matplotlib") or self.category in ("scientific_visualization", "diagram"):
            return ComponentFamily.DIAGRAM_PLACEHOLDER
        if self.category == "presentation" and "hero" in self.capability_id:
            return ComponentFamily.TITLE_BLOCK
        if self.category in ("pedagogy", "mathematics", "research_education"):
            return ComponentFamily.KEY_STATEMENT
        return ComponentFamily.TEXT_BLOCK

    @property
    def render_target(self) -> RenderTarget:
        """Derive the corresponding RenderTarget directly from metadata."""
        if self.preferred_renderer in ("svg", "reportlab"):
            return RenderTarget.REPORTLAB
        if self.preferred_renderer == "matplotlib":
            return RenderTarget.PYTHON_VISUAL
        return RenderTarget.HTML


class CapabilitySpec(BaseModel):
    """Base specification model for parameterized capability inputs."""
    title: str | None = None
    custom_params: dict[str, Any] = Field(default_factory=dict)


SpecT = TypeVar("SpecT", bound=CapabilitySpec)


class CapabilityOutput(BaseModel):
    """Rendered output payload from a capability."""
    capability_id: str
    output_format: str  # "svg", "html", "png", "json"
    rendered_content: str  # Raw SVG string, HTML snippet, or file path
    asset_path: str | None = None
    width_px: int = 600
    height_px: int = 400
    metadata: dict[str, Any] = Field(default_factory=dict)


class CapabilityRenderer(ABC, Generic[SpecT]):
    """Abstract Base Class for deterministic capability rendering."""

    @abstractmethod
    def validate_spec(self, spec: SpecT) -> bool:
        """Validate that the spec meets constraints before rendering."""
        pass

    @abstractmethod
    def measure(self, spec: SpecT, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Estimate dimensions, density, and rendering constraints."""
        pass

    @abstractmethod
    def render(self, spec: SpecT, context: dict[str, Any] | None = None) -> CapabilityOutput:
        """Deterministically render the specification into an output payload."""
        pass


class Capability(BaseModel, Generic[SpecT]):
    """Unified container for a registered capability with decentralized parameter extraction."""
    metadata: CapabilityMetadata
    spec_model: type[SpecT]
    renderer: CapabilityRenderer[SpecT]
    parameter_extractor: Callable[[Any, Any], dict[str, Any]] | None = None

    model_config = {"arbitrary_types_allowed": True}

    def extract_parameters(self, step: Any, material: Any) -> dict[str, Any]:
        """Extract domain-specific parameters from pedagogical step and semantic material."""
        if self.parameter_extractor:
            try:
                return self.parameter_extractor(step, material)
            except Exception:
                return {}
        return {}
