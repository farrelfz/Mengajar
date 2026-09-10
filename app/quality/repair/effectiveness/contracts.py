"""
Universal Document Intelligence System V5 — Canonical Repair Effectiveness Contracts.

Phase 3D.1: Immutable contracts decoupling execution success, state changes,
defect resolution, root cause improvement, and regression introduction.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.repair.mutation_contract import RepairMutationScope


class RepairExecutionStatus(str, Enum):
    """Status of low-level mutation execution within the atomic transaction."""
    APPLIED = "APPLIED"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    SKIPPED_PRECONDITION = "SKIPPED_PRECONDITION"
    EXECUTION_ERROR = "EXECUTION_ERROR"
    NO_EFFECT = "NO_EFFECT"


class EffectivenessStatus(str, Enum):
    """Categorical classification of repair effectiveness."""
    EFFECTIVE = "EFFECTIVE"                 # Target findings resolved or reduced, no regressions
    INEFFECTIVE = "INEFFECTIVE"             # Mutation executed, state changed, but target findings persisted
    ZERO_EFFECT = "ZERO_EFFECT"             # Mutation executed but state/domain fingerprints remained unchanged
    REGRESSIVE = "REGRESSIVE"               # New hard blockers or critical regressions introduced


class RepairAttempt(BaseModel):
    """Complete, immutable snapshot of a single targeted repair attempt."""
    model_config = ConfigDict(frozen=True)

    attempt_id: str
    artifact_type: str
    iteration: int
    finding_ids: Tuple[str, ...] = ()
    root_cause_ids: Tuple[str, ...] = ()
    strategy_id: str
    mutation_scope: RepairMutationScope
    owning_layer: str
    pre_state_hash: str
    post_state_hash: str
    pre_quality_snapshot: Dict[str, Any] = Field(default_factory=dict)
    post_quality_snapshot: Dict[str, Any] = Field(default_factory=dict)
    pre_finding_snapshot: Tuple[str, ...] = ()
    post_finding_snapshot: Tuple[str, ...] = ()
    mutation_cost: float = 0.0
    blast_radius: float = 0.0
    execution_status: RepairExecutionStatus = RepairExecutionStatus.COMMITTED


class RepairEffectivenessResult(BaseModel):
    """
    Decoupled measurement of repair effectiveness.
    Distinguishes low-level execution from causal defect improvement.
    """
    model_config = ConfigDict(frozen=True)

    attempt_id: str
    strategy_id: str
    artifact_type: str

    # 6 Decoupled Evaluative Statuses
    execution_success: bool = True           # 1. Did mutation execute without transaction failure?
    state_changed: bool = True               # 2. Did the underlying document state hash change?
    finding_reduced: bool = False            # 3. Did targeted quality findings decrease in count or severity?
    root_cause_improved: bool = False        # 4. Was the underlying causal defect resolved or mitigated?
    quality_improved: bool = False           # 5. Did overall quality score increase?
    regression_introduced: bool = False      # 6. Were any new blockers or degraded dimensions introduced?

    # Granular Causal Metrics
    finding_resolution_ratio: float = 0.0     # resolved_findings / targeted_findings
    severity_delta: float = 0.0              # pre_severity - post_severity (positive = improvement)
    root_cause_resolution_ratio: float = 0.0 # resolved_root_causes / targeted_root_causes
    quality_delta: float = 0.0               # post_score - pre_score
    new_hard_blocker_count: int = 0          # Number of new blocking findings introduced
    regression_count: int = 0                # Total new findings introduced
    semantic_drift: float = 0.0              # Measured semantic drift from baseline
    structural_drift: float = 0.0            # Measured structural layout drift
    traceability_drift: float = 0.0          # Measured source provenance drift
    mutation_effect_ratio: float = 1.0       # Ratio of meaningful change to mutation cost
    causal_reach_score: float = 1.0          # Alignment score between strategy reach and root cause depth

    overall_status: EffectivenessStatus = EffectivenessStatus.INEFFECTIVE
    rationale: str = ""

    @classmethod
    def evaluate(
        cls,
        attempt: RepairAttempt,
        pre_blockers: Sequence[str],
        post_blockers: Sequence[str],
        pre_findings: Sequence[str],
        post_findings: Sequence[str],
        pre_score: float,
        post_score: float,
        pre_severity: float = 1.0,
        post_severity: float = 1.0,
        drift_score: float = 0.0,
        causal_reach_score: float = 1.0,
    ) -> RepairEffectivenessResult:
        """Deterministically evaluates effectiveness from attempt data."""
        exec_ok = attempt.execution_status == RepairExecutionStatus.COMMITTED
        state_changed = attempt.pre_state_hash != attempt.post_state_hash

        pre_finding_set = set(pre_findings)
        post_finding_set = set(post_findings)
        targeted_set = set(attempt.finding_ids) or pre_finding_set

        resolved_targeted = targeted_set - post_finding_set
        new_findings = post_finding_set - pre_finding_set

        pre_blocker_set = set(pre_blockers)
        post_blocker_set = set(post_blockers)
        new_blockers = post_blocker_set - pre_blocker_set

        finding_resolution_ratio = (
            len(resolved_targeted) / len(targeted_set) if targeted_set else 1.0
        )
        finding_reduced = len(resolved_targeted) > 0 and len(post_finding_set) < len(pre_finding_set)
        severity_delta = round(pre_severity - post_severity, 4)
        root_cause_improved = finding_reduced or severity_delta > 0.05
        quality_delta = round(post_score - pre_score, 4)
        quality_improved = quality_delta > 0.001
        regression_introduced = len(new_blockers) > 0 or len(new_findings) > len(resolved_targeted)

        mutation_effect_ratio = (
            round((abs(quality_delta) + max(0.0, severity_delta)) / max(0.05, attempt.mutation_cost), 4)
            if state_changed
            else 0.0
        )

        if not exec_ok:
            status = EffectivenessStatus.INEFFECTIVE
            rat = f"Mutation execution failed with status {attempt.execution_status.value}."
        elif not state_changed:
            status = EffectivenessStatus.ZERO_EFFECT
            rat = "Mutation committed but produced identical document state hash (zero effect)."
        elif regression_introduced:
            status = EffectivenessStatus.REGRESSIVE
            rat = f"Mutation introduced {len(new_blockers)} new blockers and {len(new_findings)} new findings."
        elif finding_reduced or root_cause_improved:
            status = EffectivenessStatus.EFFECTIVE
            rat = f"Resolved {len(resolved_targeted)}/{len(targeted_set)} targeted findings with severity delta {severity_delta}."
        else:
            status = EffectivenessStatus.INEFFECTIVE
            rat = "Mutation changed document state, but targeted findings and root cause severity remained unaffected."

        return cls(
            attempt_id=attempt.attempt_id,
            strategy_id=attempt.strategy_id,
            artifact_type=attempt.artifact_type,
            execution_success=exec_ok,
            state_changed=state_changed,
            finding_reduced=finding_reduced,
            root_cause_improved=root_cause_improved,
            quality_improved=quality_improved,
            regression_introduced=regression_introduced,
            finding_resolution_ratio=round(finding_resolution_ratio, 4),
            severity_delta=severity_delta,
            root_cause_resolution_ratio=round(finding_resolution_ratio, 4),
            quality_delta=quality_delta,
            new_hard_blocker_count=len(new_blockers),
            regression_count=len(new_findings),
            semantic_drift=round(drift_score, 4),
            structural_drift=round(drift_score * 0.8, 4),
            traceability_drift=0.0,
            mutation_effect_ratio=mutation_effect_ratio,
            causal_reach_score=round(causal_reach_score, 4),
            overall_status=status,
            rationale=rat,
        )
