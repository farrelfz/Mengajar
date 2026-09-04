"""
Master Production Orchestrator: Executes DAG workflows, enforces state transitions, manages quality gates, retries, refinement loops, checkpoints, and deterministic replay.
"""

from __future__ import annotations

import time
from typing import Any
from app.orchestration.artifacts import ArtifactRegistry
from app.orchestration.checkpoints import CheckpointStore, InMemoryCheckpointStore, WorkflowCheckpoint
from app.orchestration.contracts import (
    FailureCategory,
    FailureSeverity,
    GateDecisionEnum,
    ProductionFailure,
    ProductionGateResult,
    ProductionJobContext,
    ProductionJobRequest,
    ProductionJobResult,
    ProductionJobStatus,
    StageExecutionResult,
    StageState,
)
from app.orchestration.gates import ProductionGate
from app.orchestration.idempotency import IdempotencyRegistry
from app.orchestration.profiles import PipelineProfileRegistry, PipelineProfileType
from app.orchestration.refinement_loop import RefinementLoopController
from app.orchestration.retry import RetryPolicy
from app.orchestration.stages import (
    ArtifactValidationStage,
    BlueprintGenerationStage,
    CompositionStage,
    CriticStage,
    DirectorStage,
    FinalizationStage,
    GroundingStage,
    PersonalizationStage,
    ProductionStage,
    QualityStage,
    RefinementStage,
    RenderingStage,
    RequestValidationStage,
)
from app.orchestration.state_machine import WorkflowStateMachine
from app.orchestration.trace import ExecutionTrace
from app.orchestration.workflow import WorkflowDefinition, WorkflowGraph
from app.observability import (
    observe_run,
    observe_span,
    record_event,
    record_exception,
    record_artifact,
    MetricsRegistry,
    FailureDiagnosticEngine,
    EventType,
    ObservationLevel,
    export_json,
)


class ProductionOrchestrator:
    """Master production runtime coordinator."""

    def __init__(
        self,
        checkpoint_store: CheckpointStore | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self.checkpoint_store = checkpoint_store or InMemoryCheckpointStore()
        self.retry_policy = retry_policy or RetryPolicy()
        self.artifact_registry = ArtifactRegistry()
        self.stages: dict[str, ProductionStage] = {
            "request_validation": RequestValidationStage(),
            "directing": DirectorStage(),
            "personalization": PersonalizationStage(),
            "grounding": GroundingStage(),
            "blueprint_generation": BlueprintGenerationStage(),
            "composition": CompositionStage(),
            "pre_render_quality": QualityStage(),
            "critic_review": CriticStage(),
            "refinement": RefinementStage(),
            "rendering": RenderingStage(),
            "artifact_validation": ArtifactValidationStage(),
            "finalization": FinalizationStage(),
        }

    def register_stage(self, stage: ProductionStage) -> None:
        self.stages[stage.stage_id] = stage

    def run(
        self,
        request: ProductionJobRequest,
        workflow: WorkflowDefinition | None = None,
        shared_context_data: dict[str, Any] | None = None,
    ) -> ProductionJobResult:
        """Run a production job deterministically through DAG orchestration."""
        with observe_run(request.metadata.profile) as run_id:
            start_time = time.perf_counter()

            # 1. Idempotency Check
            idempotency_key = request.idempotency_key or IdempotencyRegistry.compute_key(request)
            cached = IdempotencyRegistry.get_result(idempotency_key)
            if cached:
                record_event(
                    EventType.DIAGNOSTIC_EMITTED,
                    message="Idempotent request cache hit, returning cached job result.",
                    attributes={"job_id": request.job_id, "idempotency_key": idempotency_key}
                )
                return cached

            # 2. Resolve Workflow Definition
            if workflow is None:
                profile_name = request.metadata.profile
                workflow = PipelineProfileRegistry.get_workflow(profile_name)

            # 3. Validate DAG
            graph = WorkflowGraph(workflow)
            dag_errors = graph.validate()
            if dag_errors:
                dur = (time.perf_counter() - start_time) * 1000.0
                fail_res = ProductionFailure(
                    stage_id="orchestrator",
                    category=FailureCategory.DEPENDENCY,
                    severity=FailureSeverity.CRITICAL,
                    message=f"DAG validation failed: {'; '.join(dag_errors)}",
                )
                
                # Report failure diagnostic
                exc = ValueError(fail_res.message)
                FailureDiagnosticEngine.capture_failure(
                    exc,
                    stage="orchestrator",
                    component="ProductionOrchestrator",
                )

                return ProductionJobResult(
                    job_id=request.job_id,
                    status=ProductionJobStatus.FAILED,
                    success=False,
                    failures=[fail_res],
                    execution_duration_ms=round(dur, 2),
                )

            execution_order = graph.get_execution_order()

            # 4. Initialize State Machine, Context, and Trace
            sm = WorkflowStateMachine(workflow)
            sm.transition_job(ProductionJobStatus.RUNNING)

            ctx = ProductionJobContext(
                job_id=request.job_id,
                request=request,
                shared_data=shared_context_data or {},
            )
            trace = ExecutionTrace(job_id=request.job_id)
            trace.log_event("JOB_CREATED", message=f"Job '{request.job_id}' started with profile '{request.metadata.profile}'.")

            stage_history: list[str] = []
            failures: list[ProductionFailure] = []

            # Register initial request metadata as lineage input
            record_artifact(
                artifact_id="request",
                artifact_path=f"outputs/production_orchestration/{request.job_id}/request.json",
                artifact_type="request",
                metadata={"prompt": request.raw_input, "profile": request.metadata.profile}
            )

            # 5. Execute DAG in topological order
            idx = 0
            while idx < len(execution_order):
                sid = execution_order[idx]
                stage = self.stages.get(sid)
                if not stage:
                    idx += 1
                    continue

                # Check if stage is blocked or ready
                if not sm.is_stage_ready(sid):
                    # If optional dependency failed/skipped, mark skipped
                    node = workflow.nodes[sid]
                    if node.optional:
                        sm.transition_stage(sid, StageState.SKIPPED)
                        trace.log_event("STAGE_SKIPPED", stage_id=sid, message=f"Optional stage '{sid}' skipped.")
                    idx += 1
                    continue

                sm.transition_stage(sid, StageState.READY)
                sm.transition_stage(sid, StageState.RUNNING)
                trace.log_event("STAGE_STARTED", stage_id=sid)

                # Stage execution with retry support
                attempt = 0
                res: StageExecutionResult | None = None
                
                # Wrap stage in span
                with observe_span(sid, component=stage.__class__.__name__, stage=sid) as span_id:
                    with MetricsRegistry.timer("stage.duration_ms", tags={"stage": sid}):
                        while True:
                            attempt += 1
                            try:
                                res = stage.execute(ctx)
                            except Exception as e:
                                record_exception(e, recoverable=False)
                                FailureDiagnosticEngine.capture_failure(
                                    e,
                                    stage=sid,
                                    component=stage.__class__.__name__,
                                    completed_stages=list(stage_history),
                                    partial_outputs=ctx.shared_data,
                                )
                                raise e

                            if res.state == StageState.SUCCEEDED or res.state == StageState.SKIPPED:
                                break

                            # Handle failure
                            if res.failure:
                                retry_dec = self.retry_policy.evaluate_retry(res.failure, attempt)
                                if retry_dec.should_retry:
                                    sm.transition_stage(sid, StageState.RETRYING)
                                    trace.log_event("STAGE_RETRY", stage_id=sid, message=retry_dec.reason)
                                    continue
                                else:
                                    break
                            break

                ctx.stage_results[sid] = res
                stage_history.append(sid)

                if res.state == StageState.SUCCEEDED:
                    sm.transition_stage(sid, StageState.SUCCEEDED)
                    trace.log_event("STAGE_COMPLETED", stage_id=sid, metadata=res.output)
                    
                    # Register intermediate and final artifacts into lineage
                    if sid == "blueprint_generation":
                        record_artifact(
                            artifact_id="blueprint",
                            artifact_path=f"outputs/production_orchestration/{request.job_id}/blueprint.json",
                            artifact_type="blueprint",
                            parent_artifacts=["request"],
                        )
                    elif sid == "composition":
                        record_artifact(
                            artifact_id="composition",
                            artifact_path=f"outputs/production_orchestration/{request.job_id}/composition.json",
                            artifact_type="composition",
                            parent_artifacts=["blueprint"],
                        )
                    elif sid == "rendering":
                        pdf_path = ctx.shared_data.get("pdf_path") or f"outputs/production_orchestration/{request.job_id}/{request.job_id}.pdf"
                        record_artifact(
                            artifact_id="pdf",
                            artifact_path=pdf_path,
                            artifact_type="PDF",
                            parent_artifacts=["composition"],
                            metadata={"page_count": 3}
                        )
                elif res.state == StageState.SKIPPED:
                    sm.transition_stage(sid, StageState.SKIPPED)
                    trace.log_event("STAGE_SKIPPED", stage_id=sid)
                else:
                    sm.transition_stage(sid, StageState.FAILED)
                    trace.log_event("STAGE_FAILED", stage_id=sid, message=res.failure.message if res.failure else "")
                    if res.failure:
                        failures.append(res.failure)
                        exc = ValueError(res.failure.message)
                        FailureDiagnosticEngine.capture_failure(
                            exc,
                            stage=sid,
                            component=stage.__class__.__name__,
                            completed_stages=list(stage_history),
                            partial_outputs=ctx.shared_data,
                        )
                    sm.propagate_failure(sid)
                    break

                # Evaluate Grounding Gate if stage is Grounding
                if sid == "grounding":
                    g_gate = ProductionGate.evaluate_grounding_gate(ctx)
                    ctx.gate_results.append(g_gate)
                    
                    # Record metric for grounding contradictions
                    MetricsRegistry.set("grounding.contradictions", len(g_gate.contradicting_claims))
                    
                    if g_gate.decision == GateDecisionEnum.BLOCK:
                        trace.log_event("GATE_EVALUATED", stage_id=sid, message=f"Grounding Gate BLOCK: {g_gate.reasoning}")
                        fail_item = ProductionFailure(
                            stage_id=sid,
                            category=FailureCategory.GROUNDING,
                            severity=FailureSeverity.CRITICAL,
                            message=g_gate.reasoning,
                        )
                        failures.append(fail_item)
                        
                        exc = ValueError(g_gate.reasoning)
                        FailureDiagnosticEngine.capture_failure(
                            exc,
                            stage=sid,
                            component="GroundingGate",
                            completed_stages=list(stage_history),
                            partial_outputs=ctx.shared_data,
                        )
                        
                        sm.propagate_failure(sid)
                        break

                # Evaluate Gate & Refinement Loop if stage is Quality
                if sid == "pre_render_quality":
                    q_rep = ctx.shared_data.get("quality_report")
                    if q_rep:
                        # Record metrics for quality score
                        MetricsRegistry.set("quality.score", q_rep.overall_score)
                        
                        if not q_rep.gate_result.can_proceed:
                            # Execute Critic and Refinement loop
                            critic_stage = self.stages.get("critic_review")
                            refine_stage = self.stages.get("refinement")
                            loop_ctrl = RefinementLoopController(max_iterations=3)

                            iter_count = 0
                            while iter_count < 3:
                                iter_count += 1
                                trace.log_event("REFINEMENT_STARTED", message=f"Iteration {iter_count}")
                                
                                # Record metric for refinement iteration count
                                MetricsRegistry.increment("refinement.iterations")
                                
                                # Trace loop operations inside spans
                                with observe_span(f"refinement_iteration_{iter_count}", component="RefinementLoop", stage="refinement"):
                                    if critic_stage:
                                        critic_stage.execute(ctx)
                                    if refine_stage:
                                        refine_stage.execute(ctx)
                                    
                                    # Re-run quality
                                    q_res = stage.execute(ctx)
                                    new_q = ctx.shared_data.get("quality_report")
                                    if not new_q:
                                        break

                                    score = new_q.overall_score
                                    MetricsRegistry.set("quality.score", score)
                                    
                                    dec = loop_ctrl.evaluate_next_iteration(score, iter_count)
                                    if new_q.gate_result.can_proceed or not dec.should_continue:
                                        trace.log_event("REFINEMENT_COMPLETED", message=dec.reason)
                                        break

                idx += 1

            # 6. Evaluate Final Outcome
            has_failed_stages = any(s in [StageState.FAILED, StageState.BLOCKED] for s in sm.stage_states.values()) or len(failures) > 0
            final_status = ProductionJobStatus.FAILED if has_failed_stages else ProductionJobStatus.COMPLETED
            sm.transition_job(final_status)
            trace.log_event("JOB_COMPLETED" if final_status == ProductionJobStatus.COMPLETED else "JOB_FAILED")

            # Save checkpoint
            chk = InMemoryCheckpointStore.create_checkpoint_from_context(ctx)
            self.checkpoint_store.save(chk)

            dur_ms = (time.perf_counter() - start_time) * 1000.0
            pdf_path = ctx.shared_data.get("pdf_path")

            result = ProductionJobResult(
                job_id=request.job_id,
                status=final_status,
                success=final_status == ProductionJobStatus.COMPLETED,
                output_artifacts=ctx.artifacts,
                pdf_path=pdf_path,
                gate_results=ctx.gate_results,
                stage_history=stage_history,
                failures=failures,
                execution_duration_ms=round(dur_ms, 2),
                metadata=request.metadata.model_dump(),
            )

            IdempotencyRegistry.record_result(idempotency_key, request.job_id, result)
            
            # Export trace manifest JSON
            export_json(run_id, f"outputs/production_orchestration/{request.job_id}/observability_manifest.json")
            
            return result

    def resume(self, checkpoint_id: str, request: ProductionJobRequest) -> ProductionJobResult:
        """Resume execution of a job from a saved checkpoint."""
        with observe_run(request.metadata.profile) as run_id:
            chk = self.checkpoint_store.get(checkpoint_id)
            if not chk:
                raise KeyError(f"Checkpoint '{checkpoint_id}' not found.")

            # Restore context
            ctx = InMemoryCheckpointStore.restore_context(chk, request)
            workflow = PipelineProfileRegistry.get_workflow(request.metadata.profile)
            graph = WorkflowGraph(workflow)
            execution_order = graph.get_execution_order()

            # Filter out already completed stages
            remaining_stages = [s for s in execution_order if s not in chk.completed_stages]

            # Register initial request metadata as lineage input
            record_artifact(
                artifact_id="request",
                artifact_path=f"outputs/production_orchestration/{request.job_id}/request.json",
                artifact_type="request",
                metadata={"prompt": request.raw_input, "profile": request.metadata.profile}
            )

            # Continue execution
            start_time = time.perf_counter()
            stage_history = list(chk.completed_stages)
            failures: list[ProductionFailure] = []

            for sid in remaining_stages:
                stage = self.stages.get(sid)
                if not stage:
                    continue

                with observe_span(sid, component=stage.__class__.__name__, stage=sid) as span_id:
                    with MetricsRegistry.timer("stage.duration_ms", tags={"stage": sid}):
                        try:
                            res = stage.execute(ctx)
                        except Exception as e:
                            record_exception(e, recoverable=False)
                            FailureDiagnosticEngine.capture_failure(
                                e,
                                stage=sid,
                                component=stage.__class__.__name__,
                                completed_stages=list(stage_history),
                                partial_outputs=ctx.shared_data,
                            )
                            raise e
                        
                        ctx.stage_results[sid] = res
                        stage_history.append(sid)
                        
                        if res.state == StageState.FAILED:
                            if res.failure:
                                failures.append(res.failure)
                                exc = ValueError(res.failure.message)
                                FailureDiagnosticEngine.capture_failure(
                                    exc,
                                    stage=sid,
                                    component=stage.__class__.__name__,
                                    completed_stages=list(stage_history),
                                    partial_outputs=ctx.shared_data,
                                )
                            break
                        
                        # Register intermediate and final artifacts
                        if sid == "blueprint_generation":
                            record_artifact(
                                artifact_id="blueprint",
                                artifact_path=f"outputs/production_orchestration/{request.job_id}/blueprint.json",
                                artifact_type="blueprint",
                                parent_artifacts=["request"],
                            )
                        elif sid == "composition":
                            record_artifact(
                                artifact_id="composition",
                                artifact_path=f"outputs/production_orchestration/{request.job_id}/composition.json",
                                artifact_type="composition",
                                parent_artifacts=["blueprint"],
                            )
                        elif sid == "rendering":
                            pdf_path = ctx.shared_data.get("pdf_path") or f"outputs/production_orchestration/{request.job_id}/{request.job_id}.pdf"
                            record_artifact(
                                artifact_id="pdf",
                                artifact_path=pdf_path,
                                artifact_type="PDF",
                                parent_artifacts=["composition"],
                            )

            dur_ms = (time.perf_counter() - start_time) * 1000.0
            success = len(failures) == 0

            result = ProductionJobResult(
                job_id=request.job_id,
                status=ProductionJobStatus.COMPLETED if success else ProductionJobStatus.FAILED,
                success=success,
                output_artifacts=ctx.artifacts,
                pdf_path=ctx.shared_data.get("pdf_path"),
                gate_results=ctx.gate_results,
                stage_history=stage_history,
                failures=failures,
                execution_duration_ms=round(dur_ms, 2),
            )
            
            # Export trace manifest JSON
            export_json(run_id, f"outputs/production_orchestration/{request.job_id}/observability_manifest.json")
            
            return result
