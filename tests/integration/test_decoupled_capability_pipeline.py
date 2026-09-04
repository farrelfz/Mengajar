"""
Integration test proving plugin extensibility without modifying core infrastructure.
"""
from pathlib import Path
from pydantic import Field
from app.capabilities.contracts import (
    Capability,
    CapabilityMetadata,
    CapabilityOutput,
    CapabilityRenderer,
    CapabilitySpec,
)
from app.capabilities.registry import CapabilityRegistry
from app.composition.bridge import CompositionBridge
from app.blueprints.content import (
    ContentBlueprint,
    ContentMetadata,
    AudienceLevel,
    KnowledgeDomain,
)
from app.blueprints.pedagogical import (
    PedagogicalBlueprint,
    PedagogicalStep,
    SemanticStepType,
)
from app.blueprints.production import ProductionBlueprint, ProductionRequirement, TargetArtifactType
from app.blueprints.contracts import SemanticMaterialBlueprint


class CustomPluginSpec(CapabilitySpec):
    sample_size: int = 50
    independent_factor: str = "Light Intensity"
    metric: str = "Photosynthesis Rate"


class CustomPluginRenderer(CapabilityRenderer[CustomPluginSpec]):
    def validate_spec(self, spec: CustomPluginSpec) -> bool:
        return spec.sample_size > 0

    def measure(self, spec: CustomPluginSpec, context=None):
        return {"height_px": 250}

    def render(self, spec: CustomPluginSpec, context=None) -> CapabilityOutput:
        html = f"""
        <div class="plugin-custom-matrix">
            <h3>Experimental Matrix: {spec.independent_factor} vs {spec.metric}</h3>
            <p>Sample Size: N={spec.sample_size}</p>
        </div>
        """
        return CapabilityOutput(
            capability_id="test.experimental.variable_matrix",
            output_format="html",
            rendered_content=html,
        )


def _custom_plugin_extractor(step, material):
    return {
        "sample_size": 120,
        "independent_factor": f"Custom Factor for {material.content.metadata.title}",
        "metric": "Yield Performance",
    }


def test_extensible_plugin_without_core_modification(tmp_path: Path):
    """
    Prove that a new capability can be created, registered, resolved,
    extracted, and rendered through CompositionBridge without modifying ANY core file.
    """
    custom_registry = CapabilityRegistry()

    # 1. Define and register new capability
    test_capability = Capability(
        metadata=CapabilityMetadata(
            capability_id="test.experimental.variable_matrix",
            category="experimental",
            display_name="Test Variable Matrix",
            description="Test-only experimental variable matrix.",
            semantic_tags=["custom_experiment", "test_variable", "foundation"],
            supported_artifacts=["presentation", "document"],
            domain="general",
            preferred_renderer="html",
        ),
        spec_model=CustomPluginSpec,
        renderer=CustomPluginRenderer(),
        parameter_extractor=_custom_plugin_extractor,
    )
    custom_registry.register(test_capability)

    # 2. Setup semantic material
    material = SemanticMaterialBlueprint(
        material_id="mat_plugin_test",
        content=ContentBlueprint(
            metadata=ContentMetadata(
                title="Agricultural Lighting Experiment",
                domain=KnowledgeDomain.GENERAL_SCIENCE,
                audience=AudienceLevel.UNDERGRADUATE,
            ),
        ),
        pedagogy=PedagogicalBlueprint(
            narrative_rationale="Experimental testing sequence",
            sequence=[
                PedagogicalStep(
                    id="step_plugin_1",
                    purpose="Demonstrate plugin variable matrix",
                    semantic_type=SemanticStepType.CONCEPT,
                ),
            ],
        ),
        production=ProductionBlueprint(
            target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
            requirements=[
                ProductionRequirement(
                    step_id="step_plugin_1",
                    semantic_type="concept",
                    required_capability_id="test.experimental.variable_matrix",
                )
            ],
        ),
    )

    # 3. Execute bridge
    bridge = CompositionBridge(registry=custom_registry)
    composition, assets = bridge.compose_material(material, assets_dir=tmp_path / "assets")

    # 4. Assertions
    assert len(composition.pages) == 1
    page = composition.pages[0]
    block = page.regions[list(page.regions.keys())[0]].blocks[0]
    assert block.rendered_html is not None
    assert "Experimental Matrix: Custom Factor for Agricultural Lighting Experiment" in block.rendered_html
    assert "Sample Size: N=120" in block.rendered_html
