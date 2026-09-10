"""
Universal Document Intelligence System V5 — Generalization Validator & Anti-Masking Engine.

Phase 4.1: Distinguishes Generalization Failure from ordinary repair failure,
verifies that high aggregate scores do not mask catastrophic artifact failures,
and classifies failure taxonomy signatures.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.benchmarking.contracts import (
    BenchmarkExecutionOutcome,
    GeneralizationMetrics,
)
from app.benchmarking.taxonomy import (
    CorpusCategory,
    CorpusSplit,
    GeneralizationFailureType,
)

logger = logging.getLogger("benchmarking.generalization")


class GeneralizationValidator:
    """Classifies generalization outcomes and validates anti-masking guarantees."""

    @classmethod
    def classify_outcome_failure(
        cls,
        outcome: BenchmarkExecutionOutcome,
    ) -> Optional[GeneralizationFailureType]:
        """Classifies the exact generalization failure mode if an outcome did not export cleanly."""
        if outcome.has_export_package and outcome.hard_blockers_count == 0:
            return None

        # 1. Did an operator trigger regression?
        if len(outcome.operators_rolled_back) > 0:
            return GeneralizationFailureType.REGRESSION_FAILURE

        # 2. Did mutations execute with zero effect?
        if len(outcome.zero_effect_operators) > 0:
            return GeneralizationFailureType.ZERO_EFFECT_FAILURE

        # 3. Was it a pathological input that is theoretically non-automatable?
        if outcome.corpus_category == CorpusCategory.PATHOLOGICAL:
            return GeneralizationFailureType.NON_AUTOMATABLE_GENERALIZATION_FAILURE

        # 4. Did structural collision/overflow persist on unseen structural signatures?
        if outcome.split == CorpusSplit.UNSEEN_GENERALIZATION:
            if any("COLLISION" in b or "OVERFLOW" in b for b in outcome.hard_blockers):
                return GeneralizationFailureType.STRUCTURAL_GENERALIZATION_FAILURE
            if any("INQUIRY" in b or "STREAK" in b or "CLAIM" in b for b in outcome.hard_blockers):
                return GeneralizationFailureType.SEMANTIC_GENERALIZATION_FAILURE

        # 5. Causal mismatch or execution failure
        if outcome.total_iterations >= 3 and outcome.hard_blockers_count > 0:
            return GeneralizationFailureType.CAUSAL_MISMATCH

        return GeneralizationFailureType.EXECUTION_FAILURE

    @classmethod
    def check_anti_masking(
        cls,
        outcomes: Sequence[BenchmarkExecutionOutcome],
        metrics: GeneralizationMetrics,
        threshold_min_score: float = 0.750,
    ) -> Tuple[bool, List[str]]:
        """Verifies that high average scores are not masking catastrophic artifact drops."""
        violations: List[str] = []

        for o in outcomes:
            if o.overall_quality_score < threshold_min_score:
                violations.append(
                    f"Catastrophic score drop masked by average: {o.fixture_id} ({o.artifact_type}) scored {o.overall_quality_score:.3f} < {threshold_min_score}"
                )
            if o.hard_blockers_count > 0 and o.split == CorpusSplit.UNSEEN_GENERALIZATION:
                violations.append(
                    f"Unseen hard blocker retention masked by average: {o.fixture_id} ({o.artifact_type}) retained {o.hard_blockers_count} blockers"
                )

        has_masking = len(violations) > 0
        return has_masking, violations
