"""
Universal Document Intelligence System V5 — Score Explainability Engine.

Phase 2C: Enforces full explainability for every quality score.
No opaque scores: every dimensional score must provide underlying signals,
expected baseline ranges, individual score impacts, and an actionable diagnostic summary.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.quality_contract import QualitySignalExplanation


class DimensionalScoreExplanation(BaseModel):
    """Full explainability record for a single quality dimension."""
    model_config = ConfigDict(frozen=True)

    dimension: str
    score: float
    signals: tuple[QualitySignalExplanation, ...] = Field(default_factory=tuple)
    summary: str
    is_acceptable: bool = True

    @classmethod
    def create(
        cls,
        dimension: str,
        score: float,
        signals: list[QualitySignalExplanation],
        summary: str,
    ) -> DimensionalScoreExplanation:
        return cls(
            dimension=dimension,
            score=round(max(0.0, min(1.0, score)), 3),
            signals=tuple(signals),
            summary=summary,
            is_acceptable=score >= 0.75,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "score": self.score,
            "signals": [
                {
                    "signal": s.signal,
                    "value": s.value,
                    "expected": s.expected,
                    "impact": s.impact,
                }
                for s in self.signals
            ],
            "summary": self.summary,
        }
