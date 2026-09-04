"""
Stress testing CapabilityRegistry and Resolver V2 with 100+ registered capabilities.
"""

import time
import pytest

from app.capabilities.contracts import Capability, CapabilityMetadata, CapabilityOutput, CapabilityRenderer, CapabilitySpec
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.resolver import LibraryResolver
from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)
from app.blueprints.production import ProductionBlueprint, ProductionRequirement, SemanticIntentSpec, TargetArtifactType


class DummySpec(CapabilitySpec):
    pass

class DummyRenderer(CapabilityRenderer[DummySpec]):
    def validate_spec(self, spec: DummySpec) -> bool:
        return True
    def measure(self, spec: DummySpec, context=None):
        return {"height_px": 200}
    def render(self, spec: DummySpec, context=None) -> CapabilityOutput:
        return CapabilityOutput(capability_id="dummy", output_format="html", rendered_content="<div>Dummy</div>")


def test_registry_100_capabilities_scale():
    """Verify registry scaling, sub-50ms query latency, and duplicate prevention with 120 capabilities."""
    reg = CapabilityRegistry()

    families = list(CapabilityFamily)
    intents = list(SemanticIntent)
    structures = list(InformationStructure)
    roles = list(PedagogicalRole)
    grammars = list(VisualGrammar)

    t_start = time.perf_counter()
    # Register 120 unique synthetic capabilities
    for i in range(120):
        cap_id = f"test.scale.cap_{i:03d}"
        fam = families[i % len(families)]
        intent = intents[i % len(intents)]
        struct = structures[i % len(structures)]
        role = roles[i % len(roles)]
        gram = grammars[i % len(grammars)]

        meta = CapabilityMetadata(
            capability_id=cap_id,
            category="scale_test",
            display_name=f"Scale Test Cap {i}",
            description=f"Synthetic test capability #{i}",
            semantic_tags=[f"tag_{i%10}", "synthetic", intent.value],
            domain="test_domain",
            taxonomy=TaxonomySignature(
                family=fam,
                primary_intent=intent,
                structure=struct,
                pedagogical_role=role,
                visual_grammar=gram,
                density=DensityProfile.FOCUSED,
            ),
        )
        cap = Capability(
            metadata=meta,
            spec_model=DummySpec,
            renderer=DummyRenderer(),
        )
        reg.register(cap)

    t_register = time.perf_counter() - t_start
    assert len(reg.list_all()) == 120
    assert t_register < 0.1  # Registration of 120 capabilities takes < 100ms

    # Duplicate registration check
    with pytest.raises(ValueError, match="already registered"):
        reg.register(cap, overwrite=False)

    # Intersection query benchmark
    t_query_start = time.perf_counter()
    for _ in range(50):
        found = reg.find(
            semantic_intent=SemanticIntent.COMPARE,
            information_structure=InformationStructure.MATRIX,
        )
        assert isinstance(found, list)

    t_query = (time.perf_counter() - t_query_start) / 50
    assert t_query < 0.001  # < 1 millisecond per intersection query!

    # Resolver resolution speed across 120 capabilities
    resolver = LibraryResolver(registry=reg)
    pb = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[
            ProductionRequirement(
                step_id=f"step_{j}",
                semantic_type="scale_test",
                semantic_intent=SemanticIntentSpec(semantic_intent="compare", domain="test_domain"),
            )
            for j in range(5)
        ],
    )
    t_res_start = time.perf_counter()
    resolutions = resolver.resolve(pb)
    t_res = time.perf_counter() - t_res_start

    assert len(resolutions) == 5
    assert t_res < 0.05  # Resolving 5 steps across 120 capabilities completes in < 50ms!
