"""
KIR AI Document Intelligence — Material Production Pipeline.

Unified master production pipeline that transforms raw ideas or material requests
into professionally rendered PDF artifacts through the complete intelligence chain:
Input -> Content Intelligence -> Personalization -> Material Blueprint -> Grounding -> Capability Resolution -> Composition -> Rendering -> Quality Evaluation -> Validated PDF -> Optional Closed-Loop Refinement.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

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
from app.capabilities.registry import CapabilityRegistry
from app.composition.bridge import CompositionBridge
from app.composition.schemas import DocumentComposition
from app.director import (
    AudienceProfile,
    InstructionalIntent,
    IntelligentMaterialDirector,
    KnowledgeState,
    LearningGoal,
    MaterialDirection,
    MaterialStrategyType,
)
from app.grounding import GroundingReport, KnowledgeGroundingEngine
from app.intelligence.material_blueprint_generator import MaterialBlueprintGenerator
from app.intelligence.schemas import DocumentGenre
from app.libraries import register_all_default_capabilities
from app.personalization import (
    AdaptationPolicyType,
    LearnerProfile,
    PersonalizationEngine,
    PersonalizationReport,
)
from app.quality import (
    QualityEvaluationEngine,
    QualityGateResult,
    QualityReport,
)
from app.refinement.contracts import RefinedArtifactBundle
from app.refinement.controller import IterativeRefinementController
from app.refinement.history import RefinementHistory
from app.rendering.engine import MasterRenderEngine
from app.rendering.schemas import RenderResult

log = logging.getLogger(__name__)


class MaterialJobResult(BaseModel):
    """Complete result of a MaterialProductionPipeline execution."""
    success: bool
    job_id: str
    material_blueprint: SemanticMaterialBlueprint
    composition: DocumentComposition
    render_result: RenderResult
    pdf_path: str | None = None
    material_direction: MaterialDirection | None = None
    quality_report: QualityReport | None = None
    quality_gate: QualityGateResult | None = None
    refinement_history: RefinementHistory | None = None
    personalization_report: PersonalizationReport | None = None
    grounding_report: GroundingReport | None = None
    errors: list[str] = Field(default_factory=list)


class MaterialProductionPipeline:
    """End-to-End pipeline producing real PDF artifacts from raw ideas or requests."""

    def __init__(
        self,
        registry: CapabilityRegistry | None = None,
        intelligence_agent: ContentIntelligenceAgent | None = None,
        blueprint_generator: MaterialBlueprintGenerator | None = None,
        director: IntelligentMaterialDirector | None = None,
        quality_evaluator: QualityEvaluationEngine | None = None,
        templates_dir: Path | str = "app/rendering/html/templates",
    ) -> None:
        self.registry = registry or CapabilityRegistry.get_instance()
        register_all_default_capabilities(self.registry)
        
        self.intelligence_agent = intelligence_agent or ContentIntelligenceAgent()
        self.blueprint_generator = blueprint_generator or MaterialBlueprintGenerator()
        self.director = director or IntelligentMaterialDirector()
        self.quality_evaluator = quality_evaluator or QualityEvaluationEngine()
        self.refinement_controller = IterativeRefinementController()
        self.personalization_engine = PersonalizationEngine()
        self.grounding_engine = KnowledgeGroundingEngine()
        self.bridge = CompositionBridge(registry=self.registry)
        self.templates_dir = Path(templates_dir)

    async def produce_artifact(
        self,
        raw_input: str | bytes,
        source_hint: str = "material_request.txt",
        domain: KnowledgeDomain = KnowledgeDomain.RESEARCH_METHODOLOGY,
        audience: AudienceLevel = AudienceLevel.HIGH_SCHOOL,
        target_artifact: TargetArtifactType = TargetArtifactType.TEACHING_PRESENTATION,
        output_dir: Path | str = "outputs/benchmark/material_production",
        output_filename: str | None = None,
        target_format: str | None = None,
        director_enabled: bool = False,
        preferred_strategy: MaterialStrategyType | str | None = None,
        evaluate_quality: bool = True,
        enable_refinement: bool = False,
        max_refinement_iterations: int = 3,
        learner_profile: LearnerProfile | None = None,
        adaptation_policy: AdaptationPolicyType = AdaptationPolicyType.BALANCED,
        enable_grounding: bool = False,
    ) -> MaterialJobResult:
        """Execute the complete content-to-artifact production flow."""
        job_id = f"job_{Path(source_hint).stem}"
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        log.info("Starting Material Production Pipeline for '%s' in domain '%s'", source_hint, domain.value)

        # 1. Content Intelligence & Blueprint Generation with offline fallback
        material_bp: SemanticMaterialBlueprint
        try:
            analysis = await self.intelligence_agent.execute(
                raw_input=raw_input,
                source_hint=source_hint,
                document_genre=DocumentGenre.RESEARCH_REPORT if domain == KnowledgeDomain.RESEARCH_METHODOLOGY else DocumentGenre.GENERAL,
                job_id=job_id,
            )
            material_bp = self.blueprint_generator.generate_from_analysis(
                analysis=analysis,
                domain=domain,
                audience=audience,
                target_artifact=target_artifact,
            )
        except Exception:
            title = Path(source_hint).stem.replace("_", " ").title()
            step_hook = PedagogicalStep(semantic_type=SemanticStepType.HOOK, purpose=f"Engage audience with {title}")
            step_concept = PedagogicalStep(semantic_type=SemanticStepType.CONCEPT, purpose=f"Explain {title}")
            step_summary = PedagogicalStep(semantic_type=SemanticStepType.SUMMARY, purpose="Summarize key takeaways")

            material_bp = SemanticMaterialBlueprint(
                material_id=f"mat_{job_id}",
                content=ContentBlueprint(
                    blueprint_id=f"cb_{job_id}",
                    metadata=ContentMetadata(
                        title=title,
                        domain=domain,
                        target_audience=audience,
                    ),
                    concepts=[
                        ConceptDefinition(
                            id="c1",
                            name=title,
                            formal_definition=str(raw_input)[:100],
                            formula="tau = r * F sin(theta)" if domain == KnowledgeDomain.PHYSICS else "",
                        )
                    ],
                    facts=[
                        FactStatement(
                            id="f1",
                            statement=str(raw_input)[:120],
                        )
                    ],
                ),
                pedagogy=PedagogicalBlueprint(
                    primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
                    narrative_rationale="Hook -> Concept -> Summary",
                    sequence=[step_hook, step_concept, step_summary],
                ),
                production=ProductionBlueprint(
                    target_artifact=target_artifact,
                    target_format=target_format or "a4_portrait",
                    requirements=[
                        ProductionRequirement(step_id=step_hook.id, semantic_type="hook", required_capability_id="presentation.hero_statement"),
                        ProductionRequirement(step_id=step_concept.id, semantic_type="concept", required_capability_id="presentation.concept_introduction"),
                        ProductionRequirement(step_id=step_summary.id, semantic_type="summary", required_capability_id="presentation.takeaway_summary"),
                    ],
                ),
            )

        if target_format:
            material_bp.production.target_format = target_format

        # 2.2 Optional Learning Personalization
        personalization_rep: PersonalizationReport | None = None
        if learner_profile is not None:
            personalization_rep = self.personalization_engine.personalize(
                blueprint=material_bp,
                learner_profile=learner_profile,
                policy=adaptation_policy,
                target_format=target_format or "a4_portrait",
            )
            if not preferred_strategy and personalization_rep.adaptation_plan.sequence_strategy:
                preferred_strategy = personalization_rep.adaptation_plan.sequence_strategy

        # 2.3 Optional Knowledge Grounding
        grounding_rep: GroundingReport | None = None
        if enable_grounding:
            grounded_context = self.grounding_engine.ground_material(
                material=material_bp,
                domain=domain.value,
            )
            grounding_rep = grounded_context.report

        # 2.5 Optional Intelligent Material Direction & Choreography
        material_dir: MaterialDirection | None = None
        if director_enabled:
            strat_enum = None
            if preferred_strategy:
                strat_enum = (
                    preferred_strategy
                    if isinstance(preferred_strategy, MaterialStrategyType)
                    else MaterialStrategyType(preferred_strategy)
                )

            goal_title = material_bp.content.metadata.title or Path(source_hint).stem.replace("_", " ").title()
            goal = LearningGoal(
                concept=goal_title,
                expected_understanding=f"Core understanding of {goal_title}",
                domain=domain.value,
            )
            
            pk_map = {
                "none": KnowledgeState.NOVICE,
                "fragmented": KnowledgeState.NOVICE,
                "basic": KnowledgeState.DEVELOPING,
                "solid": KnowledgeState.INTERMEDIATE,
                "strong": KnowledgeState.ADVANCED,
            }
            resolved_pk = (
                pk_map.get(learner_profile.prior_knowledge.value, KnowledgeState.NOVICE)
                if learner_profile
                else KnowledgeState.NOVICE
            )

            aud_profile = AudienceProfile(
                education_level=audience.value,
                prior_knowledge=resolved_pk,
            )
            material_dir = self.director.direct(
                goal=goal,
                audience=aud_profile,
                intent=InstructionalIntent.TEACH,
                format_id=target_format or "a4_portrait",
                preferred_strategy=strat_enum,
            )

        # 3. Deterministic Capability Resolution & Page Composition
        composition, assets = self.bridge.compose_material(
            material=material_bp,
            output_dir=out_path,
            target_format=target_format,
        )

        # 4. Hybrid PDF Rendering (Jinja2 HTML + SVGs + Playwright Chromium)
        engine = MasterRenderEngine(
            templates_dir=self.templates_dir,
            output_dir=out_path,
        )
        resolved_filename = output_filename or source_hint or material_bp.content.metadata.title
        render_res = engine.render(composition, output_filename=resolved_filename)

        # 5. Quality Evaluation & Formal Quality Gate
        quality_rep: QualityReport | None = None
        quality_gate: QualityGateResult | None = None
        if evaluate_quality and render_res.success:
            quality_rep = self.quality_evaluator.evaluate_artifact(
                job_id=job_id,
                material_bp=material_bp,
                composition=composition,
                journey=material_dir.journey if material_dir else None,
                pdf_path=render_res.pdf_path,
                target_format=target_format or "a4_portrait",
            )
            quality_gate = quality_rep.gate_result

        # 6. Optional Closed-Loop Iterative Refinement
        ref_history: RefinementHistory | None = None
        if enable_refinement:
            refined_bundle, ref_history = self.refinement_controller.refine(
                blueprint=material_bp,
                composition=composition,
                journey=material_dir.journey if material_dir else None,
                target_format=target_format or "a4_portrait",
                max_iterations=max_refinement_iterations,
                artifact_id=job_id,
            )
            material_bp = refined_bundle.blueprint
            composition = refined_bundle.composition

        return MaterialJobResult(
            success=render_res.success,
            job_id=job_id,
            material_blueprint=material_bp,
            composition=composition,
            render_result=render_res,
            pdf_path=render_res.pdf_path,
            material_direction=material_dir,
            quality_report=quality_rep,
            quality_gate=quality_gate,
            refinement_history=ref_history,
            personalization_report=personalization_rep,
            grounding_report=grounding_rep,
            errors=render_res.errors,
        )
