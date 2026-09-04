"""
Adversarial Case B & C: Incomplete objective coverage and undefined/trivial concepts.
"""

import pytest

from app.blueprints.content import (
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    KnowledgeDomain,
    LearningObjective,
)
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.blueprints.pedagogical import PedagogicalBlueprint, PedagogicalPattern, PedagogicalStep, SemanticStepType
from app.blueprints.production import ProductionBlueprint, ProductionRequirement, TargetArtifactType
from app.quality.contracts import QualityDimension, QualitySeverity
from app.quality.semantic_evaluator import SemanticEvaluator


def test_uncovered_learning_objectives_penalizes_score():
    # 3 objectives declared, but only 1 has a corresponding concept
    content = ContentBlueprint(
        blueprint_id="bp_uncovered",
        metadata=ContentMetadata(title="Torque & Equilibrium", domain=KnowledgeDomain.PHYSICS),
        objectives=[
            LearningObjective(id="o1", objective="Understand torque", target_concept="Torque"),
            LearningObjective(id="o2", objective="Calculate moment of inertia", target_concept="Moment of Inertia"),
            LearningObjective(id="o3", objective="Analyze rotational equilibrium", target_concept="Rotational Equilibrium"),
        ],
        concepts=[
            # Only Torque is defined
            ConceptDefinition(id="c1", name="Torque", formal_definition="Rotational analog of linear force."),
        ],
        facts=[],
    )
    pedagogy = PedagogicalBlueprint(
        primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
        narrative_rationale="Rationale",
        sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")],
    )
    prod = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")],
    )
    material = SemanticMaterialBlueprint(material_id="m1", content=content, pedagogy=pedagogy, production=prod)

    metrics, findings = SemanticEvaluator.evaluate(material)

    assert len(findings) >= 1
    assert any("target concepts with no formal definitions" in f.finding.lower() for f in findings)
    assert metrics[0].score < 0.8


def test_trivial_or_empty_concept_definition_detected():
    content = ContentBlueprint(
        blueprint_id="bp_trivial_concept",
        metadata=ContentMetadata(title="Momentum", domain=KnowledgeDomain.PHYSICS),
        objectives=[LearningObjective(id="o1", objective="Understand momentum", target_concept="Momentum")],
        concepts=[
            # Definition is trivially short / empty
            ConceptDefinition(id="c1", name="Momentum", formal_definition="N/A"),
        ],
        facts=[],
    )
    pedagogy = PedagogicalBlueprint(
        primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
        narrative_rationale="Rationale",
        sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")],
    )
    prod = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")],
    )
    material = SemanticMaterialBlueprint(material_id="m2", content=content, pedagogy=pedagogy, production=prod)

    metrics, findings = SemanticEvaluator.evaluate(material)

    assert len(findings) >= 1
    assert any(f.severity == QualitySeverity.ERROR for f in findings)
    assert any("incompletely articulated concepts" in f.finding.lower() for f in findings)
    assert metrics[0].score <= 0.75
