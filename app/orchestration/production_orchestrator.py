"""
Universal Document Intelligence System V5 — Canonical Production Orchestrator.

Phase 3D: Closed-Loop Multi-Artifact Generation, Quality Governance & Safe Convergence.
Coordinates source parsing, knowledge compilation, semantic transformation, composition,
controlled rendering, physical quality evaluation, and root-cause-aware closed-loop repair.

CRITICAL INVARIANT:
THE PRODUCTION ORCHESTRATOR MUST NEVER BECOME A SECOND QUALITY AUTHORITY.
UnifiedQualityAuthority remains the sole Level-0 export decision authority.
"""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from app.intelligence.pipeline import KnowledgeCompiler, OfflineMockResolutionProvider
from app.intelligence.transformation.intent import ArtifactType, get_default_intent
from app.intelligence.transformation.selection import KnowledgeSelectionEngine
from app.orchestration.convergence_controller import (
    ConvergenceCheckResult,
    ProductionConvergenceController,
    ProductionConvergenceOutcome,
)
from app.orchestration.decision_router import (
    DecisionRouteAction,
    QualityDecisionRouter,
    QualityRoutingInstruction,
)
from app.orchestration.escalation_router import (
    LayerEscalationPlan,
    RepairEscalationLayer,
    RepairEscalationRouter,
)
from app.orchestration.execution_profiles import (
    ArtifactExecutionProfile,
    ArtifactExecutionProfileRegistry,
)
from app.orchestration.export_gate import AuthorizedExportGate, ExportPackage, UnauthorizedExportError
from app.orchestration.failures import ProductionFailureRecord, ProductionFailureType
from app.orchestration.production_context import ArtifactProductionContext
from app.orchestration.failure_reporter import ConvergenceFailureReporter
from app.orchestration.production_state import ProductionState, ProductionStateMachine
from app.orchestration.versioning import ProductionVersionManager
from app.quality.artifact_fidelity import UnifiedFidelityValidator
from app.quality.authority.master_authority import UnifiedQualityAuthority
from app.quality.contracts.authority import UnifiedQualityReport
from app.quality.contracts.decisions import ExportDecision, UnifiedQualityDecision
from app.quality.rendered.quality_engine import MasterRenderedQualityEngine
from app.quality.repair.contracts import ConvergenceState, RepairTarget
from app.quality.repair.mutation_budget import MutationBudgetTracker, get_budget_for_artifact
from app.quality.repair.mutation_contract import RepairMutationScope
from app.quality.repair.outcome_registry import RepairOutcomeRegistry
from app.quality.repair.planner import CandidateRepairOption, MinimalInterventionRepairPlanner
from app.quality.repair.portfolio import RepairCandidatePortfolio
from app.quality.repair.registry import DEFAULT_STRATEGY_REGISTRY, RepairStrategyRegistry
from app.quality.repair.root_cause import DeterministicRootCauseAnalyzer, RootCauseHypothesis
from app.quality.repair.transaction import RepairTransactionManager, RepairTransactionRecord
from app.quality.repair.vector_convergence import (
    BudgetReservationPolicy,
    ConvergenceProgressVector,
    FailurePatternType,
    QualityVector,
    RepairFailurePatternDetector,
)
from app.orchestration.forensics_exporter import RepairForensicsExporter
from app.quality.repair.effectiveness.causal_reach import CausalReachModel
from app.quality.repair.effectiveness.contracts import (
    EffectivenessStatus,
    RepairAttempt,
    RepairEffectivenessResult,
    RepairExecutionStatus,
)
from app.quality.repair.effectiveness.escalation import CausalEscalationEngine, RepairEscalationDecision, RepairEscalationReason
from app.quality.repair.effectiveness.firewall import (
    RepairStrategyCompatibilityFirewall,
    StrategyRejectionRecord,
)
from app.quality.repair.effectiveness.strategy_memory import (
    SelfDisqualifyingStrategyMemory,
    StrategyHistoryKey,
)
from app.quality.repair.effectiveness.zero_effect_detector import (
    DomainFingerprint,
    DomainFingerprinter,
    ZeroEffectMutationDetector,
)
from app.read_models.observer import (
    OBSERVATION_JOB_CREATED,
    OBSERVATION_PIPELINE_STARTED,
    OBSERVATION_QUALITY_AVAILABLE,
    OBSERVATION_TERMINAL,
    ProductionObservationAdapter,
)

logger = logging.getLogger("orchestration.production")


@dataclass(frozen=True)
class ProductionRequest:
    """Canonical request payload to produce any document artifact."""
    raw_input: str
    artifact_type: str  # PRESENTATION, HANDOUT, WORKSHEET, SCIENTIFIC_DOCUMENT
    output_dir: Path | str
    job_id: Optional[str] = None
    output_filename: Optional[str] = None
    source_filename: str = "source.md"
    max_repair_iterations: Optional[int] = None
    resolution_provider: Optional[Any] = None
    progress_callback: Optional[Callable[[str, float], None]] = None
    # Observational routing only; it has no effect on production authority.
    observation_environment: Optional[str] = None


@dataclass(frozen=True)
class ProductionOutcome:
    """Authoritative outcome of an end-to-end production orchestrator run."""
    success: bool
    job_id: str
    artifact_type: str
    final_state: ProductionState
    decision: ExportDecision
    overall_quality_score: float
    total_iterations: int
    export_package: Optional[ExportPackage] = None
    quality_report: Optional[UnifiedQualityReport] = None
    failures: Tuple[ProductionFailureRecord, ...] = ()
    warnings: Tuple[str, ...] = ()
    timing_metrics: Dict[str, float] = None


class ProductionOrchestrator:
    """Master production runtime coordinator driving generation, quality, and repair convergence."""

    def __init__(
        self,
        strategy_registry: Optional[RepairStrategyRegistry] = None,
        rendered_quality_engine: Optional[MasterRenderedQualityEngine] = None,
        fidelity_validator: Optional[UnifiedFidelityValidator] = None,
    ) -> None:
        self.strategy_registry = strategy_registry or DEFAULT_STRATEGY_REGISTRY
        self.rendered_quality_engine = rendered_quality_engine or MasterRenderedQualityEngine()
        self.fidelity_validator = fidelity_validator or UnifiedFidelityValidator()

    async def produce(self, request: ProductionRequest) -> ProductionOutcome:
        """Executes full closed-loop generation and convergence for any of the 4 artifact types."""
        start_total = time.perf_counter()
        norm_type = request.artifact_type.strip().upper()
        profile = ArtifactExecutionProfileRegistry.get_profile(norm_type)

        job_id = request.job_id or f"job_{norm_type.lower()}_{int(time.time())}"
        out_dir = Path(request.output_dir) / job_id
        out_dir.mkdir(parents=True, exist_ok=True)

        artifact_name = request.output_filename or f"{norm_type.lower()}_artifact"
        version_manager = ProductionVersionManager(base_output_dir=out_dir, artifact_name=artifact_name)

        context = ArtifactProductionContext(
            job_id=job_id,
            artifact_type=norm_type,
            source_input=request.raw_input,
            output_dir=out_dir,
            source_metadata={"source_filename": request.source_filename},
        )
        observer = ProductionObservationAdapter(
            environment=request.observation_environment,
            output_dir=out_dir,
        )
        observer.observe_context(context, OBSERVATION_JOB_CREATED)

        failures: List[ProductionFailureRecord] = []

        try:
            observer.observe_context(context, OBSERVATION_PIPELINE_STARTED)
            # ── STAGE 1: SOURCE_VALIDATING & SOURCE_PARSED ──
            t0 = time.perf_counter()
            context.transition_state(ProductionState.SOURCE_VALIDATING, reason="Validating source raw input.")
            if not request.raw_input or not request.raw_input.strip():
                raise ValueError("Raw input content cannot be empty.")
            context.transition_state(ProductionState.SOURCE_PARSED, reason="Source input verified.")
            context.record_stage_time("source_parsing", time.perf_counter() - t0)

            # ── STAGE 2: KNOWLEDGE_PROCESSING ──
            t0 = time.perf_counter()
            context.transition_state(ProductionState.KNOWLEDGE_PROCESSING, reason="Compiling knowledge manifest.")
            res_provider = request.resolution_provider or OfflineMockResolutionProvider()
            compiler = KnowledgeCompiler(resolution_provider=res_provider)
            manifest = await compiler.compile(request.raw_input, source_filename=request.source_filename)
            context.source_manifest = manifest
            context.transition_state(ProductionState.KNOWLEDGE_READY, reason="Universal knowledge manifest compiled.")
            context.record_stage_time("knowledge_processing", time.perf_counter() - t0)

            # ── STAGE 3: INTENT_RESOLUTION ──
            t0 = time.perf_counter()
            context.transition_state(ProductionState.INTENT_RESOLUTION, reason="Resolving artifact intent.")
            intent = profile.default_intent_factory()
            context.artifact_intent = intent
            context.transition_state(ProductionState.INTENT_READY, reason="Intent resolved from profile.")
            context.record_stage_time("intent_resolution", time.perf_counter() - t0)

            # ── STAGE 4: TRANSFORMATION ──
            t0 = time.perf_counter()
            context.transition_state(ProductionState.TRANSFORMATION, reason="Executing semantic transformation.")
            selection_engine = KnowledgeSelectionEngine()
            selected = selection_engine.select(manifest, intent)
            context.selected_knowledge = selected

            transformer = profile.transformer_factory()
            blueprint = transformer.transform(manifest, selected, intent)
            context.semantic_blueprint = blueprint
            context.transition_state(ProductionState.BLUEPRINT_READY, reason="Semantic blueprint created.")
            context.record_stage_time("transformation", time.perf_counter() - t0)

            # ── STAGE 5: GROUPING / COMPOSITION ──
            t0 = time.perf_counter()
            context.transition_state(ProductionState.GROUPING, reason="Bridging blueprint to render artifact.")
            bridge = profile.bridge_factory()
            render_artifact = bridge.bridge(blueprint)
            context.render_artifact = render_artifact
            context.transition_state(ProductionState.COMPOSITION_READY, reason="Render artifact composition ready.")
            context.record_stage_time("grouping_composition", time.perf_counter() - t0)

            # ── STAGE 6: RENDERING (Iteration 0) ──
            t0 = time.perf_counter()
            context.transition_state(ProductionState.RENDERING, reason="Rendering physical output via executor.")
            executor = profile.executor_factory()
            iter_0_dir = out_dir / "iteration_0"
            iter_0_dir.mkdir(parents=True, exist_ok=True)

            render_res = executor.execute_from_render_artifact(
                render_artifact=render_artifact,
                output_dir=iter_0_dir,
                output_filename=artifact_name,
            )
            context.render_result = render_res
            context.transition_state(ProductionState.RENDERED, reason="Physical rendering complete.")
            context.record_stage_time("rendering_iter_0", time.perf_counter() - t0)

            if not render_res.success:
                fail = ProductionFailureRecord(
                    failure_type=ProductionFailureType.RENDER_FAILURE,
                    owning_layer="RendererExecutor",
                    message=f"Renderer execution failed: {render_res.errors}",
                    recoverability="FATAL",
                    repair_eligible=False,
                    human_action_required=True,
                )
                failures.append(fail)
                context.transition_state(ProductionState.FAILED, reason="Initial rendering failed.")
                return ProductionOutcome(
                    success=False,
                    job_id=job_id,
                    artifact_type=norm_type,
                    final_state=ProductionState.FAILED,
                    decision=ExportDecision.BLOCKED,
                    overall_quality_score=0.0,
                    total_iterations=0,
                    failures=tuple(failures),
                    timing_metrics=context.timing_metrics,
                )

            # ── STAGE 7 & 8: QUALITY EVALUATION (Iteration 0) ──
            t0 = time.perf_counter()
            context.transition_state(ProductionState.QUALITY_EVALUATING, reason="Evaluating physical & semantic quality.")
            
            rendered_insp = None
            if render_res.pdf_path and Path(render_res.pdf_path).exists():
                rendered_insp = self.rendered_quality_engine.inspect(
                    pdf_path=render_res.pdf_path,
                    artifact_type=norm_type,
                    html_path=render_res.html_path,
                )

            fidelity_rep = None
            try:
                fidelity_rep = self.fidelity_validator.validate(blueprint, render_artifact)
            except Exception as e:
                logger.debug("Fidelity validation exception: %s", e)

            quality_report = UnifiedQualityAuthority.evaluate_artifact(
                artifact_type=norm_type,
                rendered_inspection=rendered_insp,
                fidelity_report=fidelity_rep,
            )
            context.quality_authority_result = quality_report
            context.transition_state(ProductionState.QUALITY_EVALUATED, reason="Quality Authority evaluation complete.")
            context.record_stage_time("quality_eval_iter_0", time.perf_counter() - t0)
            observer.observe_context(context, OBSERVATION_QUALITY_AVAILABLE)

            # Record Iteration 0 Snapshot
            version_manager.record_iteration(
                iteration=0,
                blueprint=blueprint,
                html_path=render_res.html_path,
                pdf_path=render_res.pdf_path,
                quality_report=quality_report,
            )

            # ── STAGE 9: DECISION ROUTING ──
            route = QualityDecisionRouter.route_decision(quality_report)

            if route.action in (DecisionRouteAction.PROCEED_TO_EXPORT, DecisionRouteAction.PROCEED_TO_EXPORT_WITH_WARNINGS):
                # Clean pass or warnings pass directly
                target_approved_state = (
                    ProductionState.APPROVED_WITH_WARNINGS
                    if route.action == DecisionRouteAction.PROCEED_TO_EXPORT_WITH_WARNINGS
                    else ProductionState.APPROVED
                )
                context.transition_state(target_approved_state, reason=route.rationale)
                export_pkg = AuthorizedExportGate.verify_and_export(context, version_manager)
                context.record_stage_time("total_runtime", time.perf_counter() - start_total)

                return ProductionOutcome(
                    success=True,
                    job_id=job_id,
                    artifact_type=norm_type,
                    final_state=ProductionState.EXPORTED,
                    decision=quality_report.decision,
                    overall_quality_score=quality_report.overall_quality_score,
                    total_iterations=0,
                    export_package=export_pkg,
                    quality_report=quality_report,
                    warnings=tuple(quality_report.warnings),
                    timing_metrics=context.timing_metrics,
                )

            elif route.action in (DecisionRouteAction.HALT_MANUAL_REVIEW, DecisionRouteAction.HALT_BLOCKED):
                target_halt_state = (
                    ProductionState.MANUAL_REVIEW_REQUIRED
                    if route.action == DecisionRouteAction.HALT_MANUAL_REVIEW
                    else ProductionState.BLOCKED
                )
                context.transition_state(target_halt_state, reason=route.rationale)
                context.record_stage_time("total_runtime", time.perf_counter() - start_total)
                
                fail = ProductionFailureRecord(
                    failure_type=ProductionFailureType.QUALITY_FAILURE,
                    owning_layer="UnifiedQualityAuthority",
                    message=route.rationale,
                    recoverability="MANUAL_INTERVENTION" if target_halt_state == ProductionState.MANUAL_REVIEW_REQUIRED else "FATAL",
                    repair_eligible=False,
                    human_action_required=True,
                    diagnostics={"hard_blockers": list(quality_report.hard_blockers)},
                )
                failures.append(fail)

                # Phase 3D.1: Generate convergence failure report for manual review
                report_file = Path(context.output_dir) / "convergence_failure_report.md"
                qvec_0 = QualityVector.from_report(quality_report)
                crit_count = len([f for f in quality_report.findings if getattr(f, "severity", "") in ("CRITICAL", "BLOCKER")])
                p_vec_0 = ConvergenceProgressVector(
                    iteration=0,
                    hard_blocker_count=len(quality_report.hard_blockers),
                    critical_finding_count=crit_count,
                    affected_element_count=len(quality_report.findings),
                    root_cause_coverage=1.0,
                    quality_vector=qvec_0,
                    overall_score=quality_report.overall_quality_score,
                    drift=0.0,
                    mutation_cost=0.0,
                    applied_strategy_id=None,
                    applied_scope=None,
                )
                ConvergenceFailureReporter.generate_report(
                    context=context,
                    output_path=report_file,
                    progress_history=[p_vec_0],
                    detected_pattern=FailurePatternType.ROOT_CAUSE_MISMATCH,
                    pattern_rationale=route.rationale,
                    termination_cause=route.rationale,
                )

                return ProductionOutcome(
                    success=False,
                    job_id=job_id,
                    artifact_type=norm_type,
                    final_state=target_halt_state,
                    decision=quality_report.decision,
                    overall_quality_score=quality_report.overall_quality_score,
                    total_iterations=0,
                    quality_report=quality_report,
                    failures=tuple(failures),
                    warnings=tuple(quality_report.warnings),
                    timing_metrics=context.timing_metrics,
                )

            # ── STAGE 10: CLOSED-LOOP REPAIR LOOP ──
            max_iters = request.max_repair_iterations or profile.max_repair_iterations
            return await self._run_repair_loop(
                context=context,
                profile=profile,
                version_manager=version_manager,
                max_iterations=max_iters,
                artifact_name=artifact_name,
                start_total_time=start_total,
            )

        except Exception as exc:
            logger.exception("ProductionOrchestrator unhandled fatal exception: %s", exc)
            if context.state_machine.can_transition_to(ProductionState.FAILED):
                context.transition_state(ProductionState.FAILED, reason=str(exc))
            fail = ProductionFailureRecord(
                failure_type=ProductionFailureType.SYSTEM_ERROR,
                owning_layer="ProductionOrchestrator",
                message=str(exc),
                recoverability="FATAL",
                repair_eligible=False,
                human_action_required=True,
            )
            failures.append(fail)
            context.record_stage_time("total_runtime", time.perf_counter() - start_total)

            return ProductionOutcome(
                success=False,
                job_id=job_id,
                artifact_type=norm_type,
                final_state=ProductionState.FAILED,
                decision=ExportDecision.BLOCKED,
                overall_quality_score=0.0,
                total_iterations=context.iteration,
                failures=tuple(failures),
                timing_metrics=context.timing_metrics,
            )
        finally:
            # Best effort only: return/exception semantics above remain sovereign.
            observer.observe_context(context, OBSERVATION_TERMINAL)

    async def _run_repair_loop(
        self,
        context: ArtifactProductionContext,
        profile: ArtifactExecutionProfile,
        version_manager: ProductionVersionManager,
        max_iterations: int,
        artifact_name: str,
        start_total_time: float,
    ) -> ProductionOutcome:
        """Executes closed-loop targeted repairs with atomic transactions and convergence control."""
        convergence_controller = ProductionConvergenceController(max_iterations=max_iterations)
        budget_tracker = MutationBudgetTracker(get_budget_for_artifact(context.artifact_type))
        outcome_reg = RepairOutcomeRegistry.get_instance()
        failures: List[ProductionFailureRecord] = []

        current_blueprint = copy.deepcopy(context.semantic_blueprint)
        current_report = context.quality_authority_result
        current_score = current_report.overall_quality_score if current_report else 0.70

        approved_iteration: Optional[int] = None
        export_package: Optional[ExportPackage] = None

        # Initialize progress history and effectiveness tracking at Iteration 0
        strategy_memory = SelfDisqualifyingStrategyMemory()
        recorded_attempts: List[RepairAttempt] = []
        recorded_effectiveness: List[RepairEffectivenessResult] = []
        recorded_rejections: List[StrategyRejectionRecord] = []
        recorded_escalations: List[RepairEscalationDecision] = []
        domain_fingerprints: List[DomainFingerprint] = [
            DomainFingerprinter.fingerprint(context.artifact_type, current_blueprint)
        ]

        iter_0_findings = current_report.findings if current_report else []
        iter_0_blockers = current_report.hard_blockers if current_report else []
        crit_0 = len([f for f in iter_0_findings if getattr(f, "severity", "") in ("CRITICAL", "BLOCKER")])
        qvec_0 = QualityVector.from_report(current_report) if current_report else QualityVector()
        progress_history: List[ConvergenceProgressVector] = [
            ConvergenceProgressVector(
                iteration=0,
                hard_blocker_count=len(iter_0_blockers),
                critical_finding_count=crit_0,
                affected_element_count=len(iter_0_findings),
                root_cause_coverage=1.0,
                quality_vector=qvec_0,
                overall_score=current_score,
                drift=0.0,
                mutation_cost=0.0,
                applied_strategy_id=None,
                applied_scope=None,
            )
        ]

        latest_pattern = FailurePatternType.HEALTHY_PROGRESS
        latest_pattern_rationale = ""

        while context.iteration < max_iterations:
            context.iteration += 1
            iter_num = context.iteration
            convergence_controller.advance_iteration()

            context.transition_state(
                ProductionState.REPAIR_ANALYZING,
                reason=f"Beginning repair analysis for cycle {iter_num}/{max_iterations}."
            )

            # Analyze failure pattern from progress history
            latest_pattern, latest_pattern_rationale = RepairFailurePatternDetector.analyze_history(progress_history)
            allowed_scopes = BudgetReservationPolicy.get_allowed_scopes_for_iteration(
                iteration=iter_num,
                max_iterations=max_iterations,
                pattern=latest_pattern,
            )

            # 1. Non-repairable Finding Check
            non_repairables = [
                f for f in current_report.findings
                if f.failure_code in ("SOURCE_CONTRADICTION", "EXTRACTION_AMBIGUITY")
            ]
            if non_repairables:
                context.transition_state(
                    ProductionState.MANUAL_REVIEW_REQUIRED,
                    reason="Non-repairable source contradiction requires manual editorial review."
                )
                fail = ProductionFailureRecord(
                    failure_type=ProductionFailureType.SAFETY_VIOLATION,
                    owning_layer="RepairEscalationRouter",
                    message="Non-repairable source contradiction detected.",
                    recoverability="MANUAL_INTERVENTION",
                    repair_eligible=False,
                    human_action_required=True,
                )
                failures.append(fail)
                report_file = Path(context.output_dir) / "convergence_failure_report.md"
                ConvergenceFailureReporter.generate_report(
                    context=context,
                    output_path=report_file,
                    progress_history=progress_history,
                    detected_pattern=FailurePatternType.ROOT_CAUSE_MISMATCH,
                    pattern_rationale="Non-repairable source contradiction present in knowledge extraction.",
                    termination_cause="Non-repairable source contradiction requires manual editorial review.",
                )
                break

            # 2. Escalation & Root Cause Attribution
            hypotheses = DeterministicRootCauseAnalyzer.analyze(
                findings=current_report.findings,
                clusters=current_report.finding_clusters,
                artifact_type=context.artifact_type,
            )

            if not hypotheses:
                context.transition_state(
                    ProductionState.BLOCKED,
                    reason="No viable root cause hypothesis inferred for current quality findings."
                )
                report_file = Path(context.output_dir) / "convergence_failure_report.md"
                ConvergenceFailureReporter.generate_report(
                    context=context,
                    output_path=report_file,
                    progress_history=progress_history,
                    detected_pattern=FailurePatternType.ROOT_CAUSE_MISMATCH,
                    pattern_rationale="Deterministic root cause analyzer found no hypothesis for current findings.",
                    termination_cause="No viable root cause hypothesis inferred for current quality findings.",
                )
                break

            # 3. Portfolio-Based Repair Planning with Strict Firewall & Disqualification Memory
            context.transition_state(ProductionState.REPAIR_PLANNING, reason="Evaluating candidate repair portfolio.")
            all_strats = list(self.strategy_registry.all_strategies())

            # Step 3a: Hard Artifact Compatibility Firewall Filtering (including Stage 5 Actuator Capability)
            eligible_strats, rejections = RepairStrategyCompatibilityFirewall.filter_eligible_strategies(
                strategies=all_strats,
                artifact_type=context.artifact_type,
                require_actuator=True,
            )
            recorded_rejections.extend(rejections)

            # Step 3b: Filter out strategies disqualified by historical effectiveness memory
            current_signature = "|".join(sorted([f.failure_code for f in current_report.findings])) if current_report else ""
            qualified_strats = []
            for s in eligible_strats:
                disqualified = False
                for hyp in hypotheses:
                    is_disqual, dis_reason = strategy_memory.is_strategy_disqualified(
                        artifact_type=context.artifact_type,
                        artifact_id="default",
                        root_cause_cluster=hyp.cause_type.name,
                        strategy_id=s.strategy_id,
                        current_defect_signature=current_signature,
                    )
                    if is_disqual:
                        disqualified = True
                        recorded_rejections.append(
                            StrategyRejectionRecord(
                                strategy_id=s.strategy_id,
                                reason=dis_reason or "Disqualified by effectiveness memory.",
                                filter_stage="SELF_DISQUALIFICATION",
                            )
                        )
                        break
                if not disqualified:
                    qualified_strats.append(s)

            primary_defect = current_report.findings[0].failure_code if current_report.findings else None
            ineffective_penalties: Dict[str, float] = {}
            for s in qualified_strats:
                mult = outcome_reg.get_strategy_multiplier(
                    strategy_id=s.strategy_id,
                    defect_code=primary_defect,
                    artifact_type=context.artifact_type,
                )
                if mult != 1.0:
                    ineffective_penalties[s.strategy_id] = mult

            portfolio_candidates: List[CandidateRepairOption] = []
            for hyp in hypotheses:
                for target in hyp.affected_targets:
                    cands = RepairCandidatePortfolio.evaluate_portfolio(
                        strategies=qualified_strats,
                        target=target,
                        hypotheses=[hyp],
                        budget_tracker=budget_tracker,
                        blueprint=current_blueprint,
                        artifact_type=context.artifact_type,
                        total_findings_count=max(1, len(current_report.findings)),
                        ineffective_penalties=ineffective_penalties,
                    )
                    portfolio_candidates.extend(cands)

            # Sort combined candidate list
            portfolio_candidates.sort(
                key=lambda o: (
                    not o.is_budget_approved,
                    o.is_pareto_dominated,
                    -o.utility_score,
                    -o.leverage_score,
                )
            )

            # Apply scope reservation policy
            approved_scoped = [
                c for c in portfolio_candidates
                if c.is_budget_approved and not c.is_pareto_dominated and c.mutation_scope in allowed_scopes
            ]
            if not approved_scoped:
                # Fallback to any non-dominated budget-approved candidate
                approved_scoped = [c for c in portfolio_candidates if c.is_budget_approved and not c.is_pareto_dominated]
            if not approved_scoped:
                # Fallback to any budget-approved candidate
                approved_scoped = [c for c in portfolio_candidates if c.is_budget_approved]

            best_candidate = approved_scoped[0] if approved_scoped else None
            best_strategy = self.strategy_registry.get_strategy(best_candidate.strategy_id) if best_candidate else None

            if not best_candidate or not best_strategy:
                # No budget-approved candidate available
                context.transition_state(
                    ProductionState.MANUAL_REVIEW_REQUIRED,
                    reason="Repair budget exhausted or no valid candidate repair strategy found."
                )
                fail = ProductionFailureRecord(
                    failure_type=ProductionFailureType.REPAIR_FAILURE,
                    owning_layer="MinimalInterventionRepairPlanner",
                    message="No repair candidates approved within remaining mutation budget.",
                    recoverability="MANUAL_INTERVENTION",
                    repair_eligible=False,
                    human_action_required=True,
                )
                failures.append(fail)
                report_file = Path(context.output_dir) / "convergence_failure_report.md"
                ConvergenceFailureReporter.generate_report(
                    context=context,
                    output_path=report_file,
                    progress_history=progress_history,
                    detected_pattern=latest_pattern,
                    pattern_rationale=latest_pattern_rationale,
                    termination_cause="Repair budget exhausted or no valid candidate repair strategy found.",
                )
                break

            # 4. Atomic Repair Transaction Execution
            context.transition_state(
                ProductionState.REPAIRING,
                reason=f"Applying atomic mutation '{best_candidate.strategy_id}' (Scope: {best_candidate.mutation_scope.name})."
            )

            current_decision = UnifiedQualityDecision(
                decision=current_report.decision,
                can_export=current_report.can_export,
                repair_required=current_report.repair_required,
                hard_blockers=current_report.hard_blockers,
                warnings=current_report.warnings,
                rationale=current_report.summary,
            )

            mutated_bp, tx_rec, committed = RepairTransactionManager.execute_transaction(
                current_blueprint=current_blueprint,
                candidate=best_candidate,
                strategy=best_strategy,
                budget_tracker=budget_tracker,
                current_decision=current_decision,
                current_score=current_score,
                artifact_type=context.artifact_type,
                iteration=iter_num,
            )

            context.repair_history.append(tx_rec)

            if not committed:
                logger.warning("Repair transaction rolled back: %s", tx_rec.rollback_reason)
                fail = ProductionFailureRecord(
                    failure_type=ProductionFailureType.REPAIR_FAILURE,
                    owning_layer="RepairTransactionManager",
                    message=f"Repair rolled back: {tx_rec.rollback_reason}",
                    recoverability="RECOVERABLE",
                    repair_eligible=True,
                    human_action_required=False,
                )
                failures.append(fail)
                continue

            current_blueprint = mutated_bp
            context.semantic_blueprint = mutated_bp

            # 5. Re-render Affected Scope (Iteration n)
            context.transition_state(ProductionState.RE_RENDERING, reason=f"Re-rendering iteration {iter_num}.")
            bridge = profile.bridge_factory()
            new_render_art = bridge.bridge(current_blueprint)
            context.render_artifact = new_render_art

            executor = profile.executor_factory()
            iter_dir = Path(context.output_dir) / f"iteration_{iter_num}"
            iter_dir.mkdir(parents=True, exist_ok=True)

            # Phase 4: Generate and persist transformation diff
            if tx_rec.actuator_result is not None:
                try:
                    from app.quality.repair.actuation.diff_system import TransformationDiffSystem
                    diff_report = TransformationDiffSystem.generate_diff(
                        actuator_result=tx_rec.actuator_result,
                        artifact_type=context.artifact_type,
                        before_blueprint=context.semantic_blueprint,
                        after_blueprint=mutated_bp,
                        iteration=iter_num,
                    )
                    TransformationDiffSystem.write_diff_artifacts(diff_report, iter_dir)
                    TransformationDiffSystem.write_diff_artifacts(diff_report, Path(context.output_dir))
                except Exception as diff_err:
                    logger.warning(f"Could not generate transformation diff: {diff_err}")

            new_render_res = executor.execute_from_render_artifact(
                render_artifact=new_render_art,
                output_dir=iter_dir,
                output_filename=artifact_name,
            )
            context.render_result = new_render_res

            # 6. Re-evaluate Quality through UnifiedQualityAuthority
            context.transition_state(ProductionState.RE_VALIDATING, reason=f"Re-evaluating quality for iteration {iter_num}.")
            rendered_insp = None
            if new_render_res.pdf_path and Path(new_render_res.pdf_path).exists():
                rendered_insp = self.rendered_quality_engine.inspect(
                    pdf_path=new_render_res.pdf_path,
                    artifact_type=context.artifact_type,
                    html_path=new_render_res.html_path,
                )

            fidelity_rep = None
            try:
                fidelity_rep = self.fidelity_validator.validate(current_blueprint, new_render_art)
            except Exception:
                pass

            re_report = UnifiedQualityAuthority.evaluate_artifact(
                artifact_type=context.artifact_type,
                rendered_inspection=rendered_insp,
                fidelity_report=fidelity_rep,
            )
            context.quality_authority_result = re_report
            context.transition_state(ProductionState.QUALITY_EVALUATED, reason=f"Iteration {iter_num} evaluated.")

            # Record versioned snapshot
            state_hash = tx_rec.after_state_hash or hashlib.sha256(str(time.time()).encode()).hexdigest()
            version_manager.record_iteration(
                iteration=iter_num,
                blueprint=current_blueprint,
                html_path=new_render_res.html_path,
                pdf_path=new_render_res.pdf_path,
                quality_report=re_report,
                transaction_record=tx_rec,
            )

            # Compute Domain Fingerprint
            post_fp = DomainFingerprinter.fingerprint(context.artifact_type, current_blueprint)
            domain_fingerprints.append(post_fp)

            # Detect Zero-Effect Mutation
            pre_fp = domain_fingerprints[-2] if len(domain_fingerprints) >= 2 else post_fp
            prev_codes = [f.failure_code for f in (current_report.findings if current_report else ())]
            new_codes = [f.failure_code for f in re_report.findings]
            target_codes = [f.failure_code for f in best_candidate.hypothesis.supporting_findings] or ([primary_defect] if primary_defect else [])

            is_zero_effect, zero_reason = ZeroEffectMutationDetector.detect_zero_effect(
                pre_fingerprint=pre_fp,
                post_fingerprint=post_fp,
                pre_state_hash=tx_rec.before_state_hash,
                post_state_hash=tx_rec.after_state_hash,
                pre_findings=prev_codes,
                post_findings=new_codes,
                targeted_finding_codes=target_codes,
            )

            # Create RepairAttempt
            attempt = RepairAttempt(
                attempt_id=f"attempt_{iter_num}_{best_candidate.strategy_id}",
                artifact_type=context.artifact_type,
                iteration=iter_num,
                finding_ids=tuple(target_codes),
                root_cause_ids=(best_candidate.hypothesis.cause_type.name,),
                strategy_id=best_strategy.strategy_id,
                mutation_scope=best_candidate.mutation_scope,
                owning_layer=getattr(best_strategy, "owning_layer", "R1"),
                pre_state_hash=tx_rec.before_state_hash,
                post_state_hash=tx_rec.after_state_hash,
                mutation_cost=tx_rec.mutation_cost,
                blast_radius=tx_rec.blast_radius,
                execution_status=RepairExecutionStatus.COMMITTED if committed else RepairExecutionStatus.ROLLED_BACK,
            )
            recorded_attempts.append(attempt)

            # Evaluate Decoupled Effectiveness
            eff_result = RepairEffectivenessResult.evaluate(
                attempt=attempt,
                pre_blockers=current_report.hard_blockers if current_report else (),
                post_blockers=re_report.hard_blockers,
                pre_findings=prev_codes,
                post_findings=new_codes,
                pre_score=current_score,
                post_score=re_report.overall_quality_score,
                drift_score=tx_rec.drift_score,
                causal_reach_score=1.0 if not is_zero_effect else 0.2,
            )
            if is_zero_effect:
                eff_result = eff_result.model_copy(update={
                    "overall_status": EffectivenessStatus.ZERO_EFFECT,
                    "rationale": zero_reason,
                })
            recorded_effectiveness.append(eff_result)

            # Record in Strategy History Memory
            history_key = StrategyHistoryKey(
                artifact_type=context.artifact_type,
                artifact_id="default",
                root_cause_cluster=best_candidate.hypothesis.cause_type.name,
                strategy_id=best_strategy.strategy_id,
            )
            strategy_memory.record_attempt_result(
                key=history_key,
                result=eff_result,
                defect_signature=current_signature,
                post_state_hash=tx_rec.after_state_hash,
            )

            # Record empirical outcome in outcome registry
            prev_blockers_cnt = len(current_report.hard_blockers) if current_report else 0
            new_blockers_cnt = len(re_report.hard_blockers)
            blocker_delta = new_blockers_cnt - prev_blockers_cnt
            qual_delta = re_report.overall_quality_score - current_score
            step_success = (blocker_delta < 0) or (re_report.can_export) or (re_report.overall_quality_score > current_score and blocker_delta <= 0 and not is_zero_effect)

            outcome_reg.record_outcome(
                artifact_type=context.artifact_type,
                defect_code=primary_defect or "DEFECT",
                root_cause_type=best_candidate.hypothesis.cause_type.value if hasattr(best_candidate.hypothesis.cause_type, 'value') else str(best_candidate.hypothesis.cause_type),
                strategy_id=best_strategy.strategy_id,
                mutation_scope=best_candidate.mutation_scope.name if hasattr(best_candidate.mutation_scope, 'name') else str(best_candidate.mutation_scope),
                quality_delta=qual_delta,
                blocker_delta=blocker_delta,
                success=step_success,
            )

            # Update progress history
            re_crits = len([f for f in re_report.findings if getattr(f, "severity", "") in ("CRITICAL", "BLOCKER")])
            progress_history.append(
                ConvergenceProgressVector(
                    iteration=iter_num,
                    hard_blocker_count=new_blockers_cnt,
                    critical_finding_count=re_crits,
                    affected_element_count=len(re_report.findings),
                    root_cause_coverage=1.0,
                    quality_vector=QualityVector.from_report(re_report),
                    overall_score=re_report.overall_quality_score,
                    drift=tx_rec.drift_score,
                    mutation_cost=tx_rec.mutation_cost,
                    applied_strategy_id=best_strategy.strategy_id,
                    applied_scope=best_candidate.mutation_scope,
                )
            )

            current_report = re_report
            current_score = re_report.overall_quality_score

            # 7. Evaluate Convergence
            conv_check = convergence_controller.evaluate(re_report, state_hash)

            if conv_check.should_terminate:
                if conv_check.can_export:
                    approved_iteration = iter_num
                    target_approved_state = (
                        ProductionState.APPROVED_WITH_WARNINGS
                        if conv_check.outcome == ProductionConvergenceOutcome.CONVERGED_WITH_WARNINGS
                        else ProductionState.APPROVED
                    )
                    context.transition_state(target_approved_state, reason=conv_check.rationale)
                    export_package = AuthorizedExportGate.verify_and_export(context, version_manager)
                    context.convergence_state = ConvergenceState.CONVERGED
                    break
                else:
                    if conv_check.outcome == ProductionConvergenceOutcome.BLOCKED:
                        context.transition_state(
                            ProductionState.BLOCKED,
                            reason=conv_check.rationale
                        )
                        context.convergence_state = ConvergenceState.NO_SAFE_REPAIR
                    elif conv_check.outcome in (
                        ProductionConvergenceOutcome.OSCILLATION_DETECTED,
                        ProductionConvergenceOutcome.BUDGET_EXHAUSTED,
                        ProductionConvergenceOutcome.NO_POSITIVE_PROGRESS,
                        ProductionConvergenceOutcome.REPAIR_SCOPE_EXHAUSTED,
                        ProductionConvergenceOutcome.MANUAL_REVIEW_REQUIRED,
                    ):
                        context.transition_state(
                            ProductionState.MANUAL_REVIEW_REQUIRED,
                            reason=conv_check.rationale
                        )
                        if conv_check.outcome == ProductionConvergenceOutcome.OSCILLATION_DETECTED:
                            context.convergence_state = ConvergenceState.OSCILLATION_DETECTED
                        elif conv_check.outcome == ProductionConvergenceOutcome.BUDGET_EXHAUSTED:
                            context.convergence_state = ConvergenceState.BUDGET_EXHAUSTED
                        else:
                            context.convergence_state = ConvergenceState.NO_SAFE_REPAIR
                    else:
                        context.transition_state(
                            ProductionState.BLOCKED,
                            reason=conv_check.rationale
                        )
                        context.convergence_state = ConvergenceState.NO_SAFE_REPAIR

                    # Phase 3D.1: Generate convergence failure report for manual review
                    report_file = Path(context.output_dir) / "convergence_failure_report.md"
                    ConvergenceFailureReporter.generate_report(
                        context=context,
                        output_path=report_file,
                        progress_history=progress_history,
                        detected_pattern=latest_pattern,
                        pattern_rationale=latest_pattern_rationale,
                        termination_cause=conv_check.rationale,
                    )
                    break

        if not export_package and context.state_machine.current_state not in (
            ProductionState.APPROVED,
            ProductionState.APPROVED_WITH_WARNINGS,
            ProductionState.EXPORTED,
            ProductionState.MANUAL_REVIEW_REQUIRED,
            ProductionState.BLOCKED,
            ProductionState.FAILED,
        ):
            context.transition_state(
                ProductionState.MANUAL_REVIEW_REQUIRED,
                reason="Maximum repair iterations reached without achieving exportable quality.",
            )
            report_file = Path(context.output_dir) / "convergence_failure_report.md"
            ConvergenceFailureReporter.generate_report(
                context=context,
                output_path=report_file,
                progress_history=progress_history,
                detected_pattern=latest_pattern,
                pattern_rationale=latest_pattern_rationale,
                termination_cause="Maximum repair iterations reached without achieving exportable quality.",
            )

        final_success = export_package is not None and context.state_machine.current_state == ProductionState.EXPORTED

        if not final_success:
            from app.quality.repair.effectiveness.coverage_matrix import RootCauseCoverageMatrix
            term_cause = "Convergence terminated without export."
            disquals = []
            if current_report and current_report.findings:
                first_code = current_report.findings[0].failure_code
                cov = RootCauseCoverageMatrix.lookup(first_code, context.artifact_type)
                rc_name = cov.root_cause.name if cov else "UNKNOWN"
                disquals = strategy_memory.get_disqualified_strategies(context.artifact_type, "default", rc_name)

            RepairForensicsExporter.export_forensics(
                context=context,
                output_dir=Path(context.output_dir),
                attempts=recorded_attempts,
                effectiveness_results=recorded_effectiveness,
                disqualified_strategies=disquals,
                rejections=recorded_rejections,
                escalation_decisions=recorded_escalations,
                domain_fingerprints=domain_fingerprints,
                final_failure_reason=term_cause,
                recommended_owning_layer="R1",
            )

        context.record_stage_time("total_runtime", time.perf_counter() - start_total_time)

        final_success = export_package is not None and context.state_machine.current_state == ProductionState.EXPORTED

        return ProductionOutcome(
            success=final_success,
            job_id=context.job_id,
            artifact_type=context.artifact_type,
            final_state=context.state_machine.current_state,
            decision=current_report.decision if current_report else ExportDecision.BLOCKED,
            overall_quality_score=current_report.overall_quality_score if current_report else 0.0,
            total_iterations=context.iteration,
            export_package=export_package,
            quality_report=current_report,
            failures=tuple(failures),
            warnings=tuple(current_report.warnings) if current_report else (),
            timing_metrics=context.timing_metrics,
        )

    produce_artifact = produce
