"""
Tests for Learner Profiles, Complexity Policy, Vocabulary, and Formula Adaptation.
"""

import pytest

from app.blueprints.content import (
    AudienceLevel,
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    KnowledgeDomain,
    LearningObjective,
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
from app.adaptation import (
    AdaptiveContentTransformer,
    ComplexityLevel,
    ComplexityPolicy,
    VocabularyTransformer,
    get_default_learner_profile,
)


def create_sample_blueprint() -> SemanticMaterialBlueprint:
    meta = ContentMetadata(
        title="Classical Mechanics: Understanding Torque",
        domain=KnowledgeDomain.PHYSICS,
        audience=AudienceLevel.HIGH_SCHOOL,
        purpose="teaching",
        duration_minutes=60,
    )
    content = ContentBlueprint(
        metadata=meta,
        objectives=[LearningObjective(objective="Understand torque", level="conceptual")],
        concepts=[ConceptDefinition(name="Torque", formal_definition="Rotational force", intuitive_explanation="Pushing a door", symbol="tau")],
    )
    step1 = PedagogicalStep(
        id="step_1",
        semantic_type=SemanticStepType.CONCEPT,
        purpose="Torque Definition",
        visual_intent="process_flow",
    )
    pedagogy = PedagogicalBlueprint(
        pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
        narrative_rationale="Intuition to formalization",
        sequence=[step1],
    )
    production = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        target_format="presentation_16_9",
        requirements=[
            ProductionRequirement(
                step_id="step_1",
                semantic_type="concept",
                required_capability_id="physics.mechanics.torque_diagram",
            )
        ],
    )
    return SemanticMaterialBlueprint(
        content=content,
        pedagogy=pedagogy,
        production=production,
    )


def test_learner_profile_and_complexity_derivation():
    smp_learner = get_default_learner_profile(AudienceLevel.MIDDLE_SCHOOL)
    assert smp_learner.mathematical_readiness == ComplexityLevel.FOUNDATIONAL

    smp_complexity = ComplexityPolicy.derive_complexity_profile(smp_learner)
    assert smp_complexity.mathematical_formalism == ComplexityLevel.FOUNDATIONAL
    assert smp_complexity.vocabulary_complexity == ComplexityLevel.FOUNDATIONAL

    univ_learner = get_default_learner_profile(AudienceLevel.UNDERGRADUATE)
    assert univ_learner.mathematical_readiness == ComplexityLevel.ADVANCED

    univ_complexity = ComplexityPolicy.derive_complexity_profile(univ_learner)
    assert univ_complexity.mathematical_formalism == ComplexityLevel.ADVANCED


def test_vocabulary_and_formula_transformation_across_levels():
    # SMP (Foundational)
    smp_title = VocabularyTransformer.transform_term("torque", ComplexityLevel.FOUNDATIONAL)
    smp_formula = VocabularyTransformer.transform_formula("torque_formula", ComplexityLevel.FOUNDATIONAL)
    assert "Gaya Putar" in smp_title
    assert "F * d" in smp_formula

    # University (Advanced)
    univ_title = VocabularyTransformer.transform_term("torque", ComplexityLevel.ADVANCED)
    univ_formula = VocabularyTransformer.transform_formula("torque_formula", ComplexityLevel.ADVANCED)
    assert "Torque Vector" in univ_title or "Momen Gaya" in univ_title
    assert "times" in univ_formula or "alpha" in univ_formula or "vec" in univ_formula


def test_adaptive_content_transformer_produces_distinct_blueprints():
    transformer = AdaptiveContentTransformer()
    bp = create_sample_blueprint()

    # Middle School transformation
    smp_learner = get_default_learner_profile(AudienceLevel.MIDDLE_SCHOOL)
    smp_complexity = ComplexityPolicy.derive_complexity_profile(smp_learner)
    smp_bp, smp_trace = transformer.transform(bp, smp_learner, smp_complexity)

    # University transformation
    univ_learner = get_default_learner_profile(AudienceLevel.UNDERGRADUATE)
    univ_complexity = ComplexityPolicy.derive_complexity_profile(univ_learner)
    univ_bp, univ_trace = transformer.transform(bp, univ_learner, univ_complexity)

    # Assert semantic blueprints differ substantially
    assert smp_bp.content.metadata.title != univ_bp.content.metadata.title
    assert smp_bp.content.concepts[0].formal_definition != univ_bp.content.concepts[0].formal_definition
    assert "foundational" in smp_bp.pedagogy.sequence[0].purpose
    assert "advanced" in univ_bp.pedagogy.sequence[0].purpose
