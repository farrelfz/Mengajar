"""
Universal Document Intelligence System V5 — Competing Hypothesis Analysis.

Phase 3B: Evaluates competing root cause hypotheses, detects causal ambiguity,
and determines authoritative CausalDecision states without discarding alternatives.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from app.quality.causal.causal_taxonomy import CausalDecision
from app.quality.causal.config import CausalIntelligenceConfig, DEFAULT_CAUSAL_CONFIG
from app.quality.causal.contracts import RootCauseHypothesis


class CompetingHypothesisAnalysisResult:
    """Outcome of evaluating competing causal hypotheses for a failure cluster."""

    def __init__(
        self,
        primary_hypothesis: Optional[RootCauseHypothesis],
        alternative_hypotheses: Tuple[RootCauseHypothesis, ...],
        decision: CausalDecision,
        is_ambiguous: bool,
        rationale: str,
    ):
        self.primary_hypothesis = primary_hypothesis
        self.alternative_hypotheses = alternative_hypotheses
        self.decision = decision
        self.is_ambiguous = is_ambiguous
        self.rationale = rationale

    @property
    def winning_hypothesis(self) -> Optional[RootCauseHypothesis]:
        return self.primary_hypothesis

    @property
    def all_hypotheses(self) -> Tuple[RootCauseHypothesis, ...]:
        if self.primary_hypothesis:
            return (self.primary_hypothesis,) + self.alternative_hypotheses
        return ()

    @property
    def top_hypotheses_delta(self) -> float:
        if self.primary_hypothesis and self.alternative_hypotheses:
            return self.primary_hypothesis.confidence_score - self.alternative_hypotheses[0].confidence_score
        return 1.0

    @property
    def ambiguity_score(self) -> float:
        if not self.primary_hypothesis or not self.alternative_hypotheses:
            return 0.0
        delta = self.top_hypotheses_delta
        return max(0.0, 1.0 - (delta / 0.20)) if delta < 0.20 else 0.0


CompetingAnalysisResult = CompetingHypothesisAnalysisResult


class CompetingHypothesisAnalyzer:
    """Analyzes differences between top hypotheses to detect ambiguity and assign CausalDecision."""

    def __init__(self, config: Optional[CausalIntelligenceConfig] = None):
        self.config = config or DEFAULT_CAUSAL_CONFIG

    def analyze(
        self,
        hypotheses: Sequence[RootCauseHypothesis],
    ) -> CompetingHypothesisAnalysisResult:
        """Evaluates competing candidates and renders an authoritative CausalDecision."""
        if not hypotheses:
            return CompetingHypothesisAnalysisResult(
                primary_hypothesis=None,
                alternative_hypotheses=(),
                decision=CausalDecision.INSUFFICIENT_EVIDENCE,
                is_ambiguous=False,
                rationale="No causal hypotheses were generated for this defect pattern.",
            )

        sorted_hyps = sorted(hypotheses, key=lambda h: h.confidence_score, reverse=True)
        top = sorted_hyps[0]
        alternatives = tuple(sorted_hyps[1:])

        # Check for insufficient evidence
        if top.confidence_score < self.config.confidence_thresholds.low:
            return CompetingHypothesisAnalysisResult(
                primary_hypothesis=top,
                alternative_hypotheses=alternatives,
                decision=CausalDecision.INSUFFICIENT_EVIDENCE,
                is_ambiguous=False,
                rationale=f"Top hypothesis confidence {top.confidence_score:.2f} is below minimum threshold (0.35).",
            )

        # Check for multiple competing hypotheses
        if len(sorted_hyps) >= 2:
            runner_up = sorted_hyps[1]
            delta = top.confidence_score - runner_up.confidence_score

            if delta <= self.config.ambiguity_margin:
                msg = (
                    f"Ambiguous root cause: Top hypothesis '{top.cause_code}' ({top.confidence_score:.2f}) "
                    f"and runner-up '{runner_up.cause_code}' ({runner_up.confidence_score:.2f}) "
                    f"differ by {delta:.2f} <= margin ({self.config.ambiguity_margin:.2f})."
                )
                return CompetingHypothesisAnalysisResult(
                    primary_hypothesis=top,
                    alternative_hypotheses=alternatives,
                    decision=CausalDecision.MULTIPLE_PLAUSIBLE_CAUSES,
                    is_ambiguous=True,
                    rationale=msg,
                )

        # Single dominant cause
        if top.confidence_score >= 0.85:
            decision = CausalDecision.ROOT_CAUSE_CONFIRMED
            msg = f"Root cause '{top.cause_code}' confirmed with high confidence ({top.confidence_score:.2f})."
        else:
            decision = CausalDecision.ROOT_CAUSE_LIKELY
            msg = f"Root cause '{top.cause_code}' is likely ({top.confidence_score:.2f})."

        return CompetingHypothesisAnalysisResult(
            primary_hypothesis=top,
            alternative_hypotheses=alternatives,
            decision=decision,
            is_ambiguous=False,
            rationale=msg,
        )
