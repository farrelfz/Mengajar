"""
Unit tests for ScientificRigorCritic and AudienceCritic.
"""

import pytest

from app.blueprints.content import (
    AudienceLevel,
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    FactStatement,
    KnowledgeDomain,
)
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.blueprints.pedagogical import PedagogicalBlueprint, PedagogicalPattern, PedagogicalStep, SemanticStepType
from app.blueprints.production import ProductionBlueprint, ProductionRequirement, TargetArtifactType
from app.critic.audience import AudienceCritic
from app.critic.context import CritiqueContextBuilder
from app.critic.contracts import CritiquePerspective, CritiqueSeverity
from app.critic.scientific import ScientificRigorCritic


def test_scientific_critic_detects_correlation_causation_fallacy():
    content = ContentBlueprint(
        blueprint_id="bp_sci",
        metadata=ContentMetadata(title="Stats & Physics", domain=KnowledgeDomain.RESEARCH_METHODOLOGY),
        objectives=[],
        concepts=[],
        facts=[
            FactStatement(id="f1", statement="Variable X is strongly correlated with Y, which proves that X causes Y.")
        ],
    )
    pedagogy = PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="Rationale", sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")])
    prod = ProductionBlueprint(target_artifact=TargetArtifactType.DETAILED_HANDOUT, requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")])
    bp = SemanticMaterialBlueprint(material_id="m_sci", content=content, pedagogy=pedagogy, production=prod)

    ctx = CritiqueContextBuilder("job_sci").with_blueprint(bp).build()
    critic = ScientificRigorCritic()
    findings = critic.critique(ctx)

    assert len(findings) == 1
    assert "Correlation Inappropriately Stated as Direct Causation" in findings[0].title
    assert findings[0].severity == CritiqueSeverity.HIGH
    assert findings[0].perspective == CritiquePerspective.SCIENTIFIC_RIGOR


def test_audience_critic_flags_advanced_tertiary_concepts_in_high_school_material():
    content = ContentBlueprint(
        blueprint_id="bp_aud",
        metadata=ContentMetadata(title="Mechanics", domain=KnowledgeDomain.PHYSICS, audience=AudienceLevel.HIGH_SCHOOL),
        objectives=[],
        concepts=[
            ConceptDefinition(id="c1", name="Lagrangian Mechanics", formal_definition="Formulation based on kinetic minus potential energy tensor."),
        ],
        facts=[],
    )
    pedagogy = PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="Rationale", sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")])
    prod = ProductionBlueprint(target_artifact=TargetArtifactType.TEACHING_PRESENTATION, requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")])
    bp = SemanticMaterialBlueprint(material_id="m_aud", content=content, pedagogy=pedagogy, production=prod)

    ctx = CritiqueContextBuilder("job_aud").with_blueprint(bp).build()
    critic = AudienceCritic()
    findings = critic.critique(ctx)

    assert len(findings) == 1
    assert findings[0].id == "aud_advanced_prerequisite_gap"
    assert findings[0].perspective == CritiquePerspective.AUDIENCE
    assert findings[0].severity == CritiqueSeverity.HIGH
