"""
Critic Panel orchestrating parallel execution with fault isolation.
"""

from __future__ import annotations

import logging
from typing import Any
from app.critic.base import BaseCritic
from app.critic.context import CritiqueContext
from app.critic.contracts import CritiqueFinding, CritiqueTrace
from app.critic.registry import CriticRegistry

logger = logging.getLogger(__name__)


class CriticPanel:
    """Dispatches available critics across the artifact context with failure isolation."""

    def __init__(self, registry: CriticRegistry | None = None) -> None:
        self.registry = registry or CriticRegistry()

    def execute_critique(
        self,
        context: CritiqueContext,
        selected_critics: list[str] | None = None,
    ) -> tuple[list[CritiqueFinding], CritiqueTrace]:
        all_findings: list[CritiqueFinding] = []
        executed: list[str] = []
        skipped: list[str] = []
        failed: list[str] = []
        reasoning_steps: list[str] = []

        available_critics = self.registry.get_all()

        for critic in available_critics:
            if selected_critics and critic.critic_id not in selected_critics:
                skipped.append(critic.critic_id)
                continue

            try:
                if not critic.can_critique(context):
                    skipped.append(critic.critic_id)
                    reasoning_steps.append(f"Critic '{critic.critic_id}' skipped: insufficient context evidence.")
                    continue

                findings = critic.critique(context)
                all_findings.extend(findings)
                executed.append(critic.critic_id)
                reasoning_steps.append(f"Critic '{critic.critic_id}' produced {len(findings)} findings.")
            except Exception as e:
                logger.exception("Critic '%s' failed during execution: %s", critic.critic_id, e)
                failed.append(critic.critic_id)
                reasoning_steps.append(f"Critic '{critic.critic_id}' raised exception: {str(e)}")

        trace = CritiqueTrace(
            critics_executed=executed,
            critics_skipped=skipped,
            critics_failed=failed,
            evidence_sources=context.available_evidence_sources(),
            reasoning_steps=reasoning_steps,
        )

        return all_findings, trace
