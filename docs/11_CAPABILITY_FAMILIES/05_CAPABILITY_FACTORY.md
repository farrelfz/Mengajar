# 05 — Capability Family Factory

## Instantaneous Semantic Capability Generation

The `CapabilityFamilyFactory` allows developers and domain pack authors to create and register complete, production-ready capabilities without implementing renderer subclasses.

### Function Signature

```python
def create_family_capability(
    capability_id: str,
    template_id: str,
    metadata: CapabilityMetadata,
    parameter_extractor: Callable[[PedagogicalStep, ContentBlueprint, dict[str, Any]], dict[str, Any] | BaseFamilySpec] | None = None,
    spec_model: type[CapabilitySpec] | None = None,
) -> Capability:
    ...
```

---

## Example: Creating a Biology Food Chain Capability

```python
from app.capabilities.contracts import CapabilityMetadata
from app.capabilities.families.factory import register_family_capability
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

# 1. Define metadata
bio_meta = CapabilityMetadata(
    capability_id="biology.ecology.trophic_cascade",
    category="biology",
    display_name="Trophic Cascade & Food Chain",
    description="Sequential energy transfer across trophic levels",
    semantic_tags=["trophic_level", "food_chain", "energy_transfer", "ecology"],
    supported_artifacts=["presentation", "document", "poster"],
    domain="biology",
    taxonomy=TaxonomySignature(
        family=CapabilityFamily.PROCESS_VISUALIZATION,
        primary_intent=SemanticIntent.SEQUENCE,
        structure=InformationStructure.LINEAR_SEQUENCE,
        pedagogical_role=PedagogicalRole.EXPLANATION,
        visual_grammar=VisualGrammar.PROCESS_FLOW,
        density=DensityProfile.FOCUSED,
    ),
)

# 2. Register via Factory (ZERO renderer classes written!)
register_family_capability(
    registry=CapabilityRegistry.get_instance(),
    capability_id="biology.ecology.trophic_cascade",
    template_id="process.linear",
    metadata=bio_meta,
)
```
