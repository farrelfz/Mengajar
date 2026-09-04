"""
Conditional Routing: Centralized policy rules determining dynamic DAG transitions.
"""

from __future__ import annotations

from typing import Any, Callable
from pydantic import BaseModel
from app.orchestration.contracts import ProductionJobContext


class RoutingDecision(BaseModel):
    decision_name: str
    target_stage: str | None
    should_divert: bool = False
    reasoning: str = ""


class RoutingRule(BaseModel):
    name: str
    source_stage: str
    predicate: str  # Description of condition
    target_stage: str


class ConditionalRouter:
    """Evaluates contextual state to determine next dynamic workflow stage."""

    @classmethod
    def evaluate_quality_routing(cls, context: ProductionJobContext) -> RoutingDecision:
        q_rep = context.shared_data.get("quality_report")
        if not q_rep:
            return RoutingDecision(decision_name="quality_absent", target_stage=None, reasoning="No quality report")

        score_val = getattr(q_rep, "overall_score", 0.0)
        can_proceed = q_rep.gate_result.can_proceed if hasattr(q_rep, "gate_result") else True

        if can_proceed:
            return RoutingDecision(
                decision_name="quality_pass",
                target_stage="rendering",
                should_divert=False,
                reasoning=f"Quality passed with score {score_val:.2f}",
            )
        else:
            return RoutingDecision(
                decision_name="quality_fail_refine",
                target_stage="critic_review",
                should_divert=True,
                reasoning=f"Quality rejected (score {score_val:.2f}) -> divert to critic & refinement",
            )

    @classmethod
    def evaluate_grounding_routing(cls, context: ProductionJobContext) -> RoutingDecision:
        g_rep = context.shared_data.get("grounding_report")
        if not g_rep:
            return RoutingDecision(decision_name="grounding_absent", target_stage=None, reasoning="No grounding report")

        if g_rep.claims_contradicted > 0:
            return RoutingDecision(
                decision_name="grounding_contradicted",
                target_stage=None,
                should_divert=True,
                reasoning=f"Grounding detected {g_rep.claims_contradicted} contradictions",
            )

        return RoutingDecision(
            decision_name="grounding_pass",
            target_stage="blueprint_generation",
            should_divert=False,
            reasoning=f"Grounding passed with overall score {g_rep.score.overall_score:.2f}",
        )
