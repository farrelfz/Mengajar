"""
Unit tests for PedagogicalCritic and CognitiveLoadCritic.
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
from app.composition.schemas import (
    ContentBlock,
    DocumentComposition,
    PageComposition,
    PageRegion,
    RegionRole,
)
from app.critic.cognitive_load import CognitiveLoadCritic
from app.critic.context import CritiqueContextBuilder
from app.critic.contracts import CritiquePerspective, CritiqueSeverity
from app.critic.pedagogical import PedagogicalCritic
from app.design.schemas import ComponentFamily
from app.director.contracts import LearningJourney, LearningStage, LearningStageType, MaterialStrategyType
from app.intelligence.schemas import DocumentMode


def test_pedagogical_critic_flags_inverted_scaffolding():
    journey = LearningJourney(
        journey_id="j_inverted",
        strategy=MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
        stages=[
            LearningStage(stage_type=LearningStageType.WORKED_EXAMPLE, title="Problem 1", purpose="Solve"),
            LearningStage(stage_type=LearningStageType.CONCEPT_FORMALIZATION, title="Theory", purpose="Define"),
        ],
    )
    ctx = CritiqueContextBuilder("job_ped").with_journey(journey).build()
    critic = PedagogicalCritic()
    findings = critic.critique(ctx)

    assert len(findings) == 1
    assert findings[0].id == "ped_worked_example_precedes_concept"
    assert findings[0].severity == CritiqueSeverity.HIGH
    assert findings[0].perspective == CritiquePerspective.PEDAGOGICAL
    assert "rote memorization" in findings[0].why_it_matters


def test_cognitive_load_critic_flags_concurrent_concept_overload():
    # 7 concepts introduced at once
    concepts = [ConceptDefinition(id=f"c_{i}", name=f"Concept {i}", formal_definition="Formal definition") for i in range(7)]
    content = ContentBlueprint(
        blueprint_id="bp_overload",
        metadata=ContentMetadata(title="Complex", domain=KnowledgeDomain.PHYSICS),
        objectives=[],
        concepts=concepts,
        facts=[],
    )
    pedagogy = PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="Rationale", sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")])
    prod = ProductionBlueprint(target_artifact=TargetArtifactType.TEACHING_PRESENTATION, requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")])
    bp = SemanticMaterialBlueprint(material_id="m_overload", content=content, pedagogy=pedagogy, production=prod)

    ctx = CritiqueContextBuilder("job_cog").with_blueprint(bp).build()
    critic = CognitiveLoadCritic()
    findings = critic.critique(ctx)

    assert len(findings) >= 1
    f_overload = next(f for f in findings if f.id == "cog_excessive_concurrent_concepts")
    assert f_overload.severity == CritiqueSeverity.HIGH
    assert "working memory" in f_overload.diagnosis.lower()
