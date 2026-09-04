from app.libraries import register_all_default_capabilities
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
from app.blueprints.production import ProductionBlueprint, TargetArtifactType
from app.blueprints.contracts import SemanticMaterialBlueprint


def _make_dummy_material(title: str = "Rotational Dynamics") -> SemanticMaterialBlueprint:
    return SemanticMaterialBlueprint(
        material_id="mat_dummy_1",
        content=ContentBlueprint(
            metadata=ContentMetadata(
                title=title,
                domain=KnowledgeDomain.PHYSICS,
                audience=AudienceLevel.HIGH_SCHOOL,
            ),
        ),
        pedagogy=PedagogicalBlueprint(
            narrative_rationale="Step by step concept introduction",
            sequence=[
                PedagogicalStep(
                    id="step_1",
                    purpose="Introduce core concept",
                    semantic_type=SemanticStepType.CONCEPT,
                ),
            ],
        ),
        production=ProductionBlueprint(
            target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        ),
    )


def test_decentralized_parameter_extraction_pedagogy():
    """Verify pedagogy capabilities extract valid parameters without bridge involvement."""
    reg = register_all_default_capabilities()
    worked_example_cap = reg.get("pedagogy.worked_example")
    assert worked_example_cap is not None

    material = _make_dummy_material("Kinematics Problem")
    step = material.pedagogy.sequence[0]

    params = worked_example_cap.extract_parameters(step, material)
    assert isinstance(params, dict)
    assert "problem" in params
    assert "Kinematics Problem" in params["problem"]

    spec = worked_example_cap.spec_model(**params)
    assert worked_example_cap.renderer.validate_spec(spec) is True


def test_decentralized_parameter_extraction_physics():
    """Verify physics capabilities extract valid parameters."""
    reg = register_all_default_capabilities()
    torque_cap = reg.get("physics.mechanics.torque_diagram")
    assert torque_cap is not None

    material = _make_dummy_material("Torque Equilibrium")
    step = material.pedagogy.sequence[0]

    params = torque_cap.extract_parameters(step, material)
    assert isinstance(params, dict)
    assert params.get("force_newtons") == 50.0

    spec = torque_cap.spec_model(**params)
    assert torque_cap.renderer.validate_spec(spec) is True


def test_decentralized_parameter_extraction_research_problem():
    """Verify research capabilities extract valid parameters."""
    reg = register_all_default_capabilities()
    funnel_cap = reg.get("research.problem.funnel")
    assert funnel_cap is not None

    material = _make_dummy_material("Microplastic Pollution")
    step = material.pedagogy.sequence[0]

    params = funnel_cap.extract_parameters(step, material)
    assert "topic" in params
    assert params["topic"] == "Microplastic Pollution"
    assert "final_research_question" in params


def test_capability_without_extractor_returns_empty_dict():
    """Verify capabilities with no parameter_extractor return an empty dict cleanly."""
    from app.capabilities.contracts import Capability, CapabilityMetadata, CapabilitySpec, CapabilityRenderer, CapabilityOutput

    class MockSpec(CapabilitySpec):
        pass

    class MockRenderer(CapabilityRenderer[MockSpec]):
        def validate_spec(self, spec: MockSpec) -> bool:
            return True
        def measure(self, spec: MockSpec, context=None):
            return {}
        def render(self, spec: MockSpec, context=None):
            return CapabilityOutput(capability_id="mock", output_format="html", rendered_content="<p>mock</p>")

    mock_cap = Capability(
        metadata=CapabilityMetadata(
            capability_id="mock.cap",
            category="mock",
            display_name="Mock",
            description="Mock cap",
        ),
        spec_model=MockSpec,
        renderer=MockRenderer(),
    )

    material = _make_dummy_material()
    params = mock_cap.extract_parameters(material.pedagogy.sequence[0], material)
    assert params == {}
