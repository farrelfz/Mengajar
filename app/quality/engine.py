"""
Master Quality Evaluation Engine & Quality Gate Arbiter.

Orchestrates multi-dimensional evaluation across semantic, pedagogical,
structural, density, redundancy, format, and physical rendering dimensions.
Computes weighted composite scores and produces actionable diagnostic traces.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.blueprints.contracts import SemanticMaterialBlueprint
from app.composition.schemas import DocumentComposition
from app.director.contracts import LearningJourney
from app.quality.contracts import (
    EvaluationStage,
    EvaluationTrace,
    QualityDimension,
    QualityFinding,
    QualityGateDecision,
    QualityGateResult,
    QualityLevel,
    QualityMetric,
    QualityReport,
    QualityScore,
    QualitySeverity,
)
from app.quality.density_evaluator import DensityEvaluator
from app.quality.format_evaluator import FormatEvaluator
from app.quality.pedagogical_evaluator import PedagogicalEvaluator
from app.quality.redundancy_evaluator import RedundancyEvaluator
from app.quality.semantic_evaluator import SemanticEvaluator
from app.quality.structural_evaluator import StructuralEvaluator


class QualityEvaluationEngine:
    """Master orchestrator for multi-dimensional material quality evaluation."""

    DIMENSION_WEIGHTS: dict[QualityDimension, float] = {
        QualityDimension.SEMANTIC_CORRECTNESS: 1.5,
        QualityDimension.PEDAGOGICAL_ALIGNMENT: 1.5,
        QualityDimension.STRUCTURAL_COHERENCE: 1.3,
        QualityDimension.INFORMATION_DENSITY: 1.2,
        QualityDimension.FORMAT_INTEGRITY: 1.4,
        QualityDimension.REDUNDANCY: 1.0,
        QualityDimension.VISUAL_APPROPRIATENESS: 1.0,
        QualityDimension.LEARNER_ALIGNMENT: 1.0,
        QualityDimension.ACCESSIBILITY: 0.8,
    }

    @classmethod
    def evaluate_artifact(
        cls,
        job_id: str,
        material_bp: SemanticMaterialBlueprint | None = None,
        blueprint: SemanticMaterialBlueprint | None = None,
        journey: LearningJourney | None = None,
        composition: DocumentComposition | None = None,
        pdf_path: str | Path | None = None,
        target_format: str = "a4_portrait",
    ) -> QualityReport:
        effective_bp = material_bp or blueprint

        all_metrics: list[QualityMetric] = []
        all_findings: list[QualityFinding] = []
        evaluator_traces: list[dict[str, Any]] = []

        # 1. Structural Coherence Evaluation
        struct_metrics, struct_findings = StructuralEvaluator.evaluate(blueprint=effective_bp, composition=composition)
        all_metrics.extend(struct_metrics)
        all_findings.extend(struct_findings)
        evaluator_traces.append({"evaluator": "StructuralEvaluator", "metrics_count": len(struct_metrics), "findings_count": len(struct_findings)})

        # 2. Semantic Evaluation
        sem_metrics, sem_findings = SemanticEvaluator.evaluate(effective_bp)
        all_metrics.extend(sem_metrics)
        all_findings.extend(sem_findings)
        evaluator_traces.append({"evaluator": "SemanticEvaluator", "metrics_count": len(sem_metrics), "findings_count": len(sem_findings)})

        # 3. Pedagogical Evaluation
        ped_metrics, ped_findings = PedagogicalEvaluator.evaluate(journey, effective_bp)
        all_metrics.extend(ped_metrics)
        all_findings.extend(ped_findings)
        evaluator_traces.append({"evaluator": "PedagogicalEvaluator", "metrics_count": len(ped_metrics), "findings_count": len(ped_findings)})

        # 4. Density Evaluation
        dens_metrics, dens_findings = DensityEvaluator.evaluate(composition, target_format=target_format)
        all_metrics.extend(dens_metrics)
        all_findings.extend(dens_findings)
        evaluator_traces.append({"evaluator": "DensityEvaluator", "metrics_count": len(dens_metrics), "findings_count": len(dens_findings)})

        # 5. Redundancy Evaluation
        red_metrics, red_findings = RedundancyEvaluator.evaluate(composition)
        all_metrics.extend(red_metrics)
        all_findings.extend(red_findings)
        evaluator_traces.append({"evaluator": "RedundancyEvaluator", "metrics_count": len(red_metrics), "findings_count": len(red_findings)})

        # 6. Physical Format & Geometry Evaluation
        expected_pages = len(composition.pages) if composition and composition.pages else None
        fmt_metrics, fmt_findings = FormatEvaluator.evaluate(pdf_path, target_format=target_format, expected_page_count=expected_pages)
        all_metrics.extend(fmt_metrics)
        all_findings.extend(fmt_findings)
        evaluator_traces.append({"evaluator": "FormatEvaluator", "metrics_count": len(fmt_metrics), "findings_count": len(fmt_findings)})

        # Compute dimensional and composite scores
        score = cls._compute_quality_score(all_metrics)

        # Arbitrate Quality Gate Decision
        gate_result = cls._arbitrate_quality_gate(score, all_findings)

        # Build EvaluationTrace
        trace = EvaluationTrace(
            evaluator_traces=evaluator_traces,
            stage_evaluations={
                "blueprint": effective_bp is not None,
                "composition": composition is not None,
                "artifact": pdf_path is not None,
            },
            score_computation_log=[
                f"Overall Score: {score.overall_score:.3f}",
                f"Quality Level: {score.quality_level.value}",
                f"Gate Decision: {gate_result.decision.value}",
            ],
        )

        return QualityReport(
            job_id=job_id,
            overall_score=score.overall_score,
            quality_level=score.quality_level,
            gate_result=gate_result,
            findings=all_findings,
            metrics=all_metrics,
            trace=trace,
            metadata={"target_format": target_format, "pdf_path": str(pdf_path) if pdf_path else None},
        )

    @classmethod
    def _compute_quality_score(cls, metrics: list[QualityMetric]) -> QualityScore:
        if not metrics:
            return QualityScore(overall_score=1.0, quality_level=QualityLevel.EXCELLENT, dimensional_scores={}, is_passing=True)

        dim_scores: dict[str, list[tuple[float, float]]] = {}
        for m in metrics:
            dim_key = m.dimension.value
            if dim_key not in dim_scores:
                dim_scores[dim_key] = []
            dim_scores[dim_key].append((m.score, m.weight))

        dimensional_scores: dict[str, float] = {}
        weighted_sum = 0.0
        total_dimension_weight = 0.0

        for dim_key, score_weight_pairs in dim_scores.items():
            dim_metric_weighted = sum(s * w for s, w in score_weight_pairs)
            dim_metric_total_w = sum(w for _, w in score_weight_pairs)
            dim_avg = dim_metric_weighted / max(1e-6, dim_metric_total_w)
            dimensional_scores[dim_key] = round(dim_avg, 3)

            dim_enum = QualityDimension(dim_key)
            dim_weight = cls.DIMENSION_WEIGHTS.get(dim_enum, 1.0)
            weighted_sum += dim_avg * dim_weight
            total_dimension_weight += dim_weight

        overall = weighted_sum / max(1e-6, total_dimension_weight)
        overall_rounded = round(min(1.0, max(0.0, overall)), 3)

        # Derive QualityLevel
        if overall_rounded >= 0.95:
            q_level = QualityLevel.EXCELLENT
        elif overall_rounded >= 0.85:
            q_level = QualityLevel.GOOD
        elif overall_rounded >= 0.75:
            q_level = QualityLevel.ACCEPTABLE
        elif overall_rounded >= 0.60:
            q_level = QualityLevel.NEEDS_IMPROVEMENT
        elif overall_rounded >= 0.40:
            q_level = QualityLevel.POOR
        else:
            q_level = QualityLevel.CRITICAL

        return QualityScore(
            overall_score=overall_rounded,
            dimensional_scores=dimensional_scores,
            quality_level=q_level,
            is_passing=overall_rounded >= 0.75,
        )

    @classmethod
    def _arbitrate_quality_gate(
        cls,
        score: QualityScore,
        findings: list[QualityFinding],
    ) -> QualityGateResult:
        critical_findings = [f for f in findings if f.severity == QualitySeverity.CRITICAL]
        error_findings = [f for f in findings if f.severity == QualitySeverity.ERROR]
        warning_findings = [f for f in findings if f.severity == QualitySeverity.WARNING]

        if critical_findings:
            decision = QualityGateDecision.FAIL
            can_proceed = False
            reasoning = f"Critical invariant violation: {critical_findings[0].finding}"
        elif error_findings or score.overall_score < 0.70:
            decision = QualityGateDecision.NEEDS_REFINEMENT
            can_proceed = False
            reasoning = f"Quality score ({score.overall_score:.2f}) or structural errors require refinement pass."
        elif warning_findings or score.overall_score < 0.85:
            decision = QualityGateDecision.PASS_WITH_WARNINGS
            can_proceed = True
            reasoning = f"Artifact meets acceptable standard ({score.overall_score:.2f}) with {len(warning_findings)} non-blocking warnings."
        else:
            decision = QualityGateDecision.PASS
            can_proceed = True
            reasoning = f"Artifact passed all quality dimensions with score {score.overall_score:.2f}."

        return QualityGateResult(
            decision=decision,
            score=score,
            critical_findings=critical_findings,
            warnings=warning_findings,
            can_proceed=can_proceed,
            gate_reasoning=reasoning,
        )
