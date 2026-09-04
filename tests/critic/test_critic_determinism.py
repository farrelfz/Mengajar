"""
Unit tests for Generative Critic determinism across 10 consecutive executions.
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
from app.critic.engine import GenerativeCriticEngine
from app.design.schemas import ComponentFamily
from app.director.contracts import LearningJourney, LearningStage, LearningStageType, MaterialStrategyType
from app.intelligence.schemas import DocumentMode


def test_critic_determinism_across_10_runs():
    content = ContentBlueprint(
        blueprint_id="bp_det",
        metadata=ContentMetadata(title="Rotational Dynamics", domain=KnowledgeDomain.PHYSICS),
        objectives=[
            LearningObjective(id="o1", objective="Understand torque", target_concept="Torque"),
            LearningObjective(id="o2", objective="Calculate precession", target_concept="Precession"),  # Undefined
        ],
        concepts=[ConceptDefinition(id="c1", name="Torque", formal_definition="Rotational force analog.")],
        facts=[],
    )
    pedagogy = PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="Rationale", sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")])
    prod = ProductionBlueprint(target_artifact=TargetArtifactType.TEACHING_PRESENTATION, requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")])
    bp = SemanticMaterialBlueprint(material_id="m_det", content=content, pedagogy=pedagogy, production=prod)

    journey = LearningJourney(
        journey_id="j_det",
        strategy=MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
        stages=[
            LearningStage(stage_type=LearningStageType.WORKED_EXAMPLE, title="Problem 1", purpose="Solve"),
            LearningStage(stage_type=LearningStageType.CONCEPT_FORMALIZATION, title="Theory", purpose="Define"),
        ],
    )

    page = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content="Torque intro.")],
            )
        },
    )
    comp = DocumentComposition(
        document_id="doc_det",
        title="Torque",
        mode=DocumentMode.PRESENTATION_16_9,
        theme_reference="default",
        source_blueprint_id="bp_det",
        pages=[page],
    )

    engine = GenerativeCriticEngine()
    reports = [
        engine.critique(
            artifact_id="job_det_test",
            blueprint=bp,
            journey=journey,
            composition=comp,
            target_format="presentation_16_9",
        )
        for _ in range(10)
    ]

    first = reports[0]
    for idx, rep in enumerate(reports[1:], start=2):
        assert rep.overall_assessment == first.overall_assessment, f"Assessment mismatch on run {idx}"
        assert len(rep.findings) == len(first.findings), f"Findings count mismatch on run {idx}"
        assert [f.id for f in rep.findings] == [f.id for f in first.findings], f"Finding IDs mismatch on run {idx}"
        assert rep.priority_queue == first.priority_queue, f"Priority queue mismatch on run {idx}"
        assert len(rep.recommendations) == len(first.recommendations), f"Recommendations count mismatch on run {idx}"
        assert [r.id for r in rep.recommendations] == [r.id for r in first.recommendations], f"Recommendation IDs mismatch on run {idx}"
        assert len(rep.agreements) == len(first.agreements), f"Agreements mismatch on run {idx}"
        assert len(rep.conflicts) == len(first.conflicts), f"Conflicts mismatch on run {idx}"
