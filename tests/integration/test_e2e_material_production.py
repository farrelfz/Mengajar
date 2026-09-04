"""
End-to-End Integration Test: AI Content-to-Artifact Material Production.

Simulates the complete production flow for the scenario:
"Create a teaching presentation about torque for Grade 11 students.
Start with intuition before mathematics, include misconceptions, a physics diagram,
derivation, worked examples, and practice questions."
"""

from pathlib import Path
import json

from app.blueprints.content import (
    AudienceLevel,
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    KnowledgeDomain,
    LearningObjective,
    MisconceptionItem,
    WorkedExampleContent,
)
from app.blueprints.pedagogical import (
    PedagogicalBlueprint,
    PedagogicalPattern,
    PedagogicalStep,
    SemanticStepType,
)
from app.blueprints.production import (
    ProductionBlueprint,
    ProductionRequirement,
    SemanticIntentSpec,
    TargetArtifactType,
)
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.capabilities.registry import CapabilityRegistry
from app.libraries import register_all_default_capabilities
from app.composition.bridge import CompositionBridge
from app.rendering.engine import MasterRenderEngine


def test_e2e_torque_presentation_production(tmp_path: Path):
    # 1. Setup Registry with all capabilities
    reg = CapabilityRegistry()
    register_all_default_capabilities(reg)

    # 2. Construct Level A (Content Blueprint)
    meta = ContentMetadata(
        title="Understanding Torque & Rotational Motion",
        domain=KnowledgeDomain.PHYSICS,
        audience=AudienceLevel.HIGH_SCHOOL,
        purpose="teaching",
        duration_minutes=60,
    )
    obj1 = LearningObjective(objective="Understand the physical meaning of torque", level="conceptual")
    concept1 = ConceptDefinition(
        name="Torque",
        formal_definition="The quantitative measure of the tendency of a force to cause a body to rotate about a specific point.",
        intuitive_explanation="Rotational push or pull. The farther from the pivot you push, the easier it is.",
        symbol="τ",
        si_unit="N·m",
        formula="τ = r · F · sin(θ)",
    )
    misconception1 = MisconceptionItem(
        common_belief="More force always means more rotation.",
        why_it_seems_true="Pushing harder feels like it should do more.",
        counterexample="Pushing on the door hinge with infinite force produces zero rotation.",
        correct_explanation="Torque requires both force and a non-zero perpendicular lever arm distance.",
    )
    content = ContentBlueprint(
        metadata=meta,
        objectives=[obj1],
        concepts=[concept1],
        misconceptions=[misconception1],
    )

    # 3. Construct Level B (Pedagogical Blueprint)
    step_hook = PedagogicalStep(
        id="step_1_hook",
        semantic_type=SemanticStepType.HOOK,
        purpose="Engage with everyday door handle observation",
    )
    step_concept = PedagogicalStep(
        id="step_2_concept",
        semantic_type=SemanticStepType.CONCEPT,
        purpose="Introduce definition of torque",
    )
    step_viz = PedagogicalStep(
        id="step_3_diagram",
        semantic_type=SemanticStepType.VISUALIZATION,
        purpose="Visualize torque vector system with pivot and lever arm",
        visual_intent="rotational_force_system",
    )
    step_misc = PedagogicalStep(
        id="step_4_misconception",
        semantic_type=SemanticStepType.MISCONCEPTION,
        purpose="Correct intuitive misconception about force vs position",
    )
    step_we = PedagogicalStep(
        id="step_5_worked_example",
        semantic_type=SemanticStepType.WORKED_EXAMPLE,
        purpose="Calculate door opening torque with given values",
    )
    pedagogy = PedagogicalBlueprint(
        primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
        narrative_rationale="Intuition -> Observation -> Formalism -> Visualization -> Scaffolded Practice",
        sequence=[step_hook, step_concept, step_viz, step_misc, step_we],
    )

    # 4. Construct Level C (Production Blueprint)
    req_hook = ProductionRequirement(
        step_id="step_1_hook",
        semantic_type="hook",
        required_capability_id="presentation.hero_statement",
    )
    req_concept = ProductionRequirement(
        step_id="step_2_concept",
        semantic_type="concept",
        required_capability_id="presentation.concept_introduction",
    )
    req_viz = ProductionRequirement(
        step_id="step_3_diagram",
        semantic_type="visualization",
        semantic_intent=SemanticIntentSpec(
            semantic_intent="rotational_force_system",
            domain="physics",
            parameters={"lever_length_m": 1.5, "force_newtons": 60.0, "force_angle_deg": 90.0},
        ),
    )
    req_misc = ProductionRequirement(
        step_id="step_4_misconception",
        semantic_type="misconception",
        required_capability_id="pedagogy.misconception_correction",
    )
    req_we = ProductionRequirement(
        step_id="step_5_worked_example",
        semantic_type="worked_example",
        required_capability_id="pedagogy.worked_example",
    )
    production = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[req_hook, req_concept, req_viz, req_misc, req_we],
    )

    # 5. Assemble unified SemanticMaterialBlueprint
    material = SemanticMaterialBlueprint(
        content=content,
        pedagogy=pedagogy,
        production=production,
    )

    # 6. Bridge to DocumentComposition
    bridge = CompositionBridge(registry=reg)
    output_dir = tmp_path / "torque_presentation_output"
    composition, assets = bridge.compose_material(material, output_dir=output_dir)

    assert len(composition.pages) == 5
    assert len(assets) >= 1
    # Verify the generated SVG exists
    assert Path(assets[0].path).exists()

    # 7. Render with MasterRenderEngine
    templates_dir = Path("app/rendering/html/templates")
    engine = MasterRenderEngine(templates_dir=templates_dir, output_dir=output_dir)
    result = engine.render(composition)

    assert result.success is True
    assert result.pdf_path is not None
    assert Path(result.pdf_path).exists()
    assert result.pages >= 5
