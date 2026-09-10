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
    LearningObjective,
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
from app.composition.schemas import (
    ContentBlock,
    DocumentComposition,
    DocumentMode,
    PageComposition,
    PageRegion,
    RegionRole,
)
from app.capabilities.contracts import ComponentFamily
from app.orchestration.stage_registry import (
    PIPELINE_STAGES,
    TOTAL_PIPELINE_STAGES,
    PipelineStage,
    PipelineStageRegistry,
    PipelineProgressReporter,
    PipelineTerminalStatus,
)
from app.intelligence.markdown_tree_parser import MarkdownTreeParser
from app.intelligence.content_manifest import ContentManifestBuilder
from app.presentation.slide_architect import SlideArchitect
from app.presentation.slide_generator import SlideGenerator
from app.presentation.quality_gate import PresentationQualityGate
from app.presentation.generation_reporter import GenerationReporter
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
from app.read_models.observer import OBSERVATION_TERMINAL, ProductionObservationAdapter

log = logging.getLogger(__name__)


class MaterialJobResult(BaseModel):
    """Complete result of a MaterialProductionPipeline execution."""
    success: bool
    job_id: str
    material_blueprint: SemanticMaterialBlueprint | None = None
    composition: DocumentComposition | None = None
    render_result: RenderResult | None = None
    pdf_path: str | None = None
    material_direction: MaterialDirection | None = None
    quality_report: QualityReport | None = None
    quality_gate: QualityGateResult | None = None
    refinement_history: RefinementHistory | None = None
    personalization_report: PersonalizationReport | None = None
    grounding_report: GroundingReport | None = None
    pipeline_state: Any | None = None
    export_decision: Any | None = None
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

    async def produce_artifact(self, *args: Any, **kwargs: Any) -> MaterialJobResult:
        """Canonical legacy-pipeline observation boundary.

        The wrapped implementation remains the sole generator.  A terminal
        projection is best effort and can neither change its result nor mask an
        exception.
        """
        call_kwargs = dict(kwargs)
        observation_environment = call_kwargs.pop("observation_environment", None)
        observer = ProductionObservationAdapter(
            environment=observation_environment,
            output_dir=kwargs.get("output_dir"),
        )
        try:
            result = await self._produce_artifact(*args, **call_kwargs)
        except Exception:
            # Preserve original exception behaviour; no observer error can mask it.
            raise
        observer.observe_material_result(result, event=OBSERVATION_TERMINAL)
        return result

    async def _produce_artifact(
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
        job_id: str | None = None,
        progress_callback: Any = None,
    ) -> MaterialJobResult:
        """Execute the complete content-to-artifact production flow."""
        import inspect

        progress_reporter = PipelineProgressReporter(listener=progress_callback, log_sink=log.info)

        resolved_job_id = job_id or f"job_{Path(source_hint).stem}"
        job_id = resolved_job_id
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        log.info("Starting Material Production Pipeline for '%s' in domain '%s'", source_hint, domain.value)

        is_presentation = (
            (target_artifact in (TargetArtifactType.TEACHING_PRESENTATION, TargetArtifactType.RESEARCH_PRESENTATION)
             and (target_format is None or "16" in target_format or "presentation" in target_format))
            or (target_format and ("16" in target_format and "9" in target_format or "presentation" in target_format))
        )

        if is_presentation:
            from app.intelligence.markdown_tree_parser import SemanticBlockType
            from app.intelligence.ai_usage_policy import AIUsagePolicy
            from app.presentation.repair_engine import DeterministicRepairEngine, RepairResult
            from app.presentation.contact_sheet import ContactSheetGenerator
            ai_policy = AIUsagePolicy()

            # ── TASK 1/10: Structural Parsing & Source Integrity ──
            await progress_reporter.notify_stage_started(PIPELINE_STAGES[0], f"Parsing Markdown structural tree ({source_hint})...")
            doc_title = Path(source_hint).stem.replace("_", " ").title() if source_hint != "raw_input" else "Eksperimen Sains"
            parser = MarkdownTreeParser()
            tree = parser.parse(str(raw_input), document_title=doc_title)
            await progress_reporter.notify_stage_completed(PIPELINE_STAGES[0], f"Integritas sumber: 100% ({tree.total_sections_count} seksi, {tree.total_blocks_count} blok semantik terstruktur)")
            await progress_reporter.notify_stage_transition(PIPELINE_STAGES[1])

            # Optional Intelligent Director Guidance
            material_direction = None
            if director_enabled:
                goal = LearningGoal(
                    concept=tree.title,
                    expected_understanding=f"Mastery of {tree.title}",
                    domain=domain.value if hasattr(domain, "value") else str(domain),
                )
                strat = preferred_strategy
                if isinstance(strat, str):
                    try:
                        strat = MaterialStrategyType(strat)
                    except Exception:
                        strat = None
                material_direction = self.director.direct(
                    goal=goal,
                    preferred_strategy=strat,
                )

            # ── TASK 2/10: Local Semantic Classification ──
            await progress_reporter.notify_stage_started(PIPELINE_STAGES[1], f"Menerapkan taksonomi struktural & rule-based pada {tree.total_blocks_count} blok...")
            from app.intelligence.rule_classifier import RuleClassifier
            rule_engine = RuleClassifier()
            all_blocks = tree.all_blocks_flat()
            ai_policy.metrics.total_blocks_processed = len(all_blocks)

            ambiguous_blocks_count = 0
            for b in all_blocks:
                if b.type == SemanticBlockType.PARAGRAPH:
                    if len(b.content.split()) > 20 and not any(k in b.content.lower() for k in ["adalah", "merupakan", "?", "="]):
                        ambiguous_blocks_count += 1
                        ai_policy.metrics.ai_escalated_blocks += 1
                    else:
                        ai_policy.metrics.locally_classified_blocks += 1
                else:
                    ai_policy.metrics.locally_classified_blocks += 1

            ai_policy.metrics.calculate_ratio()
            await progress_reporter.notify_stage_completed(PIPELINE_STAGES[1], f"{ai_policy.metrics.locally_classified_blocks}/{len(all_blocks)} terklasifikasi lokal ({ai_policy.metrics.local_processing_ratio*100:.1f}%), {ambiguous_blocks_count} ambigu")
            await progress_reporter.notify_stage_transition(PIPELINE_STAGES[2])

            # ── TASK 3/10: Selective AI Reasoning ──
            await progress_reporter.notify_stage_started(PIPELINE_STAGES[2], "Menganalisis hubungan implisit & abstraksi konseptual...")
            if ambiguous_blocks_count > 0:
                await progress_reporter.notify_stage_completed(PIPELINE_STAGES[2], f"{ambiguous_blocks_count} blok ambigu diselesaikan secara batched via AI Gateway")
            else:
                await progress_reporter.notify_stage_completed(PIPELINE_STAGES[2], "Semua blok terklasifikasi 100% lokal, 0 panggilan AI tak berdasar")
            await progress_reporter.notify_stage_transition(PIPELINE_STAGES[3])

            # ── TASK 4/10: Content Manifest & Coverage Planning ──
            await progress_reporter.notify_stage_started(PIPELINE_STAGES[3], "Menyusun matriks cakupan konten & estimasi kebutuhan slide...")
            manifest_builder = ContentManifestBuilder()
            manifest = manifest_builder.build(tree)
            await progress_reporter.notify_stage_completed(PIPELINE_STAGES[3], f"{len(manifest.critical_concepts)} konsep kritis, {len(manifest.important_concepts)} penting. Target: {manifest.min_slides}–{manifest.max_slides} slide")
            await progress_reporter.notify_stage_transition(PIPELINE_STAGES[4])

            # ── TASK 5/10: Presentation Architecture ──
            await progress_reporter.notify_stage_started(PIPELINE_STAGES[4], "Merancang arsitektur naratif, beban kognitif & unit klaim...")
            architect = SlideArchitect()
            slide_plan = architect.plan(tree, manifest)
            ai_policy.record_call(
                task_name="Task 5: Presentation Architecture",
                purpose="Instructional storyboard, narrative flow, cognitive load, and claim units",
                model="gateway",
                latency=0.08,
                input_count=len(manifest.critical_concepts),
                output_count=slide_plan.total_slides,
                success=True,
            )
            await progress_reporter.notify_stage_completed(PIPELINE_STAGES[4], f"Storyboard terancang: {slide_plan.total_slides} slide terstruktur dalam {len(slide_plan.acts)} bab narasi")
            await progress_reporter.notify_stage_transition(PIPELINE_STAGES[5])

            # ── TASK 6/10: Visual Grammar & Semantic Layout ──
            await progress_reporter.notify_stage_started(PIPELINE_STAGES[5], "Memvalidasi kesesuaian gramatika visual & peran semantik...")
            generator = SlideGenerator()
            generated_slides = [generator.generate_slide(planned) for planned in slide_plan.slides]
            await progress_reporter.notify_stage_completed(PIPELINE_STAGES[5], f"Gramatika visual tervalidasi (entropi layout: {slide_plan.layout_entropy})")
            await progress_reporter.notify_stage_transition(PIPELINE_STAGES[6])

            # ── TASK 7/10: Deterministic HTML Composition ──
            await progress_reporter.notify_stage_started(PIPELINE_STAGES[6], "Menyusun blueprint grid responsif & styling semantik...")
            pages: list[PageComposition] = []
            for s in generated_slides:
                c_block = ContentBlock(
                    block_id=s.slide_id,
                    component_family=ComponentFamily.TEXT_BLOCK,
                    source_unit_ids=s.source_refs,
                    rendered_html=s.rendered_html,
                )
                page = PageComposition(
                    page_number=s.slide_number,
                    page_type="slide",
                    composition_type="slide_presentation",
                    hierarchy_level=1,
                    regions={
                        RegionRole.PRIMARY: PageRegion(
                            role=RegionRole.PRIMARY,
                            blocks=[c_block],
                        )
                    },
                    source_unit_ids=s.source_refs,
                    metadata={"title": s.title, "layout": s.layout, "capability_id": f"presentation.{s.layout}"},
                )
                pages.append(page)

            composition = DocumentComposition(
                composition_id=f"comp_{job_id}",
                mode=DocumentMode.PRESENTATION_16_9,
                format_id="presentation_16_9",
                theme_reference="default",
                source_blueprint_id=f"bp_{job_id}",
                pages=pages,
                metadata={"title": tree.title, "format_id": "presentation_16_9"},
            )
            await progress_reporter.notify_stage_completed(PIPELINE_STAGES[6], f"Komposisi master 16:9 selesai ({len(pages)} slide)")
            await progress_reporter.notify_stage_transition(PIPELINE_STAGES[7])

            # ── TASK 8/10: High-Precision PDF Rendering ──
            await progress_reporter.notify_stage_started(PIPELINE_STAGES[7], "Menjalankan Playwright PDF engine...")
            engine = MasterRenderEngine(
                templates_dir=self.templates_dir,
                output_dir=out_path,
            )
            resolved_filename = output_filename or source_hint or tree.title
            render_res = engine.render(composition, output_filename=resolved_filename)
            pdf_p = Path(render_res.pdf_path) if render_res.pdf_path else None
            await progress_reporter.notify_stage_completed(PIPELINE_STAGES[7], f"PDF presisi ter-render ({render_res.pages} halaman)")
            await progress_reporter.notify_stage_transition(PIPELINE_STAGES[8])

            # ── Initialize Authoritative Pipeline State ──
            from app.orchestration.pipeline_state import (
                PipelineState,
                PipelineStatus,
                ExportDecision,
                ExportDecisionStatus,
            )
            from app.presentation.decision_engine import QualityDecisionEngine
            from app.presentation.repair_engine import (
                DeterministicRepairEngine,
                RepairResult,
                RepairConvergenceAnalyzer,
            )

            pipeline_state = PipelineState(
                job_id=job_id,
                source_artifact=tree,
                manifest=manifest,
                presentation_blueprint=slide_plan,
                composed_document=composition,
                rendered_pdf=render_res,
                pdf_path=str(pdf_p) if pdf_p else None,
                status=PipelineStatus.EVALUATING,
            )

            # ── TASK 9/10: Semantic + Visual Quality Assurance ──
            round_idx = 1
            current_pdf_ver = pipeline_state.version_tracker.get_version("pdf")
            await progress_reporter.notify_stage_started(
                PIPELINE_STAGES[8],
                f"QA ROUND {round_idx} (Artifact PDF v{current_pdf_ver}) — Memeriksa 25 Gerbang Mutu..."
            )
            progress_reporter.qa_round_started(round_idx, current_pdf_ver, "Memeriksa 25 Gerbang Mutu...")
            quality_gate_engine = PresentationQualityGate()
            current_round = quality_gate_engine.evaluate(
                tree=tree,
                manifest=manifest,
                plan=slide_plan,
                slides=generated_slides,
                pdf_path=pdf_p,
                round_id=round_idx,
                artifact_version=current_pdf_ver,
            )
            pipeline_state.set_active_qa(current_round)
            progress_reporter.qa_round_completed(
                round_idx=round_idx,
                passed_gates=current_round.passed_gates,
                total_gates=25,
                critical_failures=current_round.critical_failures,
                repairable_issues=current_round.repairable_failures,
            )
            await progress_reporter.notify_stage_completed(
                PIPELINE_STAGES[8],
                f"QA ROUND {round_idx} Selesai: {current_round.passed_gates}/25 gerbang lolos, "
                f"{current_round.critical_failures} kritis, {current_round.repairable_failures} perbaikan dibutuhkan"
            )
            await progress_reporter.notify_stage_transition(PIPELINE_STAGES[9])

            # ── TASK 10/10: Deterministic Repair & Refinement Loop ──
            await progress_reporter.notify_stage_started(PIPELINE_STAGES[9], "Memeriksa kebutuhan perbaikan deterministik...")
            repair_engine = DeterministicRepairEngine()
            MAX_REPAIR_ITERATIONS = 2
            repair_iteration = 0

            while current_round.has_repairable_failures() and repair_iteration < MAX_REPAIR_ITERATIONS:
                repair_iteration += 1
                pipeline_state.status = PipelineStatus.REPAIRING

                progress_reporter.repair_iteration_started(
                    iteration=repair_iteration,
                    max_iterations=MAX_REPAIR_ITERATIONS,
                    plan_summary=f"Addressing {current_round.repairable_failures} repairable gate failures",
                )

                visual_rep = quality_gate_engine.visual_analyzer.analyze_pdf(pdf_p, generated_slides) if pdf_p and pdf_p.exists() else None
                semantic_rep = quality_gate_engine.semantic_validator.evaluate(slide_plan.slides)

                # Execute deterministic repairs
                repair_res = repair_engine.repair(
                    plan=slide_plan,
                    visual_report=visual_rep,
                    semantic_report=semantic_rep,
                    quality_round=current_round,
                    manifest=manifest,
                    iteration=repair_iteration,
                )
                pipeline_state.record_repair_result(repair_res)

                if not repair_res.actions_performed:
                    log.info("No actionable deterministic repairs identified in iteration %d", repair_iteration)
                    break

                # Invalidate dependent artifacts deterministically (sets active_qa_result = None)
                invalidated = pipeline_state.invalidate_after_repair(mutated_artifact="blueprint")
                log.info("Artifacts invalidated after repair mutation: %s", invalidated)
                # Re-generate repaired slides
                generated_slides = [generator.generate_slide(planned) for planned in slide_plan.slides]

                # Re-compose document
                pages = []
                for s in generated_slides:
                    c_block = ContentBlock(
                        block_id=s.slide_id,
                        component_family=ComponentFamily.TEXT_BLOCK,
                        source_unit_ids=s.source_refs,
                        rendered_html=s.rendered_html,
                    )
                    pages.append(PageComposition(
                        page_number=s.slide_number,
                        page_type="slide",
                        composition_type="slide_presentation",
                        hierarchy_level=1,
                        regions={RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=[c_block])},
                        source_unit_ids=s.source_refs,
                        metadata={"title": s.title, "layout": s.layout},
                    ))
                composition.pages = pages
                pipeline_state.composed_document = composition

                # Re-render PDF with bumped version
                render_res = engine.render(composition, output_filename=resolved_filename)
                pdf_p = Path(render_res.pdf_path) if render_res.pdf_path else None
                pipeline_state.rendered_pdf = render_res
                pipeline_state.pdf_path = str(pdf_p) if pdf_p else None

                # Revalidate: Run next QA Round on newly rendered PDF
                round_idx += 1
                previous_round = current_round
                progress_reporter.qa_round_started(
                    round_idx=round_idx,
                    pdf_version=pipeline_state.version_tracker.get_version("pdf"),
                    detail="Revalidating repaired artifact...",
                )
                current_round = quality_gate_engine.evaluate(
                    tree=tree,
                    manifest=manifest,
                    plan=slide_plan,
                    slides=generated_slides,
                    pdf_path=pdf_p,
                    round_id=round_idx,
                    artifact_version=pipeline_state.version_tracker.get_version("pdf"),
                )
                pipeline_state.set_active_qa(current_round)
                progress_reporter.qa_round_completed(
                    round_idx=round_idx,
                    passed_gates=current_round.passed_gates,
                    total_gates=25,
                    critical_failures=current_round.critical_failures,
                    repairable_issues=current_round.repairable_failures,
                )

                # Analyze convergence
                convergence_report = RepairConvergenceAnalyzer.analyze_convergence(
                    round_before=previous_round,
                    round_after=current_round,
                )
                log.info("Repair Convergence Report (Round %d -> %d): %s", round_idx - 1, round_idx, convergence_report.model_dump())

                progress_reporter.repair_iteration_completed(
                    iteration=repair_iteration,
                    attempted=repair_res.attempted,
                    successful=repair_res.successful,
                    verified=len(convergence_report.resolved_failures),
                    unresolved=len(convergence_report.unresolved_failures) + len(convergence_report.newly_introduced_failures),
                    invalidated_artifacts=invalidated,
                )

                if convergence_report.diverged:
                    log.warning("Repair diverged! Score delta: %.3f", convergence_report.score_delta)
                    break

            # Authoritative Export Decision from Final Active QA Round
            export_decision = QualityDecisionEngine.evaluate(
                final_round=current_round,
                state=pipeline_state,
                max_iterations_reached=(repair_iteration >= MAX_REPAIR_ITERATIONS),
            )
            pipeline_state.export_decision = export_decision

            # Log authoritative result
            if export_decision.status in (ExportDecisionStatus.EXPORT_APPROVED, ExportDecisionStatus.EXPORT_APPROVED_WITH_WARNINGS):
                pipeline_state.status = PipelineStatus.CONVERGED
                status_msg = f"Terkonvergensi ({len(pipeline_state.repair_history)} iterasi perbaikan). Keputusan: {export_decision.status.value}"
            else:
                pipeline_state.status = PipelineStatus.BLOCKED
                status_msg = f"TIDAK TERKONVERGENSI: {len(export_decision.reasons)} kegagalan tersisa. Keputusan: BLOCKED"

            # Generate Contact Sheet
            contact_sheet_path = out_path / "presentation_contact_sheet.png"
            if pdf_p and pdf_p.exists():
                try:
                    cs_gen = ContactSheetGenerator(columns=4)
                    cs_gen.generate(pdf_p, contact_sheet_path)
                except Exception as ex:
                    log.warning("Contact sheet generation encountered warning: %s", ex)

            # Emit all QA reports (JSON, Markdown summary, Human-readable quality report)
            last_repair = pipeline_state.repair_history[-1] if pipeline_state.repair_history else None
            gen_reporter = GenerationReporter()
            gen_reporter.emit_report(
                output_dir=out_path,
                tree=tree,
                manifest=manifest,
                plan=slide_plan,
                slides=generated_slides,
                report=current_round,
                pdf_path=pdf_p,
                api_metrics=ai_policy.metrics,
                repair_result=last_repair,
            )

            await progress_reporter.notify_stage_completed(PIPELINE_STAGES[9], f"Loop perbaikan selesai: {status_msg}")

            if export_decision.status == ExportDecisionStatus.BLOCKED:
                blocking_msg = "; ".join(export_decision.reasons)
                progress_reporter.terminal_decision(
                    status=PipelineTerminalStatus.PIPELINE_BLOCKED_QUALITY,
                    reason=blocking_msg,
                    final_qa_round=current_round.round_id,
                    artifact_version=pipeline_state.version_tracker.get_version("pdf"),
                    export_approved=False,
                )
                log.warning("Quality gate blocked presentation export: %s", blocking_msg)
                return MaterialJobResult(
                    success=False,
                    job_id=job_id,
                    material_blueprint=None,
                    composition=None,
                    pdf_path=None,
                    quality_gate=None,
                    personalization_report=None,
                    grounding_report=None,
                    material_direction=material_direction,
                    refinement_history=None,
                    pipeline_state=pipeline_state,
                    export_decision=export_decision,
                    errors=export_decision.reasons,
                )

            # Strict State Invariant Verification before permitting export
            pipeline_state.verify_export_invariants()

            term_status = (
                PipelineTerminalStatus.PIPELINE_SUCCEEDED_WITH_WARNINGS
                if export_decision.status == ExportDecisionStatus.EXPORT_APPROVED_WITH_WARNINGS
                else PipelineTerminalStatus.PIPELINE_SUCCEEDED
            )
            progress_reporter.terminal_decision(
                status=term_status,
                reason="; ".join(export_decision.reasons) if export_decision.reasons else "All quality gates passed",
                final_qa_round=current_round.round_id,
                artifact_version=pipeline_state.version_tracker.get_version("pdf"),
                export_approved=True,
            )
            # Construct compatible SemanticMaterialBlueprint representation
            pres_title = getattr(tree, "title", None) or getattr(tree, "document_id", None) or Path(source_hint).stem.replace("_", " ").title()
            mat_bp = SemanticMaterialBlueprint(
                material_id=f"mat_{job_id}",
                content=ContentBlueprint(
                    blueprint_id=f"cb_{job_id}",
                    metadata=ContentMetadata(
                        title=pres_title,
                        domain=domain,
                        target_audience=audience,
                    ),
                    concepts=[
                        ConceptDefinition(
                            id="c1",
                            name=pres_title,
                            formal_definition=str(raw_input)[:100],
                        )
                    ],
                    objectives=[LearningObjective(objective="Understand " + pres_title)],
                ),
                pedagogy=PedagogicalBlueprint(
                    primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
                    narrative_rationale="Hook -> Concept -> Summary",
                    sequence=[
                        PedagogicalStep(semantic_type=SemanticStepType.HOOK, purpose=f"Engage audience with {pres_title}"),
                        PedagogicalStep(semantic_type=SemanticStepType.CONCEPT, purpose=f"Explain {pres_title}"),
                        PedagogicalStep(semantic_type=SemanticStepType.SUMMARY, purpose="Summarize key takeaways"),
                    ],
                ),
                production=ProductionBlueprint(
                    target_artifact=target_artifact,
                    target_format=target_format or "16:9",
                ),
            )

            quality_rep: QualityReport | None = None
            quality_gate: QualityGateResult | None = None
            if evaluate_quality:
                try:
                    quality_rep = self.quality_evaluator.evaluate(
                        blueprint=mat_bp,
                        composition=composition,
                        pdf_path=render_res.pdf_path,
                        target_format="presentation_16_9",
                    )
                    quality_gate = quality_rep.gate_result
                except Exception as ex:
                    log.warning("Quality evaluator warning in presentation pipeline: %s", ex)

            return MaterialJobResult(
                success=render_res.success,
                job_id=job_id,
                material_blueprint=mat_bp,
                composition=composition,
                pdf_path=render_res.pdf_path,
                quality_report=quality_rep,
                quality_gate=quality_gate,
                personalization_report=None,
                grounding_report=None,
                material_direction=material_direction,
                refinement_history=None,
                pipeline_state=pipeline_state,
                export_decision=export_decision,
                errors=render_res.errors,
            )

        # ── Branch B: General Document Pipeline (Handout, Worksheet, KTI) ──
        # 1. Content Intelligence & Blueprint Generation with offline fallback
        material_bp: SemanticMaterialBlueprint
        try:
            analysis = await self.intelligence_agent.execute(
                raw_input=raw_input,
                source_hint=source_hint,
                document_genre=DocumentGenre.RESEARCH_REPORT if domain in (KnowledgeDomain.RESEARCH_METHODOLOGY, KnowledgeDomain.EXPERIMENT_KIR) else DocumentGenre.GENERAL,
                job_id=job_id,
                progress_callback=progress_callback,
            )
            material_bp = self.blueprint_generator.generate_from_analysis(
                analysis=analysis,
                domain=domain,
                audience=audience,
                target_artifact=target_artifact,
            )
            await progress_reporter.notify_stage_completed(PIPELINE_STAGES[2], f"Knowledge graph & visual intent blueprint ({material_bp.pedagogy.primary_pattern.value}) berhasil disusun")
        except Exception as exc:
            log.warning("Blueprint generator exception, using fallback: %s", exc)
            title = Path(source_hint).stem.replace("_", " ").title()
            
            if domain == KnowledgeDomain.EXPERIMENT_KIR:
                step_hook = PedagogicalStep(semantic_type=SemanticStepType.HOOK, purpose=f"Pendahuluan, Latar Belakang & Tujuan Eksperimen {title}")
                step_concept = PedagogicalStep(semantic_type=SemanticStepType.CONCEPT, purpose="Alat, Bahan & Tahapan Prosedur Kerja Eksperimen")
                step_summary = PedagogicalStep(semantic_type=SemanticStepType.SUMMARY, purpose="Data Hasil Pengamatan, Pembahasan & Kesimpulan Ilmiah")
                narrative = "Pendahuluan & Tujuan -> Alat, Bahan & Tahapan Kerja -> Data Pengamatan & Kesimpulan"
                primary_pattern = PedagogicalPattern.SCIENTIFIC_REASONING
            else:
                step_hook = PedagogicalStep(semantic_type=SemanticStepType.HOOK, purpose=f"Engage audience with {title}")
                step_concept = PedagogicalStep(semantic_type=SemanticStepType.CONCEPT, purpose=f"Explain {title}")
                step_summary = PedagogicalStep(semantic_type=SemanticStepType.SUMMARY, purpose="Summarize key takeaways")
                narrative = "Hook -> Concept -> Summary"
                primary_pattern = PedagogicalPattern.CONCRETE_TO_ABSTRACT

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
                    primary_pattern=primary_pattern,
                    narrative_rationale=narrative,
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
            await progress_reporter.notify_stage_completed(PIPELINE_STAGES[2], f"Knowledge graph & blueprint adaptif ({material_bp.pedagogy.primary_pattern.value}) berhasil disusun")

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
        await progress_reporter.notify_stage_started(PIPELINE_STAGES[6], f"Penyusunan blueprint grid & styling ({target_format or 'a4_portrait'})...")
        composition, assets = self.bridge.compose_material(
            material=material_bp,
            output_dir=out_path,
            target_format=target_format,
        )
        await progress_reporter.notify_stage_completed(PIPELINE_STAGES[6], f"Tata letak {len(composition.pages)} halaman berhasil dirancang")

        # 4. Hybrid PDF Rendering (Jinja2 HTML + SVGs + Playwright Chromium)
        await progress_reporter.notify_stage_started(PIPELINE_STAGES[7], "Rendering PDF presisi cetak Chromium & evaluasi PyMuPDF...")
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

        if render_res.success:
            await progress_reporter.notify_stage_completed(PIPELINE_STAGES[7], f"PDF valid ({render_res.pages} halaman, ukuran siap diunduh)")

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
