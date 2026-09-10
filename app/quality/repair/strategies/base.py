"""
Universal Document Intelligence System V5 — Base Repair Strategy.

Phase 3B: Abstract base class for deterministic repair strategies across all artifact types.
"""

from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.quality.repair.contracts import (
    RepairAction,
    RepairMutationClass,
    RepairPlan,
    RepairRiskLevel,
    RepairTarget,
)
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType


class RepairStrategy(abc.ABC):
    """Abstract base class for all deterministic artifact repair strategies."""

    def __init__(
        self,
        strategy_id: str,
        name: str,
        supported_artifact_types: Sequence[str],
        supported_failure_codes: Sequence[str],
        supported_root_causes: Sequence[RootCauseType],
        mutation_class: RepairMutationClass,
        priority: int = 1,
        risk_level: RepairRiskLevel = RepairRiskLevel.LOW,
        mutation_cost: float = 0.1,
        causal_reach: Optional[Any] = None,
        owning_layer: Optional[str] = None,
        expected_finding_classes: Sequence[str] = (),
        expected_quality_dimensions: Sequence[str] = (),
    ) -> None:
        from app.quality.repair.effectiveness.causal_reach import CausalReach
        self.strategy_id = strategy_id
        self.name = name
        self.supported_artifact_types = tuple(a.upper() for a in supported_artifact_types)
        self.supported_failure_codes = tuple(supported_failure_codes)
        self.supported_root_causes = tuple(supported_root_causes)
        self.mutation_class = mutation_class
        self.priority = priority
        self.risk_level = risk_level
        self.mutation_cost = mutation_cost

        # Default reach and owning layer resolution
        if causal_reach is not None:
            self.causal_reach = causal_reach
        elif mutation_class == RepairMutationClass.CLASS_A_GEOMETRY:
            self.causal_reach = CausalReach.LOCAL_RENDER_GEOMETRY
        elif mutation_class == RepairMutationClass.CLASS_C_LAYOUT_REMAPPING:
            self.causal_reach = CausalReach.COMPONENT_SPATIAL_STRUCTURE
        elif mutation_class == RepairMutationClass.CLASS_B_COMPOSITION:
            self.causal_reach = CausalReach.PAGE_COMPOSITION
        elif mutation_class == RepairMutationClass.CLASS_D_PEDAGOGICAL_STRUCTURE:
            self.causal_reach = CausalReach.PEDAGOGICAL_STRUCTURE
        elif mutation_class == RepairMutationClass.CLASS_E_SEMANTIC_INTEGRITY:
            self.causal_reach = CausalReach.SEMANTIC_INTEGRITY
        else:
            self.causal_reach = CausalReach.LOCAL_RENDER_GEOMETRY

        if owning_layer is not None:
            self.owning_layer = owning_layer
        elif self.causal_reach == CausalReach.LOCAL_RENDER_GEOMETRY:
            self.owning_layer = "R0"
        elif self.causal_reach == CausalReach.COMPONENT_SPATIAL_STRUCTURE:
            self.owning_layer = "R1"
        elif self.causal_reach == CausalReach.PAGE_COMPOSITION:
            self.owning_layer = "R2"
        else:
            self.owning_layer = "R3"

        self.expected_finding_classes = tuple(expected_finding_classes)
        self.expected_quality_dimensions = tuple(expected_quality_dimensions)

    def supports(self, artifact_type: str, failure_code: str, root_cause: RootCauseType) -> bool:
        art_match = artifact_type.upper() in self.supported_artifact_types or "ALL" in self.supported_artifact_types
        code_match = failure_code in self.supported_failure_codes or "*" in self.supported_failure_codes
        cause_match = root_cause in self.supported_root_causes
        return art_match and code_match and cause_match

    @abc.abstractmethod
    def check_preconditions(
        self,
        blueprint: Any,
        target: RepairTarget,
        hypothesis: RootCauseHypothesis,
    ) -> bool:
        """Returns True if this strategy is valid and safe to apply to the target."""
        pass

    @abc.abstractmethod
    def plan_repair(
        self,
        blueprint: Any,
        target: RepairTarget,
        hypothesis: RootCauseHypothesis,
    ) -> RepairPlan:
        """Constructs the immutable RepairPlan detailing actions to perform."""
        pass

    @abc.abstractmethod
    def apply_repair(
        self,
        blueprint: Any,
        plan: RepairPlan,
    ) -> Tuple[Any, List[RepairAction]]:
        """Executes the planned mutation on a copy of the blueprint, returning mutated blueprint and applied actions."""
        pass

    def check_postconditions(
        self,
        blueprint: Any,
        target: RepairTarget,
    ) -> bool:
        """Verifies that the mutation achieved expected structural invariants."""
        return True
