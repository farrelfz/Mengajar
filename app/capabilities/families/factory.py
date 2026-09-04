"""
KIR AI Document Generation System — Capability Family Factory.

Allows instantaneous creation and registration of domain-specific semantic capabilities
by parameterizing Generative Family Templates, without writing dedicated renderer classes.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from app.blueprints.content import ContentBlueprint
from app.blueprints.pedagogical import PedagogicalStep
from app.capabilities.contracts import (
    Capability,
    CapabilityMetadata,
    CapabilityOutput,
    CapabilityRenderer,
    CapabilitySpec,
    RenderTarget,
)
from app.capabilities.families.contracts import BaseFamilySpec, FamilyTemplate
from app.capabilities.families.registry import get_default_family_registry
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)

logger = logging.getLogger(__name__)


class FamilyTemplateRendererAdapter(CapabilityRenderer[Any]):
    """Adapts a FamilyTemplate to the standard CapabilityRenderer contract."""

    def __init__(self, template: FamilyTemplate[Any], capability_id: str = "") -> None:
        self.template = template
        self.capability_id = capability_id

    def validate_spec(self, spec: Any) -> bool:
        return self.template.validate_spec(spec)

    def measure(self, spec: Any, context: dict[str, Any] | None = None) -> tuple[float, float]:
        # Standard responsive bounds
        return (400.0, 200.0)

    def render(self, spec: Any, context: dict[str, Any] | None = None) -> CapabilityOutput:
        ctx = dict(context or {})
        if "capability_id" not in ctx and self.capability_id:
            ctx["capability_id"] = self.capability_id
        return self.template.render(spec, context=ctx)


def create_family_capability(
    capability_id: str,
    template_id: str,
    metadata: CapabilityMetadata,
    parameter_extractor: Callable[[PedagogicalStep, ContentBlueprint, dict[str, Any]], dict[str, Any] | BaseFamilySpec] | None = None,
    spec_model: type[CapabilitySpec] | None = None,
) -> Capability:
    """
    Factory function to construct a complete Capability from a FamilyTemplate.
    """
    family_reg = get_default_family_registry()
    template = family_reg.get(template_id)
    if template is None:
        raise ValueError(f"Family template '{template_id}' is not registered in FamilyTemplateRegistry.")

    # Validate family taxonomy compatibility
    if metadata.taxonomy and metadata.taxonomy.family != template.family:
        raise ValueError(
            f"Capability '{capability_id}' declared family '{metadata.taxonomy.family}' "
            f"which is incompatible with template '{template_id}' (family '{template.family}')."
        )

    # Ensure taxonomy signature exists
    if metadata.taxonomy is None:
        metadata.taxonomy = TaxonomySignature(
            family=template.family,
            primary_intent=SemanticIntent.EXPLAIN,
            structure=InformationStructure.LINEAR_SEQUENCE,
            pedagogical_role=PedagogicalRole.EXPLANATION,
            visual_grammar=VisualGrammar.CONCEPT_PANEL,
            density=DensityProfile.FOCUSED,
            preferred_formats=["presentation_16_9", "a4_portrait", "a4_landscape"],
        )

    # Adapter renderer
    renderer = FamilyTemplateRendererAdapter(template, capability_id=capability_id)
    target_spec_model = spec_model or template.spec_model

    return Capability(
        metadata=metadata,
        spec_model=target_spec_model,
        renderer=renderer,
        parameter_extractor=parameter_extractor,
    )


def register_family_capability(
    registry: CapabilityRegistry,
    capability_id: str,
    template_id: str,
    metadata: CapabilityMetadata,
    parameter_extractor: Callable[[PedagogicalStep, ContentBlueprint, dict[str, Any]], dict[str, Any] | BaseFamilySpec] | None = None,
    spec_model: type[CapabilitySpec] | None = None,
    overwrite: bool = True,
) -> Capability:
    """
    Generates a Capability from a FamilyTemplate and registers it directly into CapabilityRegistry.
    """
    cap = create_family_capability(
        capability_id=capability_id,
        template_id=template_id,
        metadata=metadata,
        parameter_extractor=parameter_extractor,
        spec_model=spec_model,
    )
    registry.register(cap, overwrite=overwrite)
    return cap
