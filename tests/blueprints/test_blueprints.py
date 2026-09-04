"""
Unit tests for Level A, B, and C Blueprints and SemanticMaterialBlueprint.
"""

from app.blueprints.content import (
    AudienceLevel,
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    KnowledgeDomain,
    LearningObjective,
    MisconceptionItem,
    WorkedExampleContent,
    WorkedExampleStep,
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


def test_content_blueprint_creation():
    meta = ContentMetadata(
        title="Understanding Torque",
        domain=KnowledgeDomain.PHYSICS,
        audience=AudienceLevel.HIGH_SCHOOL,
        purpose="teaching",
        duration_minutes=60,
    )
    obj = LearningObjective(objective="Understand rotational force", level="conceptual")
    concept = ConceptDefinition(
        name="Torque",
        formal_definition="Rotational analog of linear force.",
        symbol="τ",
        si_unit="N·m",
        formula="τ = r × F",
    )
    bp = ContentBlueprint(
        metadata=meta,
        objectives=[obj],
        concepts=[concept],
    )
    assert bp.metadata.title == "Understanding Torque"
    assert len(bp.concepts) == 1
    assert bp.concepts[0].symbol == "τ"


def test_pedagogical_blueprint_sequence():
    step1 = PedagogicalStep(
        semantic_type=SemanticStepType.HOOK,
        purpose="Engage students with door handle analogy",
    )
    step2 = PedagogicalStep(
        semantic_type=SemanticStepType.CONCEPT,
        purpose="Define torque formally",
    )
    pedagogy = PedagogicalBlueprint(
        primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
        narrative_rationale="Start with everyday intuition before mathematical formalism",
        sequence=[step1, step2],
    )
    assert len(pedagogy.sequence) == 2
    assert pedagogy.primary_pattern == PedagogicalPattern.CONCRETE_TO_ABSTRACT


def test_semantic_material_blueprint_integrity():
    meta = ContentMetadata(
        title="Understanding Torque",
        domain=KnowledgeDomain.PHYSICS,
        audience=AudienceLevel.HIGH_SCHOOL,
    )
    content = ContentBlueprint(metadata=meta)
    
    step1 = PedagogicalStep(
        id="step_hook",
        semantic_type=SemanticStepType.HOOK,
        purpose="Door handle question",
    )
    step2 = PedagogicalStep(
        id="step_diagram",
        semantic_type=SemanticStepType.VISUALIZATION,
        purpose="Render rotational force diagram",
        visual_intent="rotational_force_system",
    )
    pedagogy = PedagogicalBlueprint(
        primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
        narrative_rationale="Intuition before equations",
        sequence=[step1, step2],
    )
    
    prod_req = ProductionRequirement(
        step_id="step_diagram",
        semantic_type="visualization",
        semantic_intent=SemanticIntentSpec(
            semantic_intent="rotational_force_system",
            domain="physics",
        ),
    )
    production = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[prod_req],
    )

    material = SemanticMaterialBlueprint(
        content=content,
        pedagogy=pedagogy,
        production=production,
    )

    # Auto-generation of missing production requirement for step_hook
    assert len(material.production.requirements) == 2
    step_ids = {r.step_id for r in material.production.requirements}
    assert "step_hook" in step_ids
    assert "step_diagram" in step_ids
