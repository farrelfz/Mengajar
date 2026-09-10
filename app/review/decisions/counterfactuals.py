"""
Universal Document Intelligence System V5 — Counterfactual Reasoning Recorder.

Phase 6: Captures structured counterfactual statements explaining what condition
change would have prevented the failure or enabled export approval.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CounterfactualExplanation(BaseModel):
    """Structured counterfactual hypothesis."""
    model_config = ConfigDict(frozen=True)

    target_parameter: str
    observed_condition: str
    counterfactual_condition: str
    expected_outcome: str
    rationale: str

    def to_statement(self) -> str:
        return (
            f"If '{self.target_parameter}' was {self.counterfactual_condition} "
            f"instead of {self.observed_condition}, then {self.expected_outcome}. "
            f"Rationale: {self.rationale}"
        )
