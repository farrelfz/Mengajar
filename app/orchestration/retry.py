"""
Retry Policies: Deterministic retry behavior and backoff strategies.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel
from app.orchestration.contracts import FailureCategory, FailureSeverity, ProductionFailure


class RetryStrategy(str, Enum):
    NO_RETRY = "no_retry"
    IMMEDIATE = "immediate"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


class RetryDecision(BaseModel):
    should_retry: bool
    attempt: int
    delay_ms: float
    reason: str


class RetryPolicy(BaseModel):
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.IMMEDIATE
    base_delay_ms: float = 100.0
    retryable_categories: list[FailureCategory] = [
        FailureCategory.RENDERING,
        FailureCategory.TIMEOUT,
        FailureCategory.INTERNAL,
    ]

    def evaluate_retry(self, failure: ProductionFailure, current_attempt: int) -> RetryDecision:
        if not failure.retryable or failure.severity == FailureSeverity.FATAL:
            return RetryDecision(
                should_retry=False,
                attempt=current_attempt,
                delay_ms=0.0,
                reason="Failure is marked non-retryable or fatal.",
            )

        if failure.category not in self.retryable_categories:
            return RetryDecision(
                should_retry=False,
                attempt=current_attempt,
                delay_ms=0.0,
                reason=f"Failure category '{failure.category.value}' is not configured for retry.",
            )

        if current_attempt >= self.max_attempts:
            return RetryDecision(
                should_retry=False,
                attempt=current_attempt,
                delay_ms=0.0,
                reason=f"Exceeded maximum retry attempts ({self.max_attempts}).",
            )

        # Calculate delay
        if self.strategy == RetryStrategy.IMMEDIATE:
            delay = 0.0
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.base_delay_ms * current_attempt
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.base_delay_ms * (2 ** (current_attempt - 1))
        else:
            delay = 0.0

        return RetryDecision(
            should_retry=True,
            attempt=current_attempt + 1,
            delay_ms=delay,
            reason=f"Retrying stage (attempt {current_attempt + 1}/{self.max_attempts}).",
        )
