"""
Unit tests for Acceptance Policy and Improvement Judge decisions.
"""

import pytest
from app.refinement.contracts import (
    ImprovementComparison,
    ImprovementDecision,
    InvariantCategory,
    InvariantViolation,
)
from app.refinement.decision import ImprovementJudge


def test_judge_accepts_clean_improvement():
    comp = ImprovementComparison(
        iteration=1,
        baseline_quality_score=0.75,
        candidate_quality_score=0.88,
        quality_delta=0.13,
        baseline_findings_count=2,
        candidate_findings_count=0,
        resolved_finding_ids=["f1", "f2"],
        is_meaningful_improvement=True,
    )
    decision = ImprovementJudge.judge(comp)
    assert decision == ImprovementDecision.ACCEPT


def test_judge_rejects_candidate_with_invariant_violation():
    comp = ImprovementComparison(
        iteration=1,
        baseline_quality_score=0.75,
        candidate_quality_score=0.92,
        quality_delta=0.17,
        baseline_findings_count=2,
        candidate_findings_count=0,
        resolved_finding_ids=["f1", "f2"],
        invariant_violations=[
            InvariantViolation(
                category=InvariantCategory.SEMANTIC_INVARIANT,
                invariant_name="learning_objectives_preserved",
                description="Objective deleted",
            )
        ],
        is_meaningful_improvement=False,
    )
    decision = ImprovementJudge.judge(comp)
    assert decision == ImprovementDecision.REJECT


def test_judge_rejects_candidate_with_new_regressions():
    comp = ImprovementComparison(
        iteration=1,
        baseline_quality_score=0.75,
        candidate_quality_score=0.78,
        quality_delta=0.03,
        baseline_findings_count=1,
        candidate_findings_count=2,
        resolved_finding_ids=["f1"],
        new_regressions=["new_reg_critical"],
        is_meaningful_improvement=False,
    )
    decision = ImprovementJudge.judge(comp)
    assert decision == ImprovementDecision.REJECT
