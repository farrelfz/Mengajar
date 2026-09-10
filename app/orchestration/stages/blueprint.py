"""
Blueprint Generation Stage: Calls ContentIntelligenceAgent and MaterialBlueprintGenerator with safe offline fallback.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.agents.content_intelligence_agent import ContentIntelligenceAgent
from app.blueprints.content import (
    AudienceLevel,
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    FactStatement,
    KnowledgeDomain,
)
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.blueprints.pedagogical import (
    PedagogicalBlueprint,
    PedagogicalPattern,
    PedagogicalStep,
    SemanticStepType,
)
from app.blueprints.production import (
    ProductionBlueprint,
    ProductionRequirement,
    TargetArtifactType,
)
from app.intelligence.material_blueprint_generator import MaterialBlueprintGenerator
from app.intelligence.schemas import DocumentGenre
from app.orchestration.contracts import (
    ProductionJobContext,
    StageExecutionResult,
    StageState,
    WorkflowStageType,
)
from app.orchestration.stages.base import ProductionStage


class BlueprintGenerationStage(ProductionStage):
    def __init__(
        self,
        agent: ContentIntelligenceAgent | None = None,
        generator: MaterialBlueprintGenerator | None = None,
    ) -> None:
        if agent is None:
            from app.agents.content_intelligence_agent import ContentIntelligenceAgent
            agent = ContentIntelligenceAgent()
        self.agent = agent
        self.generator = generator or MaterialBlueprintGenerator()

    @property
    def stage_id(self) -> str:
        return "blueprint_generation"

    @property
    def stage_type(self) -> WorkflowStageType:
        return WorkflowStageType.BLUEPRINT_GENERATION

    def run(self, context: ProductionJobContext) -> StageExecutionResult:
        if "material_blueprint" in context.shared_data:
            bp = context.shared_data["material_blueprint"]
            return StageExecutionResult(
                stage_id=self.stage_id,
                state=StageState.SUCCEEDED,
                output={"title": bp.content.metadata.title, "steps_count": len(bp.pedagogy.sequence)},
                artifacts=["material_blueprint"],
            )

        meta = context.request.metadata
        dom_str = meta.domain.lower()
        if dom_str == "research_methodology":
            domain_enum = KnowledgeDomain.RESEARCH_METHODOLOGY
        elif dom_str == "physics":
            domain_enum = KnowledgeDomain.PHYSICS
        elif dom_str == "education":
            domain_enum = KnowledgeDomain.EDUCATION
        else:
            domain_enum = KnowledgeDomain.GENERAL_SCIENCE

        aud_enum = AudienceLevel.HIGH_SCHOOL
        bp: SemanticMaterialBlueprint | None = None

        # Attempt intelligence agent execution
        try:
            loop = asyncio.new_event_loop()
            try:
                analysis = loop.run_until_complete(
                    self.agent.execute(
                        raw_input=context.request.raw_input,
                        source_hint=context.request.source_hint,
                        document_genre=DocumentGenre.RESEARCH_REPORT if domain_enum == KnowledgeDomain.RESEARCH_METHODOLOGY else DocumentGenre.GENERAL,
                        job_id=context.job_id,
                    )
                )
                bp = self.generator.generate_from_analysis(
                    analysis=analysis,
                    domain=domain_enum,
                    audience=aud_enum,
                    target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
                )
            finally:
                loop.close()
        except Exception:
            title = context.request.source_hint.replace("_", " ").title()
            step_hook = PedagogicalStep(semantic_type=SemanticStepType.HOOK, purpose=f"Engage audience with {title}")
            step_concept = PedagogicalStep(semantic_type=SemanticStepType.CONCEPT, purpose=f"Explain {title}")
            step_summary = PedagogicalStep(semantic_type=SemanticStepType.SUMMARY, purpose="Summarize key takeaways")

            bp = SemanticMaterialBlueprint(
                material_id=f"mat_{context.job_id}",
                content=ContentBlueprint(
                    blueprint_id=f"cb_{context.job_id}",
                    metadata=ContentMetadata(
                        title=title,
                        domain=domain_enum,
                        audience=aud_enum,
                    ),
                    concepts=[
                        ConceptDefinition(
                            id="c1",
                            name=title,
                            formal_definition=context.request.raw_input.strip()[:100],
                            formula="tau = r * F sin(theta)" if domain_enum == KnowledgeDomain.PHYSICS else "",
                        )
                    ],
                    facts=[
                        FactStatement(
                            id="f1",
                            statement=context.request.raw_input.strip()[:120],
                        )
                    ],
                ),
                pedagogy=PedagogicalBlueprint(
                    primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
                    narrative_rationale="Hook -> Concept -> Summary",
                    sequence=[step_hook, step_concept, step_summary],
                ),
                production=ProductionBlueprint(
                    target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
                    target_format=meta.target_format,
                    requirements=[
                        ProductionRequirement(step_id=step_hook.id, semantic_type="hook", required_capability_id="presentation.hero_statement"),
                        ProductionRequirement(step_id=step_concept.id, semantic_type="concept", required_capability_id="presentation.concept_introduction"),
                        ProductionRequirement(step_id=step_summary.id, semantic_type="summary", required_capability_id="presentation.takeaway_summary"),
                    ],
                ),
            )

        bp.production.target_format = meta.target_format
        context.shared_data["material_blueprint"] = bp

        return StageExecutionResult(
            stage_id=self.stage_id,
            state=StageState.SUCCEEDED,
            output={"title": bp.content.metadata.title, "steps_count": len(bp.pedagogy.sequence)},
            artifacts=["material_blueprint"],
        )
