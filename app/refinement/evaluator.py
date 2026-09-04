"""
Refinement Evaluator & Improvement Comparator: Evaluates candidate artifacts and calculates finding/score deltas.
"""

from __future__ import annotations

from app.critic.engine import GenerativeCriticEngine
from app.quality.engine import QualityEvaluationEngine
from app.refinement.contracts import (
    ImprovementComparison,
    RefinedArtifactBundle,
    RefinementCandidate,
)
from app.refinement.invariants import InvariantChecker


class RefinementEvaluator:
    """Evaluates candidates using Quality Evaluation and Generative Critic."""

    def __init__(self) -> None:
        self.critic_engine = GenerativeCriticEngine()

    def evaluate_candidate(self, candidate: RefinementCandidate) -> RefinementCandidate:
        bundle = candidate.artifact_bundle
        q_rep = QualityEvaluationEngine.evaluate_artifact(
            job_id=candidate.candidate_id,
            material_bp=bundle.blueprint,
            journey=bundle.journey,
            composition=bundle.composition,
            pdf_path=bundle.pdf_path,
            target_format=bundle.target_format,
        )
        c_rep = self.critic_engine.critique(
            artifact_id=candidate.candidate_id,
            blueprint=bundle.blueprint,
            composition=bundle.composition,
            journey=bundle.journey,
            quality_report=q_rep,
            pdf_path=bundle.pdf_path,
            target_format=bundle.target_format,
        )
        candidate.quality_report = q_rep
        candidate.critique_report = c_rep
        return candidate


class ImprovementComparator:
    """Compares baseline vs candidate diagnostic states."""

    @classmethod
    def compare(
        cls,
        baseline_bundle: RefinedArtifactBundle,
        baseline_candidate: RefinementCandidate,
        new_candidate: RefinementCandidate,
    ) -> ImprovementComparison:
        base_score = baseline_candidate.quality_report.overall_score if baseline_candidate.quality_report else 0.0
        new_score = new_candidate.quality_report.overall_score if new_candidate.quality_report else 0.0
        score_delta = round(new_score - base_score, 3)

        base_f_ids = {f.id for f in (baseline_candidate.critique_report.findings if baseline_candidate.critique_report else [])}
        new_f_ids = {f.id for f in (new_candidate.critique_report.findings if new_candidate.critique_report else [])}

        resolved = list(base_f_ids - new_f_ids)
        persisting = list(base_f_ids & new_f_ids)
        regressions = list(new_f_ids - base_f_ids)

        # Check Invariants
        violations = InvariantChecker.check_invariants(baseline_bundle, new_candidate.artifact_bundle)

        is_improvement = (score_delta > 0.0 or len(resolved) > 0) and len(regressions) == 0 and len(violations) == 0

        return ImprovementComparison(
            iteration=new_candidate.iteration,
            baseline_quality_score=base_score,
            candidate_quality_score=new_score,
            quality_delta=score_delta,
            baseline_findings_count=len(base_f_ids),
            candidate_findings_count=len(new_f_ids),
            resolved_finding_ids=resolved,
            persisting_finding_ids=persisting,
            new_regressions=regressions,
            invariant_violations=violations,
            is_meaningful_improvement=is_improvement,
            reasoning=f"Score delta: {score_delta:+.3f}, {len(resolved)} resolved, {len(regressions)} regressions, {len(violations)} invariant violations.",
        )
