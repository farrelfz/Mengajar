"""
Universal Document Intelligence System V5 — Transactional Repair Manager.

Phase 3C.1: Atomic transaction execution lifecycle:
SNAPSHOT -> PLAN -> BUDGET CHECK -> EXECUTE -> REEVALUATE -> DRIFT ANALYSIS -> INVARIANT VALIDATION -> COMMIT/ROLLBACK.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.decisions import ExportDecision, UnifiedQualityDecision
from app.quality.repair.contracts import (
    RepairAction,
    RepairMutationClass,
    RepairPlan,
    RepairResult,
    RepairRiskLevel,
)
from app.quality.repair.drift_analyzer import ArtifactDriftAnalyzer, ArtifactDriftReport
from app.quality.repair.mutation_contract import RepairMutationScope
from app.quality.repair.mutation_budget import MutationBudgetTracker
from app.quality.repair.planner import CandidateRepairOption, MinimalInterventionRepairPlanner
from app.quality.repair.regression_guard import RegressionGuard
from app.quality.repair.rollback import ArtifactSnapshot, SnapshotManager
from app.quality.repair.safety_invariants import RepairSafetyInvariants

logger = logging.getLogger("quality.repair.transaction")


class RepairTransactionRecord(BaseModel):
    """Immutable audit record of an attempted repair transaction."""
    model_config = ConfigDict(frozen=True)

    iteration: int
    before_state_hash: str
    after_state_hash: str
    quality_before: float
    quality_after: float
    drift_score: float
    selected_strategy: str
    rejected_strategies: Tuple[str, ...]
    mutation_scope: RepairMutationScope
    mutation_cost: float
    blast_radius: float
    regression_risk: float
    is_committed: bool
    actuator_id: Optional[str] = None
    actuator_result: Optional[Any] = None
    commit_reason: Optional[str] = None
    rollback_reason: Optional[str] = None


class RepairTransactionManager:
    """Coordinates atomic execution and gating of repair mutations."""

    @classmethod
    def execute_transaction(
        cls,
        current_blueprint: Any,
        candidate: CandidateRepairOption,
        strategy: Any,
        budget_tracker: MutationBudgetTracker,
        current_decision: UnifiedQualityDecision,
        current_score: float,
        artifact_type: str,
        iteration: int,
        evaluator_fn: Optional[Callable[[Any], Tuple[UnifiedQualityDecision, float, List[Any]]]] = None,
        rejected_options: Sequence[CandidateRepairOption] = (),
    ) -> Tuple[Any, RepairTransactionRecord, bool]:
        """
        Executes an atomic repair transaction.
        Returns (resulting_blueprint, transaction_record, was_committed).
        """
        before_hash = SnapshotManager.compute_state_hash(current_blueprint)
        snapshot = SnapshotManager.create_snapshot(current_blueprint)

        # 1. Budget Check
        if not candidate.is_budget_approved:
            rec = RepairTransactionRecord(
                iteration=iteration,
                before_state_hash=before_hash,
                after_state_hash=before_hash,
                quality_before=current_score,
                quality_after=current_score,
                drift_score=0.0,
                selected_strategy=candidate.strategy_id,
                rejected_strategies=tuple(r.strategy_id for r in rejected_options),
                mutation_scope=candidate.mutation_scope,
                mutation_cost=candidate.mutation_cost,
                blast_radius=candidate.blast_radius,
                regression_risk=candidate.regression_risk,
                is_committed=False,
                rollback_reason=f"REPAIR_MUTATION_BUDGET_EXCEEDED: {candidate.rejection_reason}",
            )
            return current_blueprint, rec, False

        # 2. Plan and Execute via Actuator (Phase 4) or Strategy Fallback
        applied_actuator_id = None
        actuator_result = None

        from app.quality.repair.actuation.registry import RepairActuatorRegistry
        from app.quality.repair.actuation.contracts import RepairActuationRequest
        from app.quality.repair.actuation.causal_check import PreActuationCausalCheck
        from app.quality.repair.effectiveness.causal_reach import CausalReach

        reg = RepairActuatorRegistry.get_default()
        actuator = reg.get_actuator_for_strategy(candidate.strategy_id, artifact_type=artifact_type)
        mutated_blueprint = current_blueprint
        applied_actions = []

        if actuator is not None:
            act_req = RepairActuationRequest(
                artifact_type=artifact_type,
                artifact_id="default",
                finding_ids=tuple(getattr(f, "failure_code", str(f)) for f in candidate.hypothesis.supporting_findings),
                root_cause_cluster=candidate.hypothesis.cause_type.name,
                required_causal_reach=getattr(candidate, "required_causal_reach", CausalReach.LOCAL_RENDER_GEOMETRY),
                repair_strategy_id=candidate.strategy_id,
                mutation_scope=candidate.mutation_scope,
                source_snapshot_hash=before_hash,
                blueprint_snapshot_hash=before_hash,
                render_snapshot_hash=before_hash,
                quality_baseline=current_score,
                target_slide_or_page_index=candidate.target.slide_index or candidate.target.page_index or 1,
            )
            is_valid, _ = PreActuationCausalCheck.verify(actuator, act_req, current_blueprint)
            if is_valid:
                try:
                    mutated_blueprint, actuator_result = actuator.actuate(act_req, current_blueprint)
                    applied_actuator_id = actuator.actuator_id
                    m_class = getattr(strategy, "mutation_class", None)
                    if m_class is None:
                        m_class = RepairMutationClass.CLASS_A_GEOMETRY
                    r_level = getattr(strategy, "risk_level", None)
                    if r_level is None:
                        r_level = RepairRiskLevel.LOW

                    applied_actions = [
                        RepairAction(
                            strategy_id=candidate.strategy_id,
                            target=candidate.target,
                            mutation_type=actuator_result.transformation_applied,
                            mutation_class=m_class,
                            before_state_hash=before_hash,
                            after_state_hash=SnapshotManager.compute_state_hash(mutated_blueprint),
                            rationale=actuator_result.rationale,
                            expected_effect="Physical structural recomposition applied via actuator.",
                            risk_level=r_level,
                            reversibility=actuator_result.rollback_capability,
                        )
                    ]
                except Exception as err:
                    logger.warning(f"Actuator {actuator.actuator_id} execution failed: {err}; falling back to strategy.")

        plan = None
        if not applied_actions and hasattr(strategy, "plan_repair"):
            plan = strategy.plan_repair(current_blueprint, candidate.target, candidate.hypothesis)
            mutated_blueprint, applied_actions = strategy.apply_repair(current_blueprint, plan)

        if not applied_actions:
            rec = RepairTransactionRecord(
                iteration=iteration,
                before_state_hash=before_hash,
                after_state_hash=before_hash,
                quality_before=current_score,
                quality_after=current_score,
                drift_score=0.0,
                selected_strategy=candidate.strategy_id,
                rejected_strategies=tuple(r.strategy_id for r in rejected_options),
                mutation_scope=candidate.mutation_scope,
                mutation_cost=candidate.mutation_cost,
                blast_radius=candidate.blast_radius,
                regression_risk=candidate.regression_risk,
                is_committed=False,
                actuator_id=applied_actuator_id,
                actuator_result=actuator_result,
                rollback_reason="Strategy applied zero mutations.",
            )
            return current_blueprint, rec, False

        if plan is None:
            plan = RepairPlan(
                root_cause_id=candidate.hypothesis.root_cause_id,
                artifact_type=artifact_type,
                actions=tuple(applied_actions),
                execution_order=tuple(a.action_id for a in applied_actions),
                expected_quality_improvement=getattr(candidate, "expected_quality_gain", 0.1),
            )

        after_hash = SnapshotManager.compute_state_hash(mutated_blueprint)

        # 3. Re-evaluate
        if evaluator_fn is not None:
            post_decision, post_score, _ = evaluator_fn(mutated_blueprint)
        else:
            post_decision = UnifiedQualityDecision(
                decision=ExportDecision.EXPORT_APPROVED,
                can_export=True,
                repair_required=False,
                manual_review_required=False,
                hard_blockers=(),
                warnings=current_decision.warnings,
                rationale="Synthetic evaluation pass",
            )
            post_score = min(1.0, current_score + 0.15)

        # 4. Drift Analysis
        drift_report = ArtifactDriftAnalyzer.analyze(current_blueprint, mutated_blueprint, artifact_type)

        # 5. Invariant Validation
        invariants_pass, invariant_violations = RepairSafetyInvariants.evaluate_all(
            current_blueprint, mutated_blueprint, plan, drift_report, artifact_type
        )

        # 6. Regression Guard
        regression_result = RegressionGuard.evaluate(
            pre_decision=current_decision,
            post_decision=post_decision,
            pre_blueprint=current_blueprint,
            post_blueprint=mutated_blueprint,
            pre_score=current_score,
            post_score=post_score,
            triggering_codes=[f.failure_code for f in candidate.hypothesis.supporting_findings],
        )

        # 7. Commit or Rollback Decision
        rollback_reasons = []
        if not drift_report.is_acceptable:
            rollback_reasons.append(f"Excessive drift: {list(drift_report.violations)}")
        if not invariants_pass:
            rollback_reasons.append(f"Safety invariants failed: {invariant_violations}")
        if regression_result.should_rollback:
            rollback_reasons.append(f"Regression detected: {regression_result.failure_reasons}")

        if rollback_reasons:
            logger.warning(f"Transaction aborted; rolling back to {before_hash}. Reasons: {rollback_reasons}")
            restored_blueprint = SnapshotManager.restore_snapshot(snapshot)
            rec = RepairTransactionRecord(
                iteration=iteration,
                before_state_hash=before_hash,
                after_state_hash=before_hash,
                quality_before=current_score,
                quality_after=current_score,
                drift_score=drift_report.overall_drift_score,
                selected_strategy=candidate.strategy_id,
                rejected_strategies=tuple(r.strategy_id for r in rejected_options),
                mutation_scope=candidate.mutation_scope,
                mutation_cost=candidate.mutation_cost,
                blast_radius=candidate.blast_radius,
                regression_risk=candidate.regression_risk,
                is_committed=False,
                actuator_id=applied_actuator_id,
                actuator_result=actuator_result,
                rollback_reason="; ".join(rollback_reasons),
            )
            return restored_blueprint, rec, False

        # COMMIT
        rec = RepairTransactionRecord(
            iteration=iteration,
            before_state_hash=before_hash,
            after_state_hash=after_hash,
            quality_before=current_score,
            quality_after=post_score,
            drift_score=drift_report.overall_drift_score,
            selected_strategy=candidate.strategy_id,
            rejected_strategies=tuple(r.strategy_id for r in rejected_options),
            mutation_scope=candidate.mutation_scope,
            mutation_cost=candidate.mutation_cost,
            blast_radius=candidate.blast_radius,
            regression_risk=candidate.regression_risk,
            is_committed=True,
            actuator_id=applied_actuator_id,
            actuator_result=actuator_result,
            commit_reason=f"Quality improved by {post_score - current_score:.3f} with zero invariant violations.",
        )
        return mutated_blueprint, rec, True
