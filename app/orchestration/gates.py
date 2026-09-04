"""
Production Quality Gates: Formal criteria evaluated across pipeline execution.
"""

from __future__ import annotations

from typing import Any
from app.orchestration.contracts import (
    GateDecisionEnum,
    ProductionGateResult,
    ProductionGateType,
    ProductionJobContext,
)


class ProductionGate:
    """Evaluates gates across workflow checkpoints."""

    @classmethod
    def evaluate_grounding_gate(cls, context: ProductionJobContext) -> ProductionGateResult:
        g_rep = context.shared_data.get("grounding_report")
        if not g_rep:
            return ProductionGateResult(
                gate_type=ProductionGateType.GROUNDING_GATE,
                decision=GateDecisionEnum.PASS,
                score=1.0,
                reasoning="Grounding evaluation not active for this job.",
            )

        if g_rep.claims_contradicted > 0:
            return ProductionGateResult(
                gate_type=ProductionGateType.GROUNDING_GATE,
                decision=GateDecisionEnum.BLOCK,
                score=g_rep.score.overall_score,
                threshold=0.75,
                reasoning=f"Grounding detected {g_rep.claims_contradicted} direct factual contradictions.",
                findings=[f.message for f in g_rep.findings if f.category == "contradiction"],
            )

        decision = GateDecisionEnum.PASS if g_rep.score.overall_score >= 0.70 else GateDecisionEnum.PASS_WITH_WARNINGS
        return ProductionGateResult(
            gate_type=ProductionGateType.GROUNDING_GATE,
            decision=decision,
            score=g_rep.score.overall_score,
            threshold=0.70,
            reasoning="Grounding score meets minimum threshold." if decision == GateDecisionEnum.PASS else "Grounding score below optimal threshold.",
        )
