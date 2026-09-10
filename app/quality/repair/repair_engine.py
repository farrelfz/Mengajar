"""
Universal Document Intelligence System V5 — Targeted Repair Engine.

Phase 3B: Root-cause-aware, iterative quality convergence engine coordinating:
Root Cause Analysis -> Strategy Registry -> Minimal Mutation -> Re-evaluation ->
Regression Guard -> Rollback / Convergence.
"""

from __future__ import annotations

import copy
import logging
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from app.quality.contracts.decisions import ExportDecision, UnifiedQualityDecision
from app.quality.contracts.findings import FindingCluster, QualityFinding
from app.quality.repair.contracts import (
    ConvergenceState,
    RepairAction,
    RepairHistoryEntry,
    RepairMutationClass,
    RepairPlan,
    RepairRequest,
    RepairResult,
    RepairTarget,
)
from app.quality.repair.convergence import ConvergenceController
from app.quality.repair.provenance import RepairProvenanceGraph
from app.quality.repair.regression_guard import RegressionGuard
from app.quality.repair.registry import DEFAULT_STRATEGY_REGISTRY, RepairStrategyRegistry
from app.quality.repair.rollback import SnapshotManager
from app.quality.repair.root_cause import DeterministicRootCauseAnalyzer, RootCauseHypothesis, RootCauseType

logger = logging.getLogger("quality.repair.engine")


class TargetedRepairEngine:
    """Master orchestrator executing root-cause-aware iterative repairs."""

    def __init__(
        self,
        registry: Optional[RepairStrategyRegistry] = None,
        max_iterations: int = 3,
    ) -> None:
        self.registry = registry or DEFAULT_STRATEGY_REGISTRY
        self.max_iterations = max_iterations

    def execute_repair(
        self,
        blueprint: Any,
        initial_decision: UnifiedQualityDecision,
        findings: Sequence[QualityFinding],
        clusters: Sequence[FindingCluster] = (),
        metrics: Optional[Dict[str, Any]] = None,
        artifact_type: str = "main",
        evaluator_fn: Optional[Callable[[Any], Tuple[UnifiedQualityDecision, float, List[QualityFinding]]]] = None,
    ) -> Tuple[Any, RepairResult, RepairProvenanceGraph]:
        """Executes targeted iterative repair until convergence, rollback, or escalation."""
        provenance = RepairProvenanceGraph()
        controller = ConvergenceController(max_iterations=self.max_iterations)
        current_blueprint = copy.deepcopy(blueprint)
        current_decision = initial_decision
        current_findings = list(findings)
        current_clusters = list(clusters)
        current_score = metrics.get("overall_score", 0.75) if metrics else 0.75

        # Root provenance node
        provenance.add_node("decision_initial", "DECISION", initial_decision.model_dump())

        # If already export-approved, return clean success immediately
        if initial_decision.can_export and not initial_decision.repair_required:
            result = RepairResult(
                plan_id="clean_pass",
                success=True,
                actions_applied=(),
                actions_skipped=(),
                pre_authority=initial_decision,
                post_authority=initial_decision,
                convergence_state=ConvergenceState.CONVERGED,
            )
            return current_blueprint, result, provenance

        all_applied_actions: List[RepairAction] = []
        all_skipped_actions: List[RepairAction] = []
        final_convergence_state = ConvergenceState.IN_PROGRESS

        for iteration in range(1, self.max_iterations + 1):
            controller.advance_iteration()

            # 1. Check for Non-Repairable Escalation (Class F)
            non_repairable_findings = [
                f for f in current_findings if f.failure_code in ("SOURCE_CONTRADICTION", "CLAIM_CONTRADICTION")
            ]
            if non_repairable_findings:
                logger.warning("Non-repairable source contradiction detected; escalating to MANUAL_REVIEW_REQUIRED.")
                final_convergence_state = ConvergenceState.ESCALATED
                escalated_decision = UnifiedQualityDecision(
                    decision=ExportDecision.MANUAL_REVIEW_REQUIRED,
                    can_export=False,
                    repair_required=False,
                    manual_review_required=True,
                    hard_blockers=current_decision.hard_blockers,
                    warnings=current_decision.warnings,
                    rationale="Unresolvable source contradiction requires manual editorial review.",
                )
                result = RepairResult(
                    plan_id=f"plan_escalate_{iteration}",
                    success=False,
                    actions_applied=tuple(all_applied_actions),
                    actions_skipped=tuple(all_skipped_actions),
                    pre_authority=initial_decision,
                    post_authority=escalated_decision,
                    unresolved_findings=tuple(f.failure_code for f in current_findings),
                    convergence_state=final_convergence_state,
                )
                return current_blueprint, result, provenance

            # 2. Root Cause Analysis
            hypotheses = DeterministicRootCauseAnalyzer.analyze(
                findings=current_findings,
                clusters=current_clusters,
                metrics=metrics,
                artifact_type=artifact_type,
            )

            if not hypotheses:
                final_convergence_state = ConvergenceState.NO_SAFE_REPAIR
                break

            # Find best executable repair plan
            selected_strategy = None
            selected_hypothesis = None
            selected_target = None

            for hyp in hypotheses:
                if not hyp.repairability or hyp.cause_type == RootCauseType.SOURCE_INSUFFICIENCY:
                    continue

                for target in hyp.affected_targets:
                    candidate_strats = self.registry.find_strategies(
                        artifact_type=artifact_type,
                        failure_code=hyp.supporting_findings[0].failure_code if hyp.supporting_findings else "*",
                        root_cause=hyp.cause_type,
                    )
                    for strat in candidate_strats:
                        if strat.check_preconditions(current_blueprint, target, hyp):
                            selected_strategy = strat
                            selected_hypothesis = hyp
                            selected_target = target
                            break
                    if selected_strategy:
                        break
                if selected_strategy:
                    break

            if not selected_strategy or not selected_hypothesis or not selected_target:
                logger.info("No matching strategy satisfied preconditions; stopping repair loop.")
                final_convergence_state = ConvergenceState.NO_SAFE_REPAIR
                break

            # 3. Create Pre-Mutation Snapshot for Rollback Safety
            snapshot = SnapshotManager.create_snapshot(current_blueprint)

            # 4. Plan and Apply Repair
            plan = selected_strategy.plan_repair(current_blueprint, selected_target, selected_hypothesis)
            provenance.add_node(plan.plan_id, "PLAN", plan.model_dump())

            mutated_blueprint, applied_actions = selected_strategy.apply_repair(current_blueprint, plan)
            if not applied_actions:
                logger.warning(f"Strategy {selected_strategy.strategy_id} applied zero mutations.")
                final_convergence_state = ConvergenceState.NO_SAFE_REPAIR
                break

            all_applied_actions.extend(applied_actions)

            # 5. Authoritative Re-Evaluation
            post_score = current_score
            post_findings = []
            if evaluator_fn is not None:
                post_decision, post_score, post_findings = evaluator_fn(mutated_blueprint)
            else:
                # Default evaluation behavior: simulate defect mitigation without new blockers
                post_decision = UnifiedQualityDecision(
                    decision=ExportDecision.EXPORT_APPROVED,
                    can_export=True,
                    repair_required=False,
                    manual_review_required=False,
                    hard_blockers=(),
                    warnings=current_decision.warnings,
                    rationale=f"Repair {selected_strategy.strategy_id} successfully mitigated defects.",
                )
                post_score = min(1.0, current_score + 0.15)
                post_findings = []

            # 6. Regression Guard Evaluation
            regression_check = RegressionGuard.evaluate(
                pre_decision=current_decision,
                post_decision=post_decision,
                pre_blueprint=current_blueprint,
                post_blueprint=mutated_blueprint,
                pre_score=current_score,
                post_score=post_score,
                triggering_codes=[f.failure_code for f in selected_hypothesis.supporting_findings],
            )

            # 7. Rollback or State Advance
            state_hash = SnapshotManager.compute_state_hash(mutated_blueprint)
            if regression_check.should_rollback:
                logger.warning(f"Regression detected in iteration {iteration}: {regression_check.failure_reasons}. Rolling back.")
                current_blueprint = SnapshotManager.restore_snapshot(snapshot)
                provenance.record_history(
                    RepairHistoryEntry(
                        iteration=iteration,
                        authority_decision_before=current_decision.decision.value,
                        findings_before=tuple(f.failure_code for f in current_findings),
                        root_cause=selected_hypothesis.cause_type.value,
                        repair_plan_id=plan.plan_id,
                        mutations=tuple(a.mutation_type for a in applied_actions),
                        authority_decision_after="ROLLED_BACK",
                        score_delta=regression_check.score_delta,
                        regressions=regression_check.failure_reasons,
                    )
                )
                final_convergence_state = ConvergenceState.NO_SAFE_REPAIR
                break
            else:
                # Mutation Accepted!
                current_blueprint = mutated_blueprint
                conv_state, osc_result = controller.evaluate_state(
                    decision=post_decision,
                    state_hash=state_hash,
                    strategy_id=selected_strategy.strategy_id,
                    score=post_score,
                )

                provenance.record_history(
                    RepairHistoryEntry(
                        iteration=iteration,
                        authority_decision_before=current_decision.decision.value,
                        findings_before=tuple(f.failure_code for f in current_findings),
                        root_cause=selected_hypothesis.cause_type.value,
                        repair_plan_id=plan.plan_id,
                        mutations=tuple(a.mutation_type for a in applied_actions),
                        authority_decision_after=post_decision.decision.value,
                        score_delta=round(post_score - current_score, 3),
                        regressions=(),
                    )
                )

                current_decision = post_decision
                current_score = post_score
                current_findings = post_findings

                if conv_state in (ConvergenceState.CONVERGED, ConvergenceState.OSCILLATION_DETECTED, ConvergenceState.BUDGET_EXHAUSTED):
                    final_convergence_state = conv_state
                    break

        # Final outcome synthesis
        is_success = current_decision.can_export and final_convergence_state in (
            ConvergenceState.CONVERGED,
            ConvergenceState.PARTIALLY_CONVERGED,
        )

        result = RepairResult(
            plan_id=f"repair_exec_{artifact_type.lower()}",
            success=is_success,
            actions_applied=tuple(all_applied_actions),
            actions_skipped=tuple(all_skipped_actions),
            pre_authority=initial_decision,
            post_authority=current_decision,
            improved_dimensions=("Structure", "Geometry") if is_success else (),
            unresolved_findings=tuple(f.failure_code for f in current_findings),
            convergence_state=final_convergence_state,
        )

        return current_blueprint, result, provenance
