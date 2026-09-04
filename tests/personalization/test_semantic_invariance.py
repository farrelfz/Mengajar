"""
Unit tests for Semantic Invariance across different learner profiles.
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
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.blueprints.pedagogical import PedagogicalBlueprint, PedagogicalPattern
from app.blueprints.production import ProductionBlueprint, TargetArtifactType
from app.personalization.contracts import AdaptationPolicyType
from app.personalization.engine import PersonalizationEngine
from app.personalization.profiles import CanonicalProfiles


def test_personalization_does_not_mutate_underlying_blueprint_concepts():
    content = ContentBlueprint(
        blueprint_id="bp_inv",
        metadata=ContentMetadata(title="Torque Mechanics", domain=KnowledgeDomain.PHYSICS),
        objectives=[LearningObjective(id="o1", objective="Understand torque definition", target_concept="Torque")],
        concepts=[ConceptDefinition(id="c1", name="Torque", formal_definition="Rotational force analog tau = r * F sin(theta).")],
    )
    bp = SemanticMaterialBlueprint(material_id="m1", content=content, pedagogy=PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="R"), production=ProductionBlueprint(target_artifact=TargetArtifactType.DETAILED_HANDOUT))

    engine = PersonalizationEngine()
    novice_prof = CanonicalProfiles.novice_high_support()
    adv_prof = CanonicalProfiles.advanced_challenge()

    rep_novice = engine.personalize(blueprint=bp, learner_profile=novice_prof)
    rep_adv = engine.personalize(blueprint=bp, learner_profile=adv_prof)

    # Invariant: Underlying blueprint concepts must remain 100% identical
    assert bp.content.concepts[0].formal_definition == "Rotational force analog tau = r * F sin(theta)."
    assert bp.content.objectives[0].objective == "Understand torque definition"
    assert rep_novice.adaptation_plan.sequence_strategy != rep_adv.adaptation_plan.sequence_strategy
