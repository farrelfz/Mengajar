"""
KIR AI Document Intelligence — Quality Evaluation Contracts (Legacy Compatibility).

Preserves all legacy contracts for quality evaluation:
QualityDimension, QualitySeverity, QualityLevel, EvaluationStage, QualityGateDecision,
QualityFinding, QualityMetric, QualityScore, EvaluationTrace, QualityGateResult, QualityReport.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class QualityDimension(str, Enum):
    """Core dimensions of artifact quality."""
    SEMANTIC_CORRECTNESS = "semantic_correctness"
    PEDAGOGICAL_ALIGNMENT = "pedagogical_alignment"
    STRUCTURAL_COHERENCE = "structural_coherence"
    INFORMATION_DENSITY = "information_density"
    VISUAL_APPROPRIATENESS = "visual_appropriateness"
    FORMAT_INTEGRITY = "format_integrity"
    REDUNDANCY = "redundancy"
    LEARNER_ALIGNMENT = "learner_alignment"
    ACCESSIBILITY = "accessibility"


class QualitySeverity(str, Enum):
    """Severity levels for quality findings."""
    INFO = "info"
    LOW = "low"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class QualityLevel(str, Enum):
    """Human-interpretable categorical quality grade."""
    EXCELLENT = "excellent"           # >= 0.95
    GOOD = "good"                     # >= 0.85
    ACCEPTABLE = "acceptable"         # >= 0.75
    NEEDS_IMPROVEMENT = "needs_improvement"  # >= 0.60
    POOR = "poor"                     # >= 0.40
    CRITICAL = "critical"             # < 0.40


class EvaluationStage(str, Enum):
    """Pipeline lifecycle stage at which evaluation occurs."""
    BLUEPRINT = "blueprint"
    COMPOSITION = "composition"
    ARTIFACT = "artifact"


class QualityGateDecision(str, Enum):
    """Formal decision rendered by the Quality Gate."""
    PASS = "pass"
    PASS_WITH_WARNINGS = "pass_with_warnings"
    NEEDS_REFINEMENT = "needs_refinement"
    FAIL = "fail"


class QualityFinding(BaseModel):
    """An individual quality diagnosis with evidence and actionable recommendations."""
    id: str | None = None
    dimension: QualityDimension
    severity: QualitySeverity
    finding: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    affected_artifact: str = "main"
    affected_section: str | None = None
    score_impact: float = 0.0
    recommendation: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    is_deterministic: bool = True


class QualityMetric(BaseModel):
    """A discrete, measurable quality metric with weight and raw score."""
    name: str
    dimension: QualityDimension
    score: float = Field(ge=0.0, le=1.0)
    weight: float = 1.0
    raw_value: Any = None
    threshold: float | None = None
    status: str = "evaluated"
    details: dict[str, Any] = Field(default_factory=dict)


class QualityScore(BaseModel):
    """Aggregated quality scoring across all dimensions."""
    overall_score: float = Field(ge=0.0, le=1.0)
    dimensional_scores: dict[str, float] = Field(default_factory=dict)
    quality_level: QualityLevel = QualityLevel.GOOD
    is_passing: bool = True


class EvaluationTrace(BaseModel):
    """Full explainability record of the quality evaluation process."""
    evaluator_traces: list[dict[str, Any]] = Field(default_factory=list)
    stage_evaluations: dict[str, Any] = Field(default_factory=dict)
    score_computation_log: list[str] = Field(default_factory=list)


class QualityGateResult(BaseModel):
    """Outcome of evaluating an artifact against the Quality Gate."""
    decision: QualityGateDecision
    score: QualityScore
    critical_findings: list[QualityFinding] = Field(default_factory=list)
    warnings: list[QualityFinding] = Field(default_factory=list)
    can_proceed: bool = True
    gate_reasoning: str


class QualityReport(BaseModel):
    """Complete diagnostic report produced by the Quality Evaluation Engine."""
    job_id: str
    overall_score: float
    quality_level: QualityLevel = QualityLevel.GOOD
    gate_result: QualityGateResult
    findings: list[QualityFinding] = Field(default_factory=list)
    metrics: list[QualityMetric] = Field(default_factory=list)
    trace: EvaluationTrace = Field(default_factory=EvaluationTrace)
    metadata: dict[str, Any] = Field(default_factory=dict)
