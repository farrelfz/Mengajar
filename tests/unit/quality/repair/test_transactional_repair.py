"""Unit tests for Transactional Repair Manager and Atomic Rollback."""

import pytest
from app.quality.contracts.decisions import ExportDecision, UnifiedQualityDecision
from app.quality.contracts.findings import QualityFinding
from app.quality.contracts.signals import QualityDomain, SignalSeverity
from app.quality.repair.contracts import RepairTarget
from app.quality.repair.mutation_contract import RepairMutationScope
from app.quality.repair.mutation_budget import MutationBudgetTracker, get_budget_for_artifact
from app.quality.repair.planner import CandidateRepairOption
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType
from app.quality.repair.strategies.presentation import PresentationPaddingAdjustmentStrategy
from app.quality.repair.transaction import RepairTransactionManager


class MockSlide:
    def __init__(self, slide_id, title, content, refs):
        self.slide_id = slide_id
        self.title = title
        self.content = content
        self.source_refs = refs
        self.text_density = "normal"


class MockDeck:
    def __init__(self, slides):
        self.slides = slides


def test_transaction_commits_clean_repair():
    """A clean repair improving quality without regressions commits successfully."""
    deck = MockDeck([MockSlide("s1", "Title", "Content", ["ref1"])])
    target = RepairTarget(artifact_type="PRESENTATION", element_id="s1", slide_index=1)
    hyp = RootCauseHypothesis(
        root_cause_id="rc1",
        cause_type=RootCauseType.PADDING_SPACING,
        confidence=0.9,
        affected_targets=(target,),
        supporting_findings=(
            QualityFinding(failure_code="MARGIN_VIOLATION", domain=QualityDomain.RENDERED, severity=SignalSeverity.MAJOR),
        ),
    )
    cand = CandidateRepairOption(
        strategy_id="presentation_padding_adjust",
        target=target,
        hypothesis=hyp,
        mutation_scope=RepairMutationScope.LEVEL_1_LOCAL_TOKEN,
        utility_score=15.0,
        expected_quality_gain=0.15,
        mutation_cost=0.1,
        blast_radius=0.1,
        regression_risk=0.05,
        is_budget_approved=True,
    )
    budget = MutationBudgetTracker(get_budget_for_artifact("PRESENTATION"))
    init_dec = UnifiedQualityDecision(
        decision=ExportDecision.REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        manual_review_required=False,
        hard_blockers=("MARGIN_VIOLATION",),
        warnings=(),
        rationale="Repair required due to margin violation",
    )

    strategy = PresentationPaddingAdjustmentStrategy()
    res_bp, rec, was_committed = RepairTransactionManager.execute_transaction(
        current_blueprint=deck,
        candidate=cand,
        strategy=strategy,
        budget_tracker=budget,
        current_decision=init_dec,
        current_score=0.70,
        artifact_type="PRESENTATION",
        iteration=1,
    )

    assert was_committed is True
    assert rec.is_committed is True
    assert res_bp.slides[0].text_density == "compact"
