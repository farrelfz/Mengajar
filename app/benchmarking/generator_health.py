"""
Universal Document Intelligence System V5 — Longitudinal Generator Health Model.

Phase 5: Aggregates historical benchmark runs to monitor the longitudinal health of the generator.
Identifies systemic trends, cross-artifact divergence health, and persistent regression clusters.
Does NOT influence production export decisions.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.benchmarking.golden_contracts import BenchmarkEvaluation, CertificationDecision


class GeneratorStatus(str, Enum):
    """Longitudinal stability and progression status of the generation system."""
    GENERATOR_IMPROVING = "GENERATOR_IMPROVING"        # Increasing alignment scores, 0 regressions
    GENERATOR_HEALTHY = "GENERATOR_HEALTHY"            # Stable high performance, 0 regressions
    GENERATOR_STABLE = "GENERATOR_STABLE"              # Scores remain consistent within noise boundaries
    GENERATOR_REGRESSING = "GENERATOR_REGRESSING"      # Persistent regression across evaluations (>15%)
    GENERALIZATION_RISK = "GENERALIZATION_RISK"        # High gap between known and novel inputs
    REQUIRES_INVESTIGATION = "REQUIRES_INVESTIGATION"  # Invariant failures or severe dimension collapse


class GeneratorHealthReport(BaseModel):
    """Holistic diagnostic health summary across historical benchmark runs."""
    model_config = ConfigDict(frozen=True)

    generator_version: str
    overall_status: GeneratorStatus
    total_evaluations: int
    regression_frequency: float = Field(ge=0.0, le=1.0)
    invariant_failure_rate: float = Field(ge=0.0, le=1.0)
    per_artifact_health: Dict[str, GeneratorStatus] = Field(default_factory=dict)
    per_dimension_trends: Dict[str, str] = Field(default_factory=dict)
    cross_artifact_divergence_health: str = "SUFFICIENT"
    generalization_risk_flag: bool = False
    summary: str = ""


class GeneratorHealthTracker:
    """Evaluates longitudinal health based on a collection of BenchmarkEvaluations."""

    @classmethod
    def evaluate_health(
        cls,
        evaluations: List[BenchmarkEvaluation],
        generator_version: str = "v5.0.0",
        divergence_pass: bool = True,
        generalization_gap: float = 0.02,
    ) -> GeneratorHealthReport:
        """
        Synthesizes historical evaluations into an actionable generator health assessment.
        """
        if not evaluations:
            return GeneratorHealthReport(
                generator_version=generator_version,
                overall_status=GeneratorStatus.GENERATOR_STABLE,
                total_evaluations=0,
                regression_frequency=0.0,
                invariant_failure_rate=0.0,
                summary="No evaluations recorded yet.",
            )

        n = len(evaluations)
        regressions = sum(1 for e in evaluations if e.certification_decision == CertificationDecision.BENCHMARK_REGRESSION)
        invariants_failed = sum(1 for e in evaluations if e.certification_decision == CertificationDecision.BENCHMARK_INSUFFICIENT)

        reg_freq = round(regressions / n, 3)
        inv_rate = round(invariants_failed / n, 3)

        # Per-artifact breakdown
        by_artifact: Dict[str, List[BenchmarkEvaluation]] = {}
        for e in evaluations:
            # Extract artifact type from ID or golden ref
            atype = "GENERAL"
            for candidate in ("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"):
                if candidate in e.artifact_id.upper() or candidate in e.golden_reference_id.upper():
                    atype = candidate
                    break
            by_artifact.setdefault(atype, []).append(e)

        per_art_status: Dict[str, GeneratorStatus] = {}
        for atype, evs in by_artifact.items():
            art_regs = sum(1 for ev in evs if ev.certification_decision == CertificationDecision.BENCHMARK_REGRESSION)
            art_invs = sum(1 for ev in evs if ev.certification_decision == CertificationDecision.BENCHMARK_INSUFFICIENT)
            if art_invs > 0:
                per_art_status[atype] = GeneratorStatus.REQUIRES_INVESTIGATION
            elif art_regs > 0:
                per_art_status[atype] = GeneratorStatus.GENERATOR_REGRESSING
            else:
                avg_align = sum(ev.reference_alignment for ev in evs) / len(evs)
                per_art_status[atype] = (
                    GeneratorStatus.GENERATOR_IMPROVING if avg_align >= 0.95 else GeneratorStatus.GENERATOR_HEALTHY
                )

        # Overall Status Resolution
        if inv_rate > 0.05 or not divergence_pass:
            status = GeneratorStatus.REQUIRES_INVESTIGATION
            summary = "System requires immediate investigation: hard invariants violated or cross-artifact collapse detected."
        elif reg_freq > 0.15:
            status = GeneratorStatus.GENERATOR_REGRESSING
            summary = f"System is regressing: {reg_freq*100:.1f}% of evaluations exhibited material regressions."
        elif generalization_gap > 0.08:
            status = GeneratorStatus.GENERALIZATION_RISK
            summary = f"Generalization risk: Significant performance drop ({generalization_gap:.3f}) on novel inputs."
        elif all(s in (GeneratorStatus.GENERATOR_IMPROVING, GeneratorStatus.GENERATOR_HEALTHY) for s in per_art_status.values()):
            avg_all = sum(e.reference_alignment for e in evaluations) / n
            status = GeneratorStatus.GENERATOR_IMPROVING if avg_all >= 0.95 else GeneratorStatus.GENERATOR_HEALTHY
            summary = f"Generator is healthy and stable across all evaluated artifact types (avg alignment: {avg_all:.3f})."
        else:
            status = GeneratorStatus.GENERATOR_STABLE
            summary = "Generator is operating within normal operational variance."

        return GeneratorHealthReport(
            generator_version=generator_version,
            overall_status=status,
            total_evaluations=n,
            regression_frequency=reg_freq,
            invariant_failure_rate=inv_rate,
            per_artifact_health=per_art_status,
            cross_artifact_divergence_health="SUFFICIENT" if divergence_pass else "COLLAPSE_DETECTED",
            generalization_risk_flag=(generalization_gap > 0.08),
            summary=summary,
        )
