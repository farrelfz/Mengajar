"""
Universal Document Intelligence System V5 — Canonical Repair Mutation Contract.

Phase 3C.1: Hierarchical mutation scopes (Levels 0–6), mutation risk profiles,
and immutable mutation models guaranteeing minimal intervention.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field


class RepairMutationScope(str, Enum):
    """
    Canonical hierarchical repair scopes.
    The repair engine must ALWAYS prefer the LOWEST scope capable of resolving a defect.
    """
    LEVEL_0_NO_MUTATION = "LEVEL_0_NO_MUTATION"
    LEVEL_1_LOCAL_TOKEN = "LEVEL_1_LOCAL_TOKEN"
    LEVEL_2_COMPONENT_GEOMETRY = "LEVEL_2_COMPONENT_GEOMETRY"
    LEVEL_3_PAGE_COMPOSITION = "LEVEL_3_PAGE_COMPOSITION"
    LEVEL_4_BLUEPRINT_REGROUPING = "LEVEL_4_BLUEPRINT_REGROUPING"
    LEVEL_5_ARTIFACT_STRUCTURE = "LEVEL_5_ARTIFACT_STRUCTURE"
    LEVEL_6_MANUAL_REVIEW = "LEVEL_6_MANUAL_REVIEW"

    @property
    def rank(self) -> int:
        """Numerical rank from 0 (safest, lowest intervention) to 6 (highest intervention)."""
        ranks = {
            RepairMutationScope.LEVEL_0_NO_MUTATION: 0,
            RepairMutationScope.LEVEL_1_LOCAL_TOKEN: 1,
            RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY: 2,
            RepairMutationScope.LEVEL_3_PAGE_COMPOSITION: 3,
            RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING: 4,
            RepairMutationScope.LEVEL_5_ARTIFACT_STRUCTURE: 5,
            RepairMutationScope.LEVEL_6_MANUAL_REVIEW: 6,
        }
        return ranks[self]


class RepairMutationRisk(str, Enum):
    """Risk classification of an atomic repair mutation."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RepairMutation(BaseModel):
    """Immutable specification of a declared repair mutation."""
    model_config = ConfigDict(frozen=True)

    mutation_id: str
    artifact_type: str
    target_scope: RepairMutationScope
    target_ids: Tuple[str, ...]
    operation: str
    expected_quality_gain: float = Field(ge=0.0, le=1.0)
    mutation_cost: float = Field(ge=0.0)
    blast_radius: float = Field(ge=0.0, le=1.0)
    regression_risk: float = Field(ge=0.0, le=1.0)
    semantic_preservation_requirement: float = Field(default=0.85, ge=0.0, le=1.0)
    traceability_requirement: float = Field(default=1.0, ge=0.0, le=1.0)
    rollback_capability: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
