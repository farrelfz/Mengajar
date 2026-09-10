"""Unit tests for Repair Mutation Contracts and Artifact-Specific Budgets."""

import pytest
from app.quality.repair.mutation_contract import (
    RepairMutation,
    RepairMutationRisk,
    RepairMutationScope,
)
from app.quality.repair.mutation_budget import (
    MutationBudgetTracker,
    RepairMutationBudget,
    get_budget_for_artifact,
)


def test_mutation_scope_hierarchy_ranks():
    """Verifies that mutation scopes have strictly monotonic hierarchical ranks."""
    assert RepairMutationScope.LEVEL_0_NO_MUTATION.rank == 0
    assert RepairMutationScope.LEVEL_1_LOCAL_TOKEN.rank == 1
    assert RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY.rank == 2
    assert RepairMutationScope.LEVEL_3_PAGE_COMPOSITION.rank == 3
    assert RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING.rank == 4
    assert RepairMutationScope.LEVEL_5_ARTIFACT_STRUCTURE.rank == 5
    assert RepairMutationScope.LEVEL_6_MANUAL_REVIEW.rank == 6


def test_artifact_specific_budget_limits():
    """Verifies that format-specific budgets enforce differentiated tolerances."""
    pres_budget = get_budget_for_artifact("PRESENTATION")
    sci_budget = get_budget_for_artifact("SCIENTIFIC_DOCUMENT")
    ws_budget = get_budget_for_artifact("WORKSHEET")

    # Presentation allows slide regroupings (split dense slides)
    assert pres_budget.max_blueprint_regroupings == 2
    # Scientific restricts claim downgrades and forbids element removal
    assert sci_budget.max_claim_downgrades == 2
    assert sci_budget.max_element_removal_ratio == 0.0
    # Worksheet strictly forbids content deletion
    assert ws_budget.max_element_removal_ratio == 0.0


def test_budget_tracker_enforces_maximum_mutations():
    """Verifies that exceeding total mutations blocks further execution."""
    budget = RepairMutationBudget(
        artifact_type="TEST",
        max_total_mutations=2,
        max_local_token_mutations=2,
    )
    tracker = MutationBudgetTracker(budget)

    mutation = RepairMutation(
        mutation_id="mut_1",
        artifact_type="TEST",
        target_scope=RepairMutationScope.LEVEL_1_LOCAL_TOKEN,
        target_ids=("el_1",),
        operation="adjust_padding",
        expected_quality_gain=0.10,
        mutation_cost=0.1,
        blast_radius=0.1,
        regression_risk=0.05,
    )

    can_1, _ = tracker.can_consume(mutation)
    assert can_1 is True
    tracker.consume(mutation)

    can_2, _ = tracker.can_consume(mutation)
    assert can_2 is True
    tracker.consume(mutation)

    # 3rd mutation exceeds max_total_mutations=2
    can_3, reason = tracker.can_consume(mutation)
    assert can_3 is False
    assert "Total mutation limit (2) reached" in reason


def test_budget_blocks_unauthorized_scope_overflow():
    """Verifies that exceeding a specific scope limit blocks even if total budget remains."""
    budget = RepairMutationBudget(
        artifact_type="TEST",
        max_total_mutations=5,
        max_blueprint_regroupings=1,
    )
    tracker = MutationBudgetTracker(budget)

    split_mut = RepairMutation(
        mutation_id="split_1",
        artifact_type="TEST",
        target_scope=RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING,
        target_ids=("slide_1",),
        operation="split_slide",
        expected_quality_gain=0.20,
        mutation_cost=0.5,
        blast_radius=0.4,
        regression_risk=0.15,
    )

    can_1, _ = tracker.can_consume(split_mut)
    assert can_1 is True
    tracker.consume(split_mut)

    # Second split is blocked by max_blueprint_regroupings=1
    can_2, reason = tracker.can_consume(split_mut)
    assert can_2 is False
    assert "Blueprint regrouping limit (1) reached" in reason
