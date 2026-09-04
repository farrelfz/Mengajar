"""
Unit tests for StructuralCritic and SemanticCritic.
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
from app.composition.schemas import DocumentComposition
from app.critic.context import CritiqueContextBuilder
from app.critic.contracts import CritiquePerspective, CritiqueSeverity
from app.critic.semantic import SemanticCritic
from app.critic.structural import StructuralCritic
from app.intelligence.schemas import DocumentMode


def test_structural_critic_flags_empty_composition():
    empty_comp = DocumentComposition(
        document_id="doc_empty",
        title="Empty",
        mode=DocumentMode.A4_PORTRAIT,
        theme_reference="default",
        source_blueprint_id="bp",
        pages=[],
    )
    ctx = CritiqueContextBuilder("job_empty").with_composition(empty_comp).build()
    critic = StructuralCritic()
    findings = critic.critique(ctx)

    assert len(findings) == 1
    assert findings[0].id == "struct_empty_doc"
    assert findings[0].severity == CritiqueSeverity.CRITICAL
    assert findings[0].perspective == CritiquePerspective.STRUCTURAL


def test_semantic_critic_flags_uncovered_objectives_and_shallow_definitions():
    content = ContentBlueprint(
        blueprint_id="bp_sem",
        metadata=ContentMetadata(title="Semantics", domain=KnowledgeDomain.PHYSICS),
        objectives=[
            LearningObjective(id="o1", objective="Master Torque", target_concept="Torque"),
            LearningObjective(id="o2", objective="Master Precession", target_concept="Precession"),  # Undefined
        ],
        concepts=[
            # Shallow definition
            ConceptDefinition(id="c1", name="Torque", formal_definition="Short"),
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
    bp = SemanticMaterialBlueprint(material_id="m_sem", content=content, pedagogy=pedagogy, production=prod)

    ctx = CritiqueContextBuilder("job_sem").with_blueprint(bp).build()
    critic = SemanticCritic()
    findings = critic.critique(ctx)

    assert len(findings) == 2
    f_uncovered = next(f for f in findings if f.id == "sem_uncovered_objectives")
    f_shallow = next(f for f in findings if f.id == "sem_trivial_concept_definitions")

    assert "Precession" in f_uncovered.observation
    assert "Torque" in f_shallow.observation
