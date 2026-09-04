"""
Tests for Pipeline Director Integration and Cross-Domain Policy Extensibility.
"""

import pytest

from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.capabilities.taxonomy import CapabilityFamily, VisualGrammar
from app.director import (
    BaseDomainPolicy,
    DomainPolicyRegistry,
    IntelligentMaterialDirector,
    LearningGoal,
    MaterialStrategyType,
)
from app.orchestration.production_pipeline import MaterialProductionPipeline
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


@pytest.mark.asyncio
async def test_pipeline_with_director_enabled():
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)

    res = await pipeline.produce_artifact(
        raw_input="# Torque\nUnderstanding lever arms.",
        source_hint="torque_input.md",
        domain=KnowledgeDomain.PHYSICS,
        audience=AudienceLevel.HIGH_SCHOOL,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        target_format="presentation_16_9",
        director_enabled=True,
        preferred_strategy=MaterialStrategyType.CONCRETE_TO_ABSTRACT,
    )

    assert res.success is True
    assert res.material_direction is not None
    assert res.material_direction.strategy == MaterialStrategyType.CONCRETE_TO_ABSTRACT
    assert len(res.material_direction.journey.stages) > 0


def test_cross_domain_policy_extensibility_without_core_modification():
    # Define and register a custom Chemistry policy dynamically
    class ChemistryDomainPolicy(BaseDomainPolicy):
        domain_name = "chemistry"
        preferred_strategies = [
            MaterialStrategyType.SCIENTIFIC_REASONING,
            MaterialStrategyType.CONCRETE_TO_ABSTRACT,
        ]

    custom_reg = DomainPolicyRegistry()
    custom_reg.register(ChemistryDomainPolicy())

    director = IntelligentMaterialDirector(policy_registry=custom_reg)
    goal = LearningGoal(concept="Catalytic Hydrogenation", expected_understanding="Alkene reduction", domain="chemistry")
    direction = director.direct(goal=goal)

    assert direction.strategy in [
        MaterialStrategyType.SCIENTIFIC_REASONING,
        MaterialStrategyType.CONCRETE_TO_ABSTRACT,
    ]
    assert direction.trace.policy_applied == "chemistry"
