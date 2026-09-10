"""
Universal Document Intelligence System V5 — Repair Mutation Budget.

Phase 3C.1: Enforces artifact-specific mutation limits to prevent
over-aggressive destruction of content or structure in pursuit of higher quality scores.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field
from app.quality.repair.mutation_contract import RepairMutation, RepairMutationScope


class RepairMutationBudget(BaseModel):
    """Artifact-specific budget constraining allowed repair operations."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    max_iterations: int = 3
    max_total_mutations: int = 5
    max_local_token_mutations: int = 4
    max_component_mutations: int = 3
    max_page_composition_mutations: int = 2
    max_blueprint_regroupings: int = 1
    max_structural_mutations: int = 1
    max_content_reordering_ratio: float = 0.20
    max_element_removal_ratio: float = 0.05
    max_typography_delta_ratio: float = 0.25
    max_layout_replacement_ratio: float = 0.30
    max_semantic_mutations: int = 0
    max_claim_downgrades: int = 2


class MutationBudgetTracker:
    """Stateful tracker monitoring mutation consumption against an active budget."""

    def __init__(self, budget: RepairMutationBudget) -> None:
        self.budget = budget
        self.total_mutations = 0
        self.mutations_by_scope: Dict[RepairMutationScope, int] = {
            scope: 0 for scope in RepairMutationScope
        }
        self.claim_downgrades = 0
        self.element_removal_ratio = 0.0

    def can_consume(self, mutation: RepairMutation) -> Tuple[bool, Optional[str]]:
        """Checks whether applying the mutation would exceed budget limits."""
        if self.total_mutations >= self.budget.max_total_mutations:
            return False, f"Total mutation limit ({self.budget.max_total_mutations}) reached."

        scope = mutation.target_scope
        curr_scope_count = self.mutations_by_scope.get(scope, 0)

        if scope == RepairMutationScope.LEVEL_1_LOCAL_TOKEN:
            if curr_scope_count >= self.budget.max_local_token_mutations:
                return False, f"Local token mutation limit ({self.budget.max_local_token_mutations}) reached."

        elif scope == RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY:
            if curr_scope_count >= self.budget.max_component_mutations:
                return False, f"Component mutation limit ({self.budget.max_component_mutations}) reached."

        elif scope == RepairMutationScope.LEVEL_3_PAGE_COMPOSITION:
            if curr_scope_count >= self.budget.max_page_composition_mutations:
                return False, f"Page composition mutation limit ({self.budget.max_page_composition_mutations}) reached."

        elif scope == RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING:
            if curr_scope_count >= self.budget.max_blueprint_regroupings:
                return False, f"Blueprint regrouping limit ({self.budget.max_blueprint_regroupings}) reached."

        elif scope == RepairMutationScope.LEVEL_5_ARTIFACT_STRUCTURE:
            if curr_scope_count >= self.budget.max_structural_mutations:
                return False, f"Structural mutation limit ({self.budget.max_structural_mutations}) reached."

        elif scope == RepairMutationScope.LEVEL_6_MANUAL_REVIEW:
            return False, "Scope LEVEL_6_MANUAL_REVIEW cannot be automatically executed."

        # Specific operation checks
        if "downgrade_claim" in mutation.operation:
            if self.claim_downgrades >= self.budget.max_claim_downgrades:
                return False, f"Claim downgrade limit ({self.budget.max_claim_downgrades}) reached."

        return True, None

    def consume(self, mutation: RepairMutation) -> None:
        """Records the execution of an approved mutation."""
        self.total_mutations += 1
        self.mutations_by_scope[mutation.target_scope] = (
            self.mutations_by_scope.get(mutation.target_scope, 0) + 1
        )
        if "downgrade_claim" in mutation.operation:
            self.claim_downgrades += 1


def get_budget_for_artifact(artifact_type: str) -> RepairMutationBudget:
    """Factory creating canonical budgets per artifact format."""
    upper = artifact_type.upper()
    if upper == "PRESENTATION":
        return RepairMutationBudget(
            artifact_type="PRESENTATION",
            max_iterations=3,
            max_total_mutations=6,
            max_local_token_mutations=4,
            max_component_mutations=3,
            max_page_composition_mutations=3,
            max_blueprint_regroupings=2,   # Splitting dense slides is valid
            max_structural_mutations=1,
            max_element_removal_ratio=0.05,
        )
    elif upper == "HANDOUT":
        return RepairMutationBudget(
            artifact_type="HANDOUT",
            max_iterations=3,
            max_total_mutations=5,
            max_local_token_mutations=4,
            max_component_mutations=3,
            max_page_composition_mutations=2,
            max_blueprint_regroupings=1,
            max_structural_mutations=1,
            max_element_removal_ratio=0.03,
        )
    elif upper == "WORKSHEET":
        return RepairMutationBudget(
            artifact_type="WORKSHEET",
            max_iterations=3,
            max_total_mutations=4,
            max_local_token_mutations=3,
            max_component_mutations=2,
            max_page_composition_mutations=1,
            max_blueprint_regroupings=1,
            max_structural_mutations=1,
            max_element_removal_ratio=0.0,  # Zero content removal on worksheets
            max_semantic_mutations=0,
        )
    elif upper == "SCIENTIFIC_DOCUMENT":
        return RepairMutationBudget(
            artifact_type="SCIENTIFIC_DOCUMENT",
            max_iterations=3,
            max_total_mutations=4,
            max_local_token_mutations=3,
            max_component_mutations=2,
            max_page_composition_mutations=1,
            max_blueprint_regroupings=1,
            max_structural_mutations=1,
            max_claim_downgrades=2,
            max_element_removal_ratio=0.0,  # Never silently delete evidence!
            max_semantic_mutations=0,
        )
    return RepairMutationBudget(artifact_type=upper)
