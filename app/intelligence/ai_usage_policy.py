"""
Central AI Usage Policy and Budget Tracker.

Tracks API requests, latencies, tokens, and justifies LLM escalation.
Enforces the principle: 'Never call AI when the answer is in the structure or rules'.
"""

from __future__ import annotations

import time
from typing import Any
from pydantic import BaseModel, Field


class APICallRecord(BaseModel):
    task_name: str
    purpose: str
    model: str
    latency_seconds: float
    input_items_count: int
    output_items_count: int
    success: bool
    error: str | None = None


class AIUsageMetrics(BaseModel):
    """Execution telemetry for AI and Local processing balance."""
    total_blocks_processed: int = 0
    locally_classified_blocks: int = 0
    ai_escalated_blocks: int = 0
    total_api_calls: int = 0
    selective_reasoning_calls: int = 0
    presentation_architecture_calls: int = 0
    visual_reasoning_calls: int = 0
    total_latency_seconds: float = 0.0
    local_processing_ratio: float = 1.0
    api_records: list[APICallRecord] = Field(default_factory=list)

    def calculate_ratio(self) -> float:
        if self.total_blocks_processed > 0:
            self.local_processing_ratio = round(
                self.locally_classified_blocks / self.total_blocks_processed, 3
            )
        else:
            self.local_processing_ratio = 1.0
        return self.local_processing_ratio


class AIUsagePolicy:
    """Orchestrates AI invocation decisions and monitors usage."""

    def __init__(self, escalation_threshold: float = 0.70) -> None:
        self.escalation_threshold = escalation_threshold
        self.metrics = AIUsageMetrics()

    def should_escalate_classification(self, confidence: float) -> bool:
        """Rule: Only escalate if confidence is strictly below threshold."""
        return confidence < self.escalation_threshold

    def record_call(
        self,
        task_name: str,
        purpose: str,
        model: str,
        latency: float,
        input_count: int,
        output_count: int,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Record an API invocation in the central telemetry log."""
        record = APICallRecord(
            task_name=task_name,
            purpose=purpose,
            model=model,
            latency_seconds=round(latency, 3),
            input_items_count=input_count,
            output_items_count=output_count,
            success=success,
            error=error,
        )
        self.metrics.api_records.append(record)
        self.metrics.total_api_calls += 1
        self.metrics.total_latency_seconds = round(
            self.metrics.total_latency_seconds + latency, 3
        )

        if "selective" in task_name.lower():
            self.metrics.selective_reasoning_calls += 1
        elif "architect" in task_name.lower() or "presentation" in task_name.lower():
            self.metrics.presentation_architecture_calls += 1
        elif "visual" in task_name.lower():
            self.metrics.visual_reasoning_calls += 1
