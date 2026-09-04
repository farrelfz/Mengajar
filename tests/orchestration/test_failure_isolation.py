"""
Unit tests for Failure Isolation and classification.
"""

import pytest
from app.orchestration.contracts import FailureCategory, FailureSeverity
from app.orchestration.failures import FailureIsolationManager


def test_failure_isolation_manager_classifies_exceptions():
    f_input = FailureIsolationManager.classify_exception("validation", ValueError("empty input provided"))
    assert f_input.category == FailureCategory.INPUT
    assert f_input.severity == FailureSeverity.FATAL
    assert f_input.retryable is False

    f_render = FailureIsolationManager.classify_exception("rendering", TimeoutError("Playwright render timed out"))
    assert f_render.category == FailureCategory.RENDERING
    assert f_render.severity == FailureSeverity.RECOVERABLE
    assert f_render.retryable is True
