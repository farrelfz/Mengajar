"""Unit tests for Minimal Intervention Repair Planner and Utility Ranking."""

import pytest
from app.quality.contracts.findings import QualityFinding
from app.quality.contracts.signals import QualityDomain, SignalSeverity
from app.quality.repair.contracts import RepairTarget
from app.quality.repair.mutation_contract import RepairMutationScope
from app.quality.repair.mutation_budget import MutationBudgetTracker, get_budget_for_artifact
from app.quality.repair.planner import MinimalInterventionRepairPlanner
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType
from app.quality.repair.strategies.presentation import (
    PresentationDensitySplitStrategy,
    PresentationLayoutRemapStrategy,
    PresentationPaddingAdjustmentStrategy,
)


class MockSlide:
    def __init__(self, slide_id, title, content, refs):
        self.slide_id = slide_id
        self.title = title
        self.content = content
        self.source_refs = refs
        self.layout = "two_column"
        self.key_blocks = refs


class MockDeck:
    def __init__(self, slides):
        self.slides = slides


def test_utility_formula_calculation():
    """Verifies that low-cost, low-blast-radius strategies achieve higher utility."""
    # Low cost (0.1), low blast radius (0.1), low risk (0.05) -> High utility
    u_high = MinimalInterventionRepairPlanner.calculate_utility(
        expected_quality_gain=0.15,
        strategy_confidence=0.90,
        root_cause_confidence=0.90,
        mutation_cost=0.10,
        blast_radius=0.10,
        regression_risk=0.05,
    )

    # High cost (0.6), high blast radius (0.6), high risk (0.35) -> Low utility
    u_low = MinimalInterventionRepairPlanner.calculate_utility(
        expected_quality_gain=0.15,
        strategy_confidence=0.90,
        root_cause_confidence=0.90,
        mutation_cost=0.60,
        blast_radius=0.60,
        regression_risk=0.35,
    )

    assert u_high > u_low
    assert u_high > 10.0


def test_planner_prefers_minimal_intervention_scope():
    """
    Given both a Level 1 padding adjustment and a Level 4 slide split,
    the planner must prefer Level 1 minimal intervention.
    """
    deck = MockDeck([
        MockSlide("s1", "Title", "A" * 250, ["u1", "u2", "u3"])
    ])
    target = RepairTarget(
        artifact_type="PRESENTATION",
        element_id="s1",
        slide_index=1,
    )
    hypothesis = RootCauseHypothesis(
        root_cause_id="rc_1",
        cause_type=RootCauseType.CONTENT_DENSITY,
        confidence=0.90,
        affected_targets=(target,),
        supporting_findings=(
            QualityFinding(
                failure_code="TEXT_CLIPPING",
                domain=QualityDomain.RENDERED,
                severity=SignalSeverity.MAJOR,
            ),
        ),
    )

    budget_tracker = MutationBudgetTracker(get_budget_for_artifact("PRESENTATION"))

    strategies = [
        PresentationDensitySplitStrategy(),       # Level 4
        PresentationPaddingAdjustmentStrategy(),   # Level 1
    ]

    candidates = MinimalInterventionRepairPlanner.evaluate_candidates(
        strategies=strategies,
        target=target,
        hypothesis=hypothesis,
        budget_tracker=budget_tracker,
        blueprint=deck,
    )

    assert len(candidates) >= 2
    # The top-ranked option must have LOWER mutation scope rank (Level 1 < Level 4)
    top_option = candidates[0]
    assert top_option.mutation_scope == RepairMutationScope.LEVEL_1_LOCAL_TOKEN
    assert top_option.strategy_id == "presentation_padding_adjust"
