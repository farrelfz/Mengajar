"""
Universal Document Intelligence System V5 — Canonical Repair Contracts.

Phase 3B: Immutable contracts for root-cause-aware targeted repair,
mutation classifications, repair planning, execution results, and history tracking.
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.decisions import UnifiedQualityDecision
from app.quality.contracts.findings import QualityFinding


class RepairMutationClass(str, Enum):
    """Six orthogonal mutation classes establishing strict boundaries on automated repair."""
    CLASS_A_GEOMETRY = "CLASS_A_GEOMETRY"  # Non-semantic physical (padding, margins, grid)
    CLASS_B_COMPOSITION = "CLASS_B_COMPOSITION"  # Compositional (split, merge, rebalance, cards)
    CLASS_C_LAYOUT_REMAPPING = "CLASS_C_LAYOUT_REMAPPING"  # Visual grammar layout family remap
    CLASS_D_PEDAGOGICAL_STRUCTURE = "CLASS_D_PEDAGOGICAL_STRUCTURE"  # Inquiry arc, narrative order
    CLASS_E_SEMANTIC_INTEGRITY = "CLASS_E_SEMANTIC_INTEGRITY"  # Claim evidence link, certainty soften
    CLASS_F_NON_REPAIRABLE = "CLASS_F_NON_REPAIRABLE"  # Contradictions, missing source -> Escalate


class RepairRiskLevel(str, Enum):
    """Risk tiers for repair interventions."""
    LOW = "LOW"          # Safe local adjustment (padding, spacing)
    MEDIUM = "MEDIUM"    # Compositional change (slide split, layout remap)
    HIGH = "HIGH"        # Pedagogical reorder or claim certainty downgrade
    CRITICAL = "CRITICAL" # Potential information loss or semantic refactor


class ConvergenceState(str, Enum):
    """State of the repair iteration loop."""
    CONVERGED = "CONVERGED"
    PARTIALLY_CONVERGED = "PARTIALLY_CONVERGED"
    NO_SAFE_REPAIR = "NO_SAFE_REPAIR"
    OSCILLATION_DETECTED = "OSCILLATION_DETECTED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    ESCALATED = "ESCALATED"
    IN_PROGRESS = "IN_PROGRESS"


class RepairTarget(BaseModel):
    """Identifies the precise artifact unit targeted for repair."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    artifact_id: str = "main"
    page_index: Optional[int] = None
    slide_index: Optional[int] = None
    element_id: Optional[str] = None
    blueprint_element_id: Optional[str] = None
    source_knowledge_ids: Tuple[str, ...] = Field(default_factory=tuple)
    affected_region: Optional[str] = None


class RepairAction(BaseModel):
    """A single deterministic mutation planned or applied to a target."""
    model_config = ConfigDict(frozen=True)

    action_id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:8]}")
    strategy_id: str
    target: RepairTarget
    mutation_type: str
    mutation_class: RepairMutationClass
    before_state_hash: str
    after_state_hash: Optional[str] = None
    rationale: str
    expected_effect: str
    risk_level: RepairRiskLevel = RepairRiskLevel.LOW
    reversibility: bool = True
    dependencies: Tuple[str, ...] = Field(default_factory=tuple)


class RepairPlan(BaseModel):
    """An ordered set of repair actions addressing an attributed root cause."""
    model_config = ConfigDict(frozen=True)

    plan_id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:8]}")
    root_cause_id: str
    artifact_type: str
    actions: Tuple[RepairAction, ...] = Field(default_factory=tuple)
    execution_order: Tuple[str, ...] = Field(default_factory=tuple)
    expected_quality_improvement: float = Field(default=0.0, ge=0.0, le=1.0)
    estimated_regression_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    iteration_number: int = 1


class RepairResult(BaseModel):
    """Output of executing a repair plan, evaluated authoritatively."""
    model_config = ConfigDict(frozen=True)

    plan_id: str
    success: bool
    actions_applied: Tuple[RepairAction, ...] = Field(default_factory=tuple)
    actions_skipped: Tuple[RepairAction, ...] = Field(default_factory=tuple)
    pre_authority: UnifiedQualityDecision
    post_authority: Optional[UnifiedQualityDecision] = None
    improved_dimensions: Tuple[str, ...] = Field(default_factory=tuple)
    regressed_dimensions: Tuple[str, ...] = Field(default_factory=tuple)
    unresolved_findings: Tuple[str, ...] = Field(default_factory=tuple)
    convergence_state: ConvergenceState = ConvergenceState.IN_PROGRESS


class RepairHistoryEntry(BaseModel):
    """Immutable audit entry for a single repair iteration."""
    model_config = ConfigDict(frozen=True)

    iteration: int
    authority_decision_before: str
    findings_before: Tuple[str, ...] = Field(default_factory=tuple)
    root_cause: str
    repair_plan_id: str
    mutations: Tuple[str, ...] = Field(default_factory=tuple)
    authority_decision_after: str
    score_delta: float = 0.0
    regressions: Tuple[str, ...] = Field(default_factory=tuple)
    timestamp: float = Field(default_factory=time.time)


class RepairRequest(BaseModel):
    """Formal request initiated by UnifiedQualityAuthority routing to repair engine."""
    model_config = ConfigDict(frozen=True)

    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    authority_decision: UnifiedQualityDecision
    triggering_findings: Tuple[QualityFinding, ...] = Field(default_factory=tuple)
    correlated_cluster_ids: Tuple[str, ...] = Field(default_factory=tuple)
    root_cause_hypothesis: Optional[Any] = None
    artifact_type: str
    targets: Tuple[RepairTarget, ...] = Field(default_factory=tuple)
    repair_priority: int = 1
    repair_budget: int = 3
    forbidden_mutations: Tuple[RepairMutationClass, ...] = Field(default_factory=tuple)
    expected_postconditions: Tuple[str, ...] = Field(default_factory=tuple)
