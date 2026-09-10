"""
Universal Document Intelligence System V5 — Certification Decision Explainability.

Phase 5: Produces explicit, human-readable causal explanations for every benchmark decision.
Replaces black-box scores with step-by-step decision path traces and actionable recommendations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.benchmarking.golden_contracts import BenchmarkEvaluation, CertificationDecision


class CertificationExplanation(BaseModel):
    """Causal, auditable explanation detailing why a benchmark certification decision was reached."""
    model_config = ConfigDict(frozen=True)

    evaluation_id: str
    artifact_id: str
    decision: CertificationDecision
    decision_path: str
    triggering_dimensions: List[str] = Field(default_factory=list)
    hard_invariants_status: Dict[str, bool] = Field(default_factory=dict)
    baseline_comparison: Dict[str, Any] = Field(default_factory=dict)
    regression_evidence: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    uncertainties: List[str] = Field(default_factory=list)
    recommended_action: str = ""
    human_readable_summary: str = ""


class CertificationExplainer:
    """Generates traceable, transparent explanations for BenchmarkEvaluation records."""

    @classmethod
    def explain(cls, evaluation: BenchmarkEvaluation) -> CertificationExplanation:
        dec = evaluation.certification_decision
        invs = evaluation.hard_invariant_results
        reg = evaluation.regression_analysis
        dims = evaluation.dimension_results

        triggering_dims: List[str] = []
        uncertainties: List[str] = []
        path_steps: List[str] = []

        # 1. Inspect Hard Invariants
        failed_invs = [k for k, v in invs.items() if not v]
        if failed_invs:
            path_steps.append(f"Hard invariant check failed: {failed_invs}")
            triggering_dims.extend(failed_invs)

        # 2. Inspect Regression
        is_reg = reg.get("is_regression", False)
        reg_details = reg.get("details", {})
        if is_reg:
            path_steps.append(f"Material regression detected in: {list(reg_details.keys())}")
            triggering_dims.extend(list(reg_details.keys()))

        # 3. Inspect Dimension Thresholds
        dim_scores = {d: res.normalized_score for d, res in dims.items() if res.applicability > 0.0}
        min_dim = min(dim_scores.values()) if dim_scores else 1.0
        avg_dim = sum(dim_scores.values()) / len(dim_scores) if dim_scores else 1.0

        for d, s in dim_scores.items():
            if s < 0.50:
                path_steps.append(f"Critical dimension collapse in '{d}' (score={s:.3f} < 0.50)")
                if d not in triggering_dims:
                    triggering_dims.append(d)
            elif s < 0.70:
                path_steps.append(f"Sub-optimal score in '{d}' (score={s:.3f} < 0.70)")

        # 4. Formulate Actionable Synthesis & Causal Narrative
        if dec == CertificationDecision.BENCHMARK_INSUFFICIENT:
            why = "WHY_INSUFFICIENT"
            summary = (
                f"Certification blocked: One or more non-negotiable hard invariants were violated: {failed_invs}. "
                "The artifact fails foundational integrity requirements regardless of numerical scores."
            )
            action = f"Resolve invariant failures ({failed_invs}) immediately before rerunning certification."

        elif dec == CertificationDecision.BENCHMARK_REGRESSION:
            why = "WHY_REGRESSION"
            drops_summary = ", ".join(f"{d} (drop=-{info.get('drop', 0):.3f})" for d, info in reg_details.items())
            summary = (
                f"Certification failed: Significant regression detected compared to historical baseline in {drops_summary}. "
                "Quality drop exceeds noise threshold (0.05) with high confidence."
            )
            action = f"Investigate recent generator/repair mutations affecting {list(reg_details.keys())}."

        elif dec == CertificationDecision.MANUAL_BENCHMARK_REVIEW_REQUIRED:
            why = "WHY_MANUAL_REVIEW"
            summary = (
                f"Manual review required: One or more critical dimensions dropped below minimum acceptable threshold (0.50): {triggering_dims}. "
                f"Average alignment is {avg_dim:.3f}, but minimum dimension score is {min_dim:.3f}."
            )
            action = f"Submit artifact and quality diagnostics to Phase 6 Review Studio for expert human assessment."

        elif dec == CertificationDecision.CERTIFIED_WITH_WARNINGS:
            why = "WHY_WARNING"
            summary = (
                f"Certified with warnings: Overall alignment is acceptable ({avg_dim:.3f}), but minor dimension weaknesses "
                f"or soft threshold variances were noted in {triggering_dims or 'secondary indicators'}."
            )
            action = "Artifact may proceed, but track identified warning dimensions across subsequent releases."

        elif dec == CertificationDecision.CERTIFIED_EXCELLENT:
            why = "WHY_CERTIFIED"
            summary = (
                f"Certified excellent: All evaluated dimensions exceed excellence threshold (avg={avg_dim:.3f} >= 0.90, "
                f"min={min_dim:.3f} >= 0.70), with zero hard invariant violations and zero regressions."
            )
            action = "Candidate artifact meets gold-standard requirements. Ready for baseline consideration."

        else:  # CERTIFIED_ACCEPTABLE
            why = "WHY_CERTIFIED"
            summary = (
                f"Certified acceptable: Artifact meets standard operational benchmarks (avg={avg_dim:.3f} >= 0.70) "
                "with zero hard invariant violations and zero regressions."
            )
            action = "Standard certified performance achieved."

        decision_path_str = f"{why} -> " + " -> ".join(path_steps or ["All criteria satisfied"])

        return CertificationExplanation(
            evaluation_id=evaluation.evaluation_id,
            artifact_id=evaluation.artifact_id,
            decision=dec,
            decision_path=decision_path_str,
            triggering_dimensions=triggering_dims,
            hard_invariants_status=invs,
            baseline_comparison=reg_details,
            regression_evidence=str(reg_details) if is_reg else "No regression detected",
            confidence=round(min(res.confidence for res in dims.values()) if dims else 1.0, 3),
            uncertainties=uncertainties,
            recommended_action=action,
            human_readable_summary=summary,
        )
