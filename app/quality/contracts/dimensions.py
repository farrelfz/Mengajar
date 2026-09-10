"""
Universal Document Intelligence System V5 — Canonical Quality Dimensions.

Phase 3A.1: Dimensional score aggregation contracts preserving individual
dimension scores, weights, confidence, and contributing signals.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field


class CanonicalQualityDimension(str, Enum):
    """Canonical dimensions covering all four quality truth layers."""
    # Layer 1: Semantic Integrity
    SEMANTIC_GROUNDING = "SEMANTIC_GROUNDING"
    CLAIM_VERACITY = "CLAIM_VERACITY"
    KNOWLEDGE_TRACEABILITY = "KNOWLEDGE_TRACEABILITY"

    # Layer 2: Artifact Fidelity
    BLUEPRINT_FIDELITY = "BLUEPRINT_FIDELITY"
    ELEMENT_SURVIVAL = "ELEMENT_SURVIVAL"
    CONTRACT_COMPLIANCE = "CONTRACT_COMPLIANCE"

    # Layer 3: Artifact Quality
    NARRATIVE_FLOW = "NARRATIVE_FLOW"
    COGNITIVE_LOAD = "COGNITIVE_LOAD"
    INQUIRY_STRUCTURE = "INQUIRY_STRUCTURE"
    SCIENTIFIC_RIGOR = "SCIENTIFIC_RIGOR"
    STYLE_DESIGN = "STYLE_DESIGN"

    # Layer 4: Physical Rendered Quality
    READABILITY = "READABILITY"
    PHYSICAL_GEOMETRY = "PHYSICAL_GEOMETRY"
    VISUAL_DENSITY = "VISUAL_DENSITY"
    PAGE_BALANCE = "PAGE_BALANCE"


class QualityDimensionScore(BaseModel):
    """Score breakdown for an individual quality dimension."""
    model_config = ConfigDict(frozen=True)

    dimension: str
    score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    contributing_signals: Tuple[str, ...] = Field(default_factory=tuple)  # signal_ids
    findings: Tuple[str, ...] = Field(default_factory=tuple)              # finding_ids
    weight: float = Field(default=1.0, ge=0.0)
    rationale: str = ""
