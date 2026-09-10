"""
Universal Document Intelligence System V5 — Quality Contracts.

Phase 2C: Explicit separation of Quality from Fidelity.
Quality Validation answers: "Is the resulting artifact actually good?"
- visual_quality
- information_design
- artifact_specific_quality
- composition_quality
- readability_quality
- rhythm_quality
- structural_quality
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.legacy_contracts import (
    QualityDimension,
    QualityFinding,
    QualityLevel,
    QualitySeverity,
)


class QualitySignalExplanation(BaseModel):
    """Explainable diagnostic signal contributing to a quality score."""
    model_config = ConfigDict(frozen=True)

    signal: str
    value: Any
    expected: str
    impact: float
    dimension: str
    description: str = ""


class ArtifactQualityReport(BaseModel):
    """Authoritative quality evaluation report for an artifact.
    
    Evaluates design, ergonomics, pedagogical effectiveness, and readability:
    - visual_quality (hierarchy, styling, collision)
    - information_design (visual grammar, semantic alignment, density)
    - artifact_specific_quality (pedagogical inquiry, scientific rigor)
    - composition_quality (balance, layout diversity, whitespace)
    - readability_quality (typography scale, text clipping, contrast)
    - rhythm_quality (pacing, streak prevention, cognitive cadence)
    - structural_quality (section transitions, heading hierarchy)
    
    CRITICAL RULE:
    High quality MUST NOT hide semantic corruption or contract violations.
    """
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    visual_quality: float = Field(ge=0.0, le=1.0)
    information_design: float = Field(ge=0.0, le=1.0)
    artifact_specific_quality: float = Field(ge=0.0, le=1.0)
    composition_quality: float = Field(ge=0.0, le=1.0)
    readability_quality: float = Field(ge=0.0, le=1.0)
    rhythm_quality: float = Field(ge=0.0, le=1.0)
    structural_quality: float = Field(default=1.0, ge=0.0, le=1.0)
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    quality_level: QualityLevel = QualityLevel.GOOD
    is_passing: bool = True
    dimensional_scores: Dict[str, float] = Field(default_factory=dict)
    signals: Tuple[QualitySignalExplanation, ...] = Field(default_factory=tuple)
    explanations: Tuple[str, ...] = Field(default_factory=tuple)
    findings: Tuple[QualityFinding, ...] = Field(default_factory=tuple)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    evaluated_at: float = Field(default_factory=time.time)

    @classmethod
    def compute(
        cls,
        artifact_type: str,
        visual_quality: float,
        information_design: float,
        artifact_specific_quality: float,
        composition_quality: float,
        readability_quality: float,
        rhythm_quality: float,
        structural_quality: float = 1.0,
        signals: List[QualitySignalExplanation] | None = None,
        explanations: List[str] | None = None,
        findings: List[QualityFinding] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> ArtifactQualityReport:
        dim_scores = {
            "visual_quality": round(visual_quality, 3),
            "information_design": round(information_design, 3),
            "artifact_specific_quality": round(artifact_specific_quality, 3),
            "composition_quality": round(composition_quality, 3),
            "readability_quality": round(readability_quality, 3),
            "rhythm_quality": round(rhythm_quality, 3),
            "structural_quality": round(structural_quality, 3),
        }

        # Weighted composite score
        overall = round(
            (
                visual_quality * 0.15
                + information_design * 0.20
                + artifact_specific_quality * 0.25
                + composition_quality * 0.15
                + readability_quality * 0.10
                + rhythm_quality * 0.10
                + structural_quality * 0.05
            ),
            3,
        )
        overall = max(0.0, min(1.0, overall))

        # Determine QualityLevel
        if overall >= 0.95:
            q_level = QualityLevel.EXCELLENT
        elif overall >= 0.85:
            q_level = QualityLevel.GOOD
        elif overall >= 0.75:
            q_level = QualityLevel.ACCEPTABLE
        elif overall >= 0.60:
            q_level = QualityLevel.NEEDS_IMPROVEMENT
        elif overall >= 0.40:
            q_level = QualityLevel.POOR
        else:
            q_level = QualityLevel.CRITICAL

        f_list = list(findings or [])
        has_critical = any(f.severity == QualitySeverity.CRITICAL for f in f_list)
        is_passing = overall >= 0.75 and not has_critical

        return cls(
            artifact_type=artifact_type,
            visual_quality=round(visual_quality, 3),
            information_design=round(information_design, 3),
            artifact_specific_quality=round(artifact_specific_quality, 3),
            composition_quality=round(composition_quality, 3),
            readability_quality=round(readability_quality, 3),
            rhythm_quality=round(rhythm_quality, 3),
            structural_quality=round(structural_quality, 3),
            overall_quality_score=overall,
            quality_level=q_level,
            is_passing=is_passing,
            dimensional_scores=dim_scores,
            signals=tuple(signals or []),
            explanations=tuple(explanations or []),
            findings=tuple(f_list),
            metadata=metadata or {},
        )
