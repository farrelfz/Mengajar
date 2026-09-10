"""
Universal Document Intelligence System V5 — Causal Intelligence Configuration.

Phase 3B: Centralized configuration parameters for correlation weights, thresholds,
causal confidence boundaries, ambiguity margins, and repair readiness policies.
"""

from __future__ import annotations

from typing import Dict
from pydantic import BaseModel, ConfigDict, Field


class CorrelationWeights(BaseModel):
    """Normalized weights across the 5 correlation proximity dimensions."""
    model_config = ConfigDict(frozen=True)

    spatial: float = 0.30
    structural: float = 0.25
    semantic: float = 0.15
    lineage: float = 0.15
    pattern: float = 0.15

    def total(self) -> float:
        return self.spatial + self.structural + self.semantic + self.lineage + self.pattern


class CausalConfidenceThresholds(BaseModel):
    """Categorical boundary scores for causal attribution certainty."""
    model_config = ConfigDict(frozen=True)

    very_high: float = 0.90
    high: float = 0.75
    medium: float = 0.55
    low: float = 0.35
    very_low: float = 0.20


class CausalIntelligenceConfig(BaseModel):
    """Centralized configuration for Phase 3B failure correlation and causal attribution."""
    model_config = ConfigDict(frozen=True)

    weights: CorrelationWeights = Field(default_factory=CorrelationWeights)
    confidence_thresholds: CausalConfidenceThresholds = Field(default_factory=CausalConfidenceThresholds)

    # Edge and cluster formation thresholds
    min_correlation_threshold: float = 0.60
    strong_correlation_threshold: float = 0.80

    # Competing hypothesis ambiguity boundary
    ambiguity_margin: float = 0.10

    # Evidence scoring parameters
    min_explanatory_coverage_for_high: float = 0.60
    max_contradiction_penalty: float = 0.40
    competition_penalty_rate: float = 0.15

    # Repair readiness limits
    deterministic_repair_min_confidence: float = 0.75
    high_risk_max_blast_radius: int = 5


# Singleton default configuration instance
DEFAULT_CAUSAL_CONFIG = CausalIntelligenceConfig()
