"""
Universal Document Intelligence System V5 — Disagreement & Consensus Analyzer.

Phase 6: Multi-dimensional comparison of concurrent reviews.
No majority vote may ever override a safety invariant.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.review.contracts.enums import (
    AdjudicationOutcome,
    DisagreementType,
    ExpertDecisionType,
)
from app.review.contracts.review_decision import ReviewDecision


class DisagreementReport(BaseModel):
    """Detailed multi-dimensional breakdown of concordance across reviewers."""
    model_config = ConfigDict(frozen=True)

    agreement_score: float = Field(ge=0.0, le=1.0)
    disagreement_types: Tuple[DisagreementType, ...] = Field(default_factory=tuple)
    adjudication_outcome: AdjudicationOutcome
    safety_blocker_raised: bool = False
    explanation: str = ""


class DisagreementAnalyzer:
    """Evaluates concordance between two or more independent expert reviews."""

    @classmethod
    def analyze(
        cls,
        decisions: Sequence[ReviewDecision],
        has_safety_blocker: bool = False,
    ) -> DisagreementReport:
        """Compares review decisions across all epistemic dimensions."""
        if not decisions:
            return DisagreementReport(
                agreement_score=1.0,
                disagreement_types=(),
                adjudication_outcome=AdjudicationOutcome.INSUFFICIENT_EVIDENCE,
                explanation="No review decisions provided.",
            )

        if len(decisions) == 1:
            outcome = (
                AdjudicationOutcome.EXPERT_ADJUDICATION_REQUIRED
                if has_safety_blocker
                else AdjudicationOutcome.CONSENSUS
            )
            return DisagreementReport(
                agreement_score=1.0,
                disagreement_types=(),
                adjudication_outcome=outcome,
                safety_blocker_raised=has_safety_blocker,
                explanation="Single review decision recorded.",
            )

        disagreements: List[DisagreementType] = []

        # 1. Compare decision types
        types = {d.decision_type for d in decisions}
        if len(types) > 1:
            disagreements.append(DisagreementType.OBSERVATION_DISAGREEMENT)

        # 2. Compare root cause assessments
        root_causes = {d.root_cause_assessment for d in decisions if d.root_cause_assessment}
        if len(root_causes) > 1:
            disagreements.append(DisagreementType.ROOT_CAUSE_DISAGREEMENT)

        # 3. Compare directives
        directive_types_sets = [{dir_item.directive_type for dir_item in d.directives} for d in decisions]
        if len(directive_types_sets) > 1 and directive_types_sets[0] != directive_types_sets[1]:
            disagreements.append(DisagreementType.DIRECTIVE_DISAGREEMENT)

        # Compute simple concordant score across dimensions
        total_dimensions = 3
        concordant_count = total_dimensions - len(disagreements)
        score = max(0.0, concordant_count / float(total_dimensions))

        # Check safety blocker invariant
        if has_safety_blocker:
            outcome = AdjudicationOutcome.EXPERT_ADJUDICATION_REQUIRED
            expl = "Safety blocker active: Cannot resolve via simple consensus; expert adjudication required."
        elif score >= 0.80:
            outcome = AdjudicationOutcome.CONSENSUS
            expl = f"High concordance ({score:.2f}); consensus adopted."
        elif score >= 0.40:
            outcome = AdjudicationOutcome.SECOND_REVIEW_REQUIRED
            expl = f"Moderate variance ({score:.2f}) across {len(disagreements)} dimensions; second review required."
        else:
            outcome = AdjudicationOutcome.EXPERT_ADJUDICATION_REQUIRED
            expl = f"Significant divergence ({score:.2f}); senior expert adjudication required."

        return DisagreementReport(
            agreement_score=round(score, 3),
            disagreement_types=tuple(disagreements),
            adjudication_outcome=outcome,
            safety_blocker_raised=has_safety_blocker,
            explanation=expl,
        )
