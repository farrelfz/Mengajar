"""
Universal Document Intelligence System V5 — Generalization Metrics Engine.

Phase 4.1: Calculates scientifically rigorous corpus-level metrics:
RGR (Repair Generalization Rate), RRG (Repair Regression Rate), FRR (False Repair Rate),
CRR (Causal Resolution Rate), ZER (Zero-Effect Rate), and Generalization Gap.
"""

from __future__ import annotations

import logging
import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.benchmarking.contracts import (
    BenchmarkExecutionOutcome,
    GeneralizationMetrics,
)
from app.benchmarking.taxonomy import CorpusCategory, CorpusSplit

logger = logging.getLogger("benchmarking.metrics")


class GeneralizationMetricEngine:
    """Evaluates corpus-wide generalization performance and anti-masking distribution statistics."""

    @classmethod
    def compute_metrics(
        cls,
        outcomes: Sequence[BenchmarkExecutionOutcome],
    ) -> GeneralizationMetrics:
        if not outcomes:
            return GeneralizationMetrics(
                total_jobs=0,
                known_jobs=0,
                unseen_jobs=0,
                pathological_jobs=0,
                repair_generalization_rate=0.0,
                repair_regression_rate=0.0,
                false_repair_rate=0.0,
                causal_resolution_rate=0.0,
                zero_effect_rate=0.0,
                known_corpus_mean_score=0.0,
                unseen_corpus_mean_score=0.0,
                generalization_gap=0.0,
                generalization_warning=False,
                worst_case_score=0.0,
                unseen_blocker_retention_rate=0.0,
                mean_iterations_to_convergence=0.0,
            )

        known_splits = (CorpusSplit.TRAINING_REFERENCE, CorpusSplit.VALIDATION_REFERENCE)
        known_outcomes = [o for o in outcomes if o.split in known_splits]
        unseen_outcomes = [o for o in outcomes if o.split == CorpusSplit.UNSEEN_GENERALIZATION]
        pathological_outcomes = [o for o in outcomes if o.split == CorpusSplit.ADVERSARIAL or o.corpus_category == CorpusCategory.PATHOLOGICAL]

        # 1. Score Averages & Generalization Gap
        known_scores = [o.overall_quality_score for o in known_outcomes]
        unseen_scores = [o.overall_quality_score for o in unseen_outcomes]
        all_scores = [o.overall_quality_score for o in outcomes]

        mean_known = statistics.mean(known_scores) if known_scores else 0.0
        mean_unseen = statistics.mean(unseen_scores) if unseen_scores else 0.0
        gap = mean_known - mean_unseen
        worst_case = min(all_scores) if all_scores else 0.0

        # 2. Repair Generalization Rate (RGR) on unseen fixtures
        unseen_attempts = sum(len(o.operators_attempted) for o in unseen_outcomes)
        unseen_successes = sum(len(o.operators_committed) for o in unseen_outcomes)
        rgr = unseen_successes / max(1, unseen_attempts) if unseen_attempts > 0 else 1.0

        # 3. Repair Regression Rate (RRG) across all runs
        total_committed = sum(len(o.operators_committed) for o in outcomes)
        total_regressions = sum(len(o.operators_rolled_back) for o in outcomes)
        rrg = total_regressions / max(1, (total_committed + total_regressions))

        # 4. Zero-Effect Rate (ZER)
        total_attempts = sum(len(o.operators_attempted) for o in outcomes)
        total_zero_effect = sum(len(o.zero_effect_operators) for o in outcomes)
        zer = total_zero_effect / max(1, total_attempts)

        # 5. False Repair Rate (FRR)
        # Attempted repairs on jobs that already had perfect score or 0 blockers where score did not improve
        false_attempts = 0
        for o in outcomes:
            if o.hard_blockers_count == 0 and len(o.operators_attempted) > 0 and o.overall_quality_score >= 0.99:
                false_attempts += len(o.operators_attempted)
        frr = false_attempts / max(1, total_attempts)

        # 6. Causal Resolution Rate (CRR)
        # Ratio of jobs where hard blockers were completely resolved
        jobs_with_blockers_resolved = sum(
            1 for o in outcomes if o.hard_blockers_count == 0 and len(o.operators_committed) > 0
        )
        total_jobs_requiring_repair = sum(
            1 for o in outcomes if (len(o.operators_attempted) > 0 or len(o.operators_committed) > 0)
        )
        crr = min(1.0, jobs_with_blockers_resolved / max(1, total_jobs_requiring_repair)) if total_jobs_requiring_repair > 0 else 1.0

        # 7. Unseen Blocker Retention Rate
        unseen_with_blockers = sum(1 for o in unseen_outcomes if o.hard_blockers_count > 0)
        unseen_blocker_retention = unseen_with_blockers / max(1, len(unseen_outcomes))

        # 8. Mean Iterations
        mean_iters = statistics.mean(o.total_iterations for o in outcomes) if outcomes else 0.0

        # 9. Generalization Warning trigger
        # Warning if gap > 0.08 or any unseen job has retained hard blockers or worst case < 0.75
        gen_warning = bool(gap > 0.08 or unseen_blocker_retention > 0.0 or worst_case < 0.75)

        return GeneralizationMetrics(
            total_jobs=len(outcomes),
            known_jobs=len(known_outcomes),
            unseen_jobs=len(unseen_outcomes),
            pathological_jobs=len(pathological_outcomes),
            repair_generalization_rate=round(rgr, 4),
            repair_regression_rate=round(rrg, 4),
            false_repair_rate=round(frr, 4),
            causal_resolution_rate=round(crr, 4),
            zero_effect_rate=round(zer, 4),
            known_corpus_mean_score=round(mean_known, 4),
            unseen_corpus_mean_score=round(mean_unseen, 4),
            generalization_gap=round(gap, 4),
            generalization_warning=gen_warning,
            worst_case_score=round(worst_case, 4),
            unseen_blocker_retention_rate=round(unseen_blocker_retention, 4),
            mean_iterations_to_convergence=round(mean_iters, 2),
        )
