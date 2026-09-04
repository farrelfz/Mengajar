"""
Unit tests for CriticPanel dispatch, execution filtering, and failure isolation.
"""

import pytest

from app.critic.base import BaseCritic
from app.critic.context import CritiqueContext, CritiqueContextBuilder
from app.critic.contracts import (
    CritiqueConfidence,
    CritiqueFinding,
    CritiquePerspective,
    CritiqueSeverity,
)
from app.critic.panel import CriticPanel
from app.critic.registry import CriticRegistry


class MockPassingCritic(BaseCritic):
    @property
    def critic_id(self) -> str:
        return "mock_pass"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.STRUCTURAL

    def can_critique(self, context: CritiqueContext) -> bool:
        return True

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        return [
            CritiqueFinding(
                id="f_pass",
                perspective=self.perspective,
                title="Mock Passing Finding",
                observation="Observation",
                diagnosis="Diagnosis",
                why_it_matters="Matters",
                severity=CritiqueSeverity.LOW,
                confidence=CritiqueConfidence.HIGH,
                improvement_direction="None",
            )
        ]


class MockFailingCritic(BaseCritic):
    @property
    def critic_id(self) -> str:
        return "mock_fail"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.SCIENTIFIC_RIGOR

    def can_critique(self, context: CritiqueContext) -> bool:
        return True

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        raise RuntimeError("Simulated internal critic failure")


def test_critic_panel_fault_isolation():
    reg = CriticRegistry()
    reg.register(MockPassingCritic())
    reg.register(MockFailingCritic())

    panel = CriticPanel(registry=reg)
    ctx = CritiqueContextBuilder("job_panel_test").build()

    findings, trace = panel.execute_critique(ctx)

    # Passing critic should succeed and produce findings
    assert len(findings) == 1
    assert findings[0].id == "f_pass"

    # Trace should log execution and failure without blowing up execution
    assert "mock_pass" in trace.critics_executed
    assert "mock_fail" in trace.critics_failed
