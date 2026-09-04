"""
Strongly typed contracts and data models for Iterative Refinement and Closed-Loop Material Improvement.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from app.blueprints.contracts import SemanticMaterialBlueprint
from app.composition.schemas import DocumentComposition
from app.critic.contracts import CritiqueReport
from app.director.contracts import LearningJourney
from app.quality.contracts import QualityReport


class RefinementStage(str, Enum):
    ANALYSIS = "analysis"
    PLANNING = "planning"
    PATCH_GENERATION = "patch_generation"
    CANDIDATE_EVALUATION = "candidate_evaluation"
    COMPARISON = "comparison"
    DECISION = "decision"
    CONVERGENCE_CHECK = "convergence_check"
    COMPLETE = "complete"
    STOPPED = "stopped"


class RefinementTargetLayer(str, Enum):
    BLUEPRINT = "blueprint"
    DIRECTOR = "director"
    CAPABILITY_SELECTION = "capability_selection"
    COMPOSITION = "composition"
    CONTENT = "content"
    DENSITY = "density"
    VISUAL_STRUCTURE = "visual_structure"
    FORMAT_METADATA = "format_metadata"


class RefinementScope(str, Enum):
    TOKEN = "token"
    BLOCK = "block"
    REGION = "region"
    PAGE = "page"
    SECTION = "section"
    DOCUMENT = "document"


class RefinementIntent(str, Enum):
    REORDER = "reorder"
    CLARIFY = "clarify"
    SIMPLIFY = "simplify"
    EXPAND = "expand"
    CONDENSE = "condense"
    REPLACE_CAPABILITY = "replace_capability"
    REMOVE_REDUNDANCY = "remove_redundancy"
    ADD_SCAFFOLDING = "add_scaffolding"
    REBALANCE_DENSITY = "rebalance_density"
    IMPROVE_TRANSITION = "improve_transition"
    STRENGTHEN_EVIDENCE = "strengthen_evidence"
    FIX_STRUCTURE = "fix_structure"


class RefinementRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImprovementDecision(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    RETRY = "retry"
    STOP_CONVERGED = "stop_converged"
    STOP_MAX_ITERATIONS = "stop_max_iterations"
    STOP_OSCILLATION = "stop_oscillation"
    STOP_RISK = "stop_risk"
    STOP_NO_IMPROVEMENT = "stop_no_improvement"


class InvariantCategory(str, Enum):
    SEMANTIC_INVARIANT = "semantic_invariant"
    PEDAGOGICAL_INVARIANT = "pedagogical_invariant"
    STRUCTURAL_INVARIANT = "structural_invariant"
    FORMAT_INVARIANT = "format_invariant"
    CONTENT_PRESERVATION_INVARIANT = "content_preservation_invariant"
    TRACE_INVARIANT = "trace_invariant"


class InvariantViolation(BaseModel):
    category: InvariantCategory
    invariant_name: str
    description: str
    violating_data: dict[str, Any] = Field(default_factory=dict)


class RefinementAction(BaseModel):
    action_id: str = Field(description="Unique deterministic action ID")
    source_finding_ids: list[str] = Field(default_factory=list, description="Quality or Critic finding IDs being addressed")
    target_layer: RefinementTargetLayer
    target_scope: RefinementScope
    target_identifier: str = Field(default="global", description="Page, block, or step ID targeted")
    intent: RefinementIntent
    rationale: str = Field(description="Explanation of why this action resolves the finding")
    expected_benefit: str = Field(description="Expected qualitative or quantitative improvement")
    estimated_risk: RefinementRisk = Field(default=RefinementRisk.LOW)
    constraints: list[str] = Field(default_factory=list)
    preservation_requirements: list[str] = Field(default_factory=list)


class RefinementPlan(BaseModel):
    plan_id: str = Field(description="Unique deterministic plan ID")
    source_artifact_id: str
    iteration: int = Field(default=1)
    actions: list[RefinementAction] = Field(default_factory=list)
    invariants: list[str] = Field(default_factory=list)
    expected_improvement: str = Field(default="")
    risk_summary: str = Field(default="LOW")
    trace: list[str] = Field(default_factory=list)


class RefinementPatch(BaseModel):
    patch_id: str = Field(description="Unique deterministic patch ID")
    target_layer: RefinementTargetLayer
    target_identifier: str
    change_summary: str
    source_action_ids: list[str] = Field(default_factory=list)
    before_state: dict[str, Any] = Field(default_factory=dict)
    after_state: dict[str, Any] = Field(default_factory=dict)


class RefinedArtifactBundle(BaseModel):
    """Holds the multi-layer state of an artifact version."""
    artifact_id: str
    blueprint: SemanticMaterialBlueprint
    composition: DocumentComposition
    journey: LearningJourney | None = None
    pdf_path: str | Path | None = None
    target_format: str = "a4_portrait"


class RefinementCandidate(BaseModel):
    candidate_id: str
    parent_artifact_id: str
    iteration: int
    patches: list[RefinementPatch] = Field(default_factory=list)
    artifact_bundle: RefinedArtifactBundle
    quality_report: QualityReport | None = None
    critique_report: CritiqueReport | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ImprovementComparison(BaseModel):
    iteration: int
    baseline_quality_score: float
    candidate_quality_score: float
    quality_delta: float
    baseline_findings_count: int
    candidate_findings_count: int
    resolved_finding_ids: list[str] = Field(default_factory=list)
    persisting_finding_ids: list[str] = Field(default_factory=list)
    new_regressions: list[str] = Field(default_factory=list)
    invariant_violations: list[InvariantViolation] = Field(default_factory=list)
    is_meaningful_improvement: bool = False
    decision: ImprovementDecision = ImprovementDecision.ACCEPT
    reasoning: str = ""


class RefinementTrace(BaseModel):
    iteration: int
    finding_ids_addressed: list[str] = Field(default_factory=list)
    actions_planned: list[str] = Field(default_factory=list)
    patches_applied: list[str] = Field(default_factory=list)
    candidate_score: float = 0.0
    quality_delta: float = 0.0
    decision: ImprovementDecision = ImprovementDecision.ACCEPT
    decision_reasoning: str = ""
