"""
Unit tests for deterministic Retry Policies.
"""

import pytest
from app.orchestration.contracts import FailureCategory, FailureSeverity, ProductionFailure
from app.orchestration.retry import RetryPolicy, RetryStrategy


def test_retry_policy_retries_recoverable_rendering_failure():
    policy = RetryPolicy(max_attempts=3, strategy=RetryStrategy.IMMEDIATE)
    failure = ProductionFailure(
        stage_id="rendering",
        category=FailureCategory.RENDERING,
        severity=FailureSeverity.RECOVERABLE,
        message="Transient render glitch",
        retryable=True,
    )

    dec = policy.evaluate_retry(failure, current_attempt=1)
    assert dec.should_retry is True
    assert dec.attempt == 2


def test_retry_policy_rejects_fatal_input_failure():
    policy = RetryPolicy(max_attempts=3)
    failure = ProductionFailure(
        stage_id="validation",
        category=FailureCategory.INPUT,
        severity=FailureSeverity.FATAL,
        message="Invalid raw input",
        retryable=False,
    )

    dec = policy.evaluate_retry(failure, current_attempt=1)
    assert dec.should_retry is False
