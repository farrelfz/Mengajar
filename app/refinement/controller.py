"""
Master Iterative Refinement Controller: Orchestrates the closed refinement loop.
"""

from __future__ import annotations

import copy
from typing import Any

from app.blueprints.contracts import SemanticMaterialBlueprint
from app.composition.schemas import DocumentComposition
from app.director.contracts import LearningJourney
from app.refinement.contracts import (
    ImprovementDecision,
    RefinedArtifactBundle,
    RefinementCandidate,
    RefinementTrace,
)
from app.refinement.convergence import ConvergenceDetector
from app.refinement.decision import ImprovementJudge
from app.refinement.evaluator import ImprovementComparator, RefinementEvaluator
from app.refinement.executor import RefinementExecutor
from app.refinement.history import RefinementHistory
from app.refinement.planner import RefinementPlanner


class IterativeRefinementController:
    """Master controller managing closed-loop multi-iteration refinement."""

    def __init__(self) -> None:
        self.planner = RefinementPlanner()
        self.executor = RefinementExecutor()
        self.evaluator = RefinementEvaluator()
        self.judge = ImprovementJudge()

    def refine(
        self,
        blueprint: SemanticMaterialBlueprint,
        composition: DocumentComposition,
        journey: LearningJourney | None = None,
        target_format: str = "a4_portrait",
        max_iterations: int = 3,
        artifact_id: str = "artifact",
    ) -> tuple[RefinedArtifactBundle, RefinementHistory]:
        initial_bundle = RefinedArtifactBundle(
            artifact_id=artifact_id,
            blueprint=copy.deepcopy(blueprint),
            composition=copy.deepcopy(composition),
            journey=copy.deepcopy(journey) if journey else None,
            target_format=target_format,
        )

        history = RefinementHistory(artifact_id=artifact_id)

        # Iteration 0: Baseline Evaluation
        base_candidate = RefinementCandidate(
            candidate_id=f"{artifact_id}_base",
            parent_artifact_id="root",
            iteration=0,
            patches=[],
            artifact_bundle=copy.deepcopy(initial_bundle),
        )
        base_candidate = self.evaluator.evaluate_candidate(base_candidate)
        base_score = base_candidate.quality_report.overall_score if base_candidate.quality_report else 1.0
        history.baseline_score = base_score
        history.final_score = base_score

        base_fingerprint = ConvergenceDetector.compute_state_fingerprint(base_candidate)
        history.fingerprints.append(base_fingerprint)

        # If baseline is already excellent (score >= 0.95 and 0 critical/high findings), finish immediately
        crit_high_findings = [
            f for f in (base_candidate.critique_report.findings if base_candidate.critique_report else [])
            if f.severity.value in ["critical", "high"]
        ]
        if base_score >= 0.95 and not crit_high_findings:
            history.final_decision = ImprovementDecision.ACCEPT
            history.stop_reason = "Baseline already satisfies excellent quality criteria."
            return initial_bundle, history

        current_bundle = initial_bundle
        current_candidate = base_candidate
        history_scores = [base_score]

        for iteration in range(1, max_iterations + 1):
            # 1. Plan
            plan = self.planner.create_plan(
                artifact_bundle=current_bundle,
                quality_report=current_candidate.quality_report,
                critique_report=current_candidate.critique_report,
                iteration=iteration,
            )

            if not plan.actions:
                history.final_decision = ImprovementDecision.STOP_CONVERGED
                history.stop_reason = "No further refinement actions required."
                break

            # 2. Execute Patches
            candidate = self.executor.execute_plan(baseline=current_bundle, plan=plan)

            # 3. Evaluate Candidate
            candidate = self.evaluator.evaluate_candidate(candidate)
            cand_score = candidate.quality_report.overall_score if candidate.quality_report else 0.0

            # 4. Compare with baseline
            comparison = ImprovementComparator.compare(
                baseline_bundle=initial_bundle,
                baseline_candidate=current_candidate,
                new_candidate=candidate,
            )

            # 5. Judge Decision
            decision = self.judge.judge(comparison)
            comparison.decision = decision

            cand_fingerprint = ConvergenceDetector.compute_state_fingerprint(candidate)

            # 6. Check Convergence / Oscillation
            conv_decision = ConvergenceDetector.check_convergence(
                history_fingerprints=history.fingerprints,
                history_scores=history_scores,
                current_fingerprint=cand_fingerprint,
                current_score=cand_score,
            )

            trace = RefinementTrace(
                iteration=iteration,
                finding_ids_addressed=[a.action_id for a in plan.actions],
                actions_planned=[a.intent.value for a in plan.actions],
                patches_applied=[p.patch_id for p in candidate.patches],
                candidate_score=cand_score,
                quality_delta=comparison.quality_delta,
                decision=conv_decision or decision,
                decision_reasoning=comparison.reasoning,
            )

            history.record_iteration(
                plan=plan,
                candidate=candidate,
                comparison=comparison,
                fingerprint=cand_fingerprint,
                trace=trace,
            )

            if conv_decision is not None:
                history.final_decision = conv_decision
                history.stop_reason = f"Refinement halted by convergence detector: {conv_decision.value}."
                if decision == ImprovementDecision.ACCEPT:
                    current_bundle = candidate.artifact_bundle
                break

            if decision == ImprovementDecision.ACCEPT:
                current_bundle = candidate.artifact_bundle
                current_candidate = candidate
                history_scores.append(cand_score)
                history.final_decision = ImprovementDecision.ACCEPT
                history.stop_reason = f"Candidate accepted at iteration {iteration}."
            elif decision == ImprovementDecision.REJECT:
                history.final_decision = ImprovementDecision.REJECT
                history.stop_reason = f"Candidate rejected at iteration {iteration} due to invariant violation or regression."
                break
            elif decision == ImprovementDecision.STOP_NO_IMPROVEMENT:
                history.final_decision = ImprovementDecision.STOP_NO_IMPROVEMENT
                history.stop_reason = "Halting refinement: no meaningful score improvement achieved."
                break

            if iteration == max_iterations:
                history.final_decision = ImprovementDecision.STOP_MAX_ITERATIONS
                history.stop_reason = f"Reached maximum allowed iterations limit ({max_iterations})."

        return current_bundle, history
