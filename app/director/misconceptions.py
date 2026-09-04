"""
Misconception Engine & Conceptual Conflict Detector.

Detects high-value pedagogical opportunities to surface and correct common student misconceptions.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class MisconceptionOpportunity(BaseModel):
    """Identified student misconception opportunity for a given topic."""
    topic: str
    misconception_statement: str
    learner_likelihood: float = 0.8  # [0.0 - 1.0]
    conceptual_risk: str = "medium"
    correction_strategy: str = "counterexample_contrast"
    recommended_position: int = 2


KNOWN_MISCONCEPTIONS: list[MisconceptionOpportunity] = [
    MisconceptionOpportunity(
        topic="torque",
        misconception_statement="Greater applied force always produces greater rotational torque regardless of lever arm.",
        learner_likelihood=0.85,
        conceptual_risk="high",
        correction_strategy="lever_arm_counterexample",
        recommended_position=2,
    ),
    MisconceptionOpportunity(
        topic="gravity",
        misconception_statement="Heavier objects accelerate faster in free fall because gravity pulls harder on them.",
        learner_likelihood=0.90,
        conceptual_risk="high",
        correction_strategy="mass_inertia_cancellation",
        recommended_position=2,
    ),
    MisconceptionOpportunity(
        topic="correlation",
        misconception_statement="A strong statistical correlation between two variables proves a direct causal relationship.",
        learner_likelihood=0.75,
        conceptual_risk="medium",
        correction_strategy="confounding_factor_contrast",
        recommended_position=2,
    ),
    MisconceptionOpportunity(
        topic="research_hypothesis",
        misconception_statement="A scientific hypothesis is simply an educated guess without theoretical grounding.",
        learner_likelihood=0.70,
        conceptual_risk="medium",
        correction_strategy="falsifiability_grounding",
        recommended_position=2,
    ),
]


class MisconceptionDetector:
    """Discovers misconception opportunities for input topics and text."""

    @staticmethod
    def detect_for_topic(topic_text: str) -> MisconceptionOpportunity | None:
        text_lower = topic_text.lower()
        for misc in KNOWN_MISCONCEPTIONS:
            if misc.topic in text_lower:
                return misc
        return None
