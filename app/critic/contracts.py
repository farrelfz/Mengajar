"""
Strongly typed contracts and data models for the Generative Critic subsystem.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class CritiquePerspective(str, Enum):
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    PEDAGOGICAL = "pedagogical"
    COGNITIVE_LOAD = "cognitive_load"
    NARRATIVE = "narrative"
    VISUAL_COMMUNICATION = "visual_communication"
    SCIENTIFIC_RIGOR = "scientific_rigor"
    AUDIENCE = "audience"
    REDUNDANCY = "redundancy"
    CAPABILITY_SELECTION = "capability_selection"


class CritiqueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CritiqueConfidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CERTAIN = "certain"


class CritiquePriority(str, Enum):
    BLOCKER = "blocker"
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CritiqueStatus(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"


class ImplementationScope(str, Enum):
    BLOCK = "block"
    REGION = "region"
    PAGE = "page"
    SECTION = "section"
    DOCUMENT = "document"
    GLOBAL_PATTERN = "global_pattern"


class CritiqueEvidence(BaseModel):
    source: str = Field(description="Evidence source (e.g. blueprint, composition, quality_report, director)")
    location: str = Field(default="global", description="Specific page, step, or block identifier")
    observation: str = Field(description="Direct factual observation of what is present or missing")
    supporting_data: dict[str, Any] = Field(default_factory=dict, description="Structured numerical or categorical data")
    confidence: CritiqueConfidence = Field(default=CritiqueConfidence.HIGH, description="Confidence in this evidence item")


class CritiqueFinding(BaseModel):
    id: str = Field(description="Unique deterministic identifier for the finding")
    perspective: CritiquePerspective = Field(description="Perspective from which this critique originated")
    title: str = Field(description="Concise human-readable title summarizing the issue")
    observation: str = Field(description="What was directly observed in the artifact")
    diagnosis: str = Field(description="Causal explanation of why this observation represents a weakness")
    why_it_matters: str = Field(description="Educational, scientific, or cognitive rationale for fixing it")
    evidence: list[CritiqueEvidence] = Field(default_factory=list, description="Supporting evidence items")
    severity: CritiqueSeverity = Field(default=CritiqueSeverity.MEDIUM, description="Severity of the issue")
    confidence: CritiqueConfidence = Field(default=CritiqueConfidence.HIGH, description="Confidence in this diagnosis")
    affected_locations: list[str] = Field(default_factory=list, description="List of affected sections, pages, or blocks")
    improvement_direction: str = Field(description="Actionable guidance on how to resolve or improve the artifact")


class CritiqueRecommendation(BaseModel):
    id: str = Field(description="Unique deterministic recommendation identifier")
    finding_ids: list[str] = Field(default_factory=list, description="Findings addressed by this recommendation")
    recommendation: str = Field(description="Concrete guidance on what improvement direction to take")
    rationale: str = Field(description="Why this recommendation resolves the identified weaknesses")
    expected_impact: str = Field(description="Expected qualitative improvement once addressed")
    implementation_scope: ImplementationScope = Field(default=ImplementationScope.PAGE, description="Scope of the recommendation")
    priority: CritiquePriority = Field(default=CritiquePriority.MEDIUM, description="Actionable priority ranking")


class CritiqueConflict(BaseModel):
    conflict_id: str = Field(description="Unique conflict identifier")
    conflict_type: str = Field(description="Nature of tension (e.g. pedagogy_vs_cognitive_load)")
    perspectives: list[CritiquePerspective] = Field(description="Critics with competing assessments")
    competing_findings: list[str] = Field(description="IDs of findings in tension")
    synthesis_question: str = Field(description="Core trade-off question to be resolved by the refiner")


class CritiqueAgreement(BaseModel):
    agreement_id: str = Field(description="Unique agreement identifier")
    finding_ids: list[str] = Field(description="Related findings identified by multiple critics")
    perspectives: list[CritiquePerspective] = Field(description="Critics that independently arrived at the same conclusion")
    shared_conclusion: str = Field(description="Summary of the shared diagnosis")
    agreement_strength: str = Field(default="HIGH", description="Strength of consensus (e.g. LOW, MEDIUM, HIGH)")


class CritiqueTrace(BaseModel):
    critics_executed: list[str] = Field(default_factory=list)
    critics_skipped: list[str] = Field(default_factory=list)
    critics_failed: list[str] = Field(default_factory=list)
    evidence_sources: list[str] = Field(default_factory=list)
    reasoning_steps: list[str] = Field(default_factory=list)
    synthesis_steps: list[str] = Field(default_factory=list)
    conflicts_detected: int = Field(default=0)
    agreements_detected: int = Field(default=0)


class CritiqueReport(BaseModel):
    artifact_id: str = Field(description="Identifier of the artifact evaluated")
    overall_assessment: str = Field(description="Synthesized executive critique summary")
    findings: list[CritiqueFinding] = Field(default_factory=list)
    recommendations: list[CritiqueRecommendation] = Field(default_factory=list)
    conflicts: list[CritiqueConflict] = Field(default_factory=list)
    agreements: list[CritiqueAgreement] = Field(default_factory=list)
    priority_queue: list[str] = Field(default_factory=list, description="Ordered finding IDs from highest to lowest priority")
    trace: CritiqueTrace = Field(default_factory=CritiqueTrace)
    metadata: dict[str, Any] = Field(default_factory=dict)
