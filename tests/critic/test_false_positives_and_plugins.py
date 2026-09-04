"""
Unit tests for False-Positive Protection and External Critic Plugin Extensibility.
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
from app.blueprints.pedagogical import PedagogicalBlueprint, PedagogicalPattern, PedagogicalStep, SemanticStepType
from app.blueprints.production import ProductionBlueprint, ProductionRequirement, TargetArtifactType
from app.composition.schemas import (
    ContentBlock,
    DocumentComposition,
    PageComposition,
    PageRegion,
    RegionRole,
)
from app.critic.base import BaseCritic
from app.critic.context import CritiqueContext, CritiqueContextBuilder
from app.critic.contracts import (
    CritiqueConfidence,
    CritiqueFinding,
    CritiquePerspective,
    CritiqueSeverity,
)
from app.critic.engine import GenerativeCriticEngine
from app.critic.registry import CriticRegistry
from app.design.schemas import ComponentFamily
from app.director.contracts import LearningJourney, LearningStage, LearningStageType, MaterialStrategyType
from app.intelligence.schemas import DocumentMode


class DomainSpecificQuantumCritic(BaseCritic):
    """External domain plugin critic."""

    @property
    def critic_id(self) -> str:
        return "quantum_domain_critic"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.SCIENTIFIC_RIGOR

    def can_critique(self, context: CritiqueContext) -> bool:
        return True

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        return [
            CritiqueFinding(
                id="plugin_quantum_superposition_check",
                perspective=self.perspective,
                title="Quantum Superposition State Scrutiny",
                observation="Plugin evaluated quantum state.",
                diagnosis="Superposition checked by domain plugin.",
                why_it_matters="Quantum rigor.",
                severity=CritiqueSeverity.LOW,
                confidence=CritiqueConfidence.HIGH,
                improvement_direction="Maintain quantum state consistency.",
            )
        ]


def test_plugin_critic_dynamic_registration_and_execution():
    reg = CriticRegistry()
    reg.register(DomainSpecificQuantumCritic())

    engine = GenerativeCriticEngine(registry=reg)
    report = engine.critique(artifact_id="job_plugin_test")

    assert len(report.findings) == 1
    assert report.findings[0].id == "plugin_quantum_superposition_check"
    assert "quantum_domain_critic" in report.trace.critics_executed


def test_false_positive_protection_on_intentional_clean_minimalism():
    # Clean 1-concept high school physics lesson with correct sequence
    content = ContentBlueprint(
        blueprint_id="bp_clean",
        metadata=ContentMetadata(title="Torque Basics", domain=KnowledgeDomain.PHYSICS, audience=AudienceLevel.HIGH_SCHOOL),
        objectives=[LearningObjective(id="o1", objective="Understand torque definition", target_concept="Torque")],
        concepts=[ConceptDefinition(id="c1", name="Torque", formal_definition="Rotational analog of linear force.")],
        facts=[],
    )
    pedagogy = PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="Rationale", sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")])
    prod = ProductionBlueprint(target_artifact=TargetArtifactType.TEACHING_PRESENTATION, requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")])
    bp = SemanticMaterialBlueprint(material_id="m_clean", content=content, pedagogy=pedagogy, production=prod)

    journey = LearningJourney(
        journey_id="j_clean",
        strategy=MaterialStrategyType.CONCEPTUAL_DISCOVERY,
        stages=[
            LearningStage(stage_type=LearningStageType.HOOK, title="Opening Door", purpose="Intuition"),
            LearningStage(stage_type=LearningStageType.CONCEPT_FORMALIZATION, title="Torque Equation", purpose="Formula"),
            LearningStage(stage_type=LearningStageType.WORKED_EXAMPLE, title="Example Problem", purpose="Apply"),
        ],
    )

    page = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content="Torque equals force times lever arm.")],
            )
        },
    )
    comp = DocumentComposition(
        document_id="doc_clean",
        title="Torque",
        mode=DocumentMode.PRESENTATION_16_9,
        theme_reference="default",
        source_blueprint_id="bp_clean",
        pages=[page],
    )

    engine = GenerativeCriticEngine()
    report = engine.critique(
        artifact_id="job_clean_test",
        blueprint=bp,
        journey=journey,
        composition=comp,
        target_format="presentation_16_9",
        audience_level="high_school",
    )

    # Clean minimal artifact should produce 0 critical or high severity findings
    crit_high = [f for f in report.findings if f.severity in [CritiqueSeverity.CRITICAL, CritiqueSeverity.HIGH]]
    assert len(crit_high) == 0
