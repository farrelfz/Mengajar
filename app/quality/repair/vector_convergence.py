"""
Universal Document Intelligence System V5 — Quality Vector Convergence & Pattern Detection.

Phase 3D.1: Multi-dimensional QualityVector, blocker-aware progress prioritization,
local minimum detection (TOKEN_CHURN, SCOPE_CHURN, SYMPTOM_LOOP, FALSE_PROGRESS),
and budget reservation policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.authority import UnifiedQualityReport
from app.quality.repair.mutation_contract import RepairMutationScope


class FailurePatternType(str, Enum):
    """Patterns indicating that repair is trapped in a local minimum or symptom loop."""
    TOKEN_CHURN = "TOKEN_CHURN"                    # Same discrete token modified repeatedly without blocker reduction
    SCOPE_CHURN = "SCOPE_CHURN"                    # Consecutive low-level mutations yielding zero blocker reduction
    SYMPTOM_LOOP = "SYMPTOM_LOOP"                  # Same symptom/defect repeatedly targeted without curing root cause
    ROOT_CAUSE_MISMATCH = "ROOT_CAUSE_MISMATCH"    # Selected mutation target does not address causal ancestor
    FALSE_PROGRESS = "FALSE_PROGRESS"              # Overall score increased but hard blocker count remained unchanged
    HEALTHY_PROGRESS = "HEALTHY_PROGRESS"          # Legitimate blocker reduction or vector improvement


class QualityVector(BaseModel):
    """Authoritative 4-dimensional quality vector."""
    model_config = ConfigDict(frozen=True)

    semantic_integrity: float = 1.0
    artifact_fidelity: float = 1.0
    artifact_quality: float = 1.0
    rendered_quality: float = 1.0

    @classmethod
    def from_report(cls, report: UnifiedQualityReport) -> QualityVector:
        ds = report.domain_scores or {}
        return cls(
            semantic_integrity=round(float(ds.get("semantic_integrity", 1.0)), 3),
            artifact_fidelity=round(float(ds.get("artifact_fidelity", 1.0)), 3),
            artifact_quality=round(float(ds.get("artifact_quality", 1.0)), 3),
            rendered_quality=round(float(ds.get("rendered_quality", 1.0)), 3),
        )

    def dominates(self, other: QualityVector) -> bool:
        """Dominance Rule: True if no dimension worsens and at least one improves."""
        vals_self = [self.semantic_integrity, self.artifact_fidelity, self.artifact_quality, self.rendered_quality]
        vals_other = [other.semantic_integrity, other.artifact_fidelity, other.artifact_quality, other.rendered_quality]

        no_worse = all(s >= o for s, o in zip(vals_self, vals_other))
        strictly_better = any(s > o for s, o in zip(vals_self, vals_other))
        return no_worse and strictly_better


class ConvergenceProgressVector(BaseModel):
    """Comprehensive multi-attribute progress snapshot per iteration."""
    model_config = ConfigDict(frozen=True)

    iteration: int
    hard_blocker_count: int
    critical_finding_count: int
    affected_element_count: int
    root_cause_coverage: float
    quality_vector: QualityVector
    overall_score: float
    drift: float = 0.0
    mutation_cost: float = 0.0
    applied_strategy_id: Optional[str] = None
    applied_scope: Optional[RepairMutationScope] = None


class RepairFailurePatternDetector:
    """Detects ineffective repair loops and triggers evidence-based escalation."""

    @classmethod
    def analyze_history(
        cls,
        history: Sequence[ConvergenceProgressVector],
    ) -> Tuple[FailurePatternType, str]:
        if len(history) < 2:
            return FailurePatternType.HEALTHY_PROGRESS, "Initial iteration baseline."

        curr = history[-1]
        prev = history[-2]

        # 1. FALSE_PROGRESS: score went up, but hard blockers remained identical
        if curr.overall_score > prev.overall_score and curr.hard_blocker_count > 0 and curr.hard_blocker_count >= prev.hard_blocker_count:
            return (
                FailurePatternType.FALSE_PROGRESS,
                f"Score increased from {prev.overall_score:.3f} to {curr.overall_score:.3f} but hard blockers remained {curr.hard_blocker_count} (False Progress).",
            )

        # 2. TOKEN_CHURN: repeated Level 1 mutations with zero blocker change
        if len(history) >= 3:
            last_3_scopes = [h.applied_scope for h in history[-3:]]
            if all(s == RepairMutationScope.LEVEL_1_LOCAL_TOKEN for s in last_3_scopes if s is not None):
                if curr.hard_blocker_count == history[-3].hard_blocker_count:
                    return (
                        FailurePatternType.TOKEN_CHURN,
                        "Repeated LEVEL_1_LOCAL_TOKEN mutations failed to reduce hard blockers across 3 cycles.",
                    )

        # 3. SCOPE_CHURN: multiple low-level mutations without blocker reduction
        if curr.hard_blocker_count > 0 and curr.hard_blocker_count >= prev.hard_blocker_count:
            if curr.applied_strategy_id == prev.applied_strategy_id:
                return (
                    FailurePatternType.SYMPTOM_LOOP,
                    f"Same strategy '{curr.applied_strategy_id}' repeatedly applied with zero blocker reduction.",
                )

        # 4. Healthy Progress: blocker reduction or non-worsening vector improvement
        if curr.hard_blocker_count < prev.hard_blocker_count:
            return FailurePatternType.HEALTHY_PROGRESS, f"Hard blockers reduced from {prev.hard_blocker_count} to {curr.hard_blocker_count}."

        if curr.quality_vector.dominates(prev.quality_vector):
            return FailurePatternType.HEALTHY_PROGRESS, "Quality vector strictly dominates previous iteration."

        return FailurePatternType.HEALTHY_PROGRESS, "Iteration progressed within nominal thresholds."


class BudgetReservationPolicy:
    """
    Guarantees mutation budget is preserved for structural repairs (R2/R3)
    and prevents low-level token tweaks from consuming the entire iteration limit.
    """

    @classmethod
    def get_allowed_scopes_for_iteration(
        cls,
        iteration: int,
        max_iterations: int,
        pattern: FailurePatternType,
    ) -> List[RepairMutationScope]:
        """
        Evidence-based escalation:
        If stuck in TOKEN_CHURN, SCOPE_CHURN, or SYMPTOM_LOOP, strictly escalate scope!
        """
        if pattern in (FailurePatternType.TOKEN_CHURN, FailurePatternType.SCOPE_CHURN, FailurePatternType.SYMPTOM_LOOP):
            # Escalate directly to R1 / R2 / R3!
            return [
                RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
                RepairMutationScope.LEVEL_3_PAGE_COMPOSITION,
                RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING,
            ]

        if iteration == 1:
            # First iteration prefers minimal intervention (R0, R1)
            return [
                RepairMutationScope.LEVEL_1_LOCAL_TOKEN,
                RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
                RepairMutationScope.LEVEL_3_PAGE_COMPOSITION,
            ]
        elif iteration == 2:
            return [
                RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
                RepairMutationScope.LEVEL_3_PAGE_COMPOSITION,
                RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING,
            ]
        else:
            # Later iterations prioritize structural / blueprint fixes
            return [
                RepairMutationScope.LEVEL_3_PAGE_COMPOSITION,
                RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING,
                RepairMutationScope.LEVEL_5_ARTIFACT_STRUCTURE,
            ]
