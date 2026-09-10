"""
Universal Document Intelligence System V5 — Canonical Repair Actuation Contracts.

Phase 4: Defines authoritative request/result data contracts and the RepairActuator
protocol to transform repair from descriptive planning to executable artifact mutation.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Protocol, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.repair.actuation.mutation_layers import TransformationLayer
from app.quality.repair.effectiveness.causal_reach import CausalReach
from app.quality.repair.effectiveness.contracts import RepairExecutionStatus
from app.quality.repair.effectiveness.zero_effect_detector import DomainFingerprint
from app.quality.repair.mutation_contract import RepairMutationScope
from app.quality.repair.root_cause import RootCauseType


class RepairActuationRequest(BaseModel):
    """Authoritative request carrying all causal and snapshot context for real artifact mutation."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    artifact_id: str
    finding_ids: Tuple[str, ...]
    root_cause_cluster: str
    required_causal_reach: CausalReach
    repair_strategy_id: str
    mutation_scope: RepairMutationScope
    source_snapshot_hash: str
    blueprint_snapshot_hash: str
    render_snapshot_hash: str
    quality_baseline: float
    target_element_id: Optional[str] = None
    target_slide_or_page_index: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)


class RepairActuationResult(BaseModel):
    """Authoritative execution outcome of an executable repair transformation."""
    model_config = ConfigDict(frozen=True)

    actuator_id: str
    execution_status: RepairExecutionStatus
    transformation_applied: str
    changed_artifact_layers: Tuple[TransformationLayer, ...]
    before_fingerprint: Optional[DomainFingerprint] = None
    after_fingerprint: Optional[DomainFingerprint] = None
    changed_element_ids: Tuple[str, ...] = Field(default_factory=tuple)
    changed_blueprint_ids: Tuple[str, ...] = Field(default_factory=tuple)
    changed_knowledge_refs: Tuple[str, ...] = Field(default_factory=tuple)
    causal_reach_achieved: CausalReach
    mutation_cost: float
    rollback_capability: bool = True
    provenance: Dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""
    error_message: Optional[str] = None


class RepairActuator(Protocol):
    """Protocol implemented by all real structural and semantic transformation operators."""

    @property
    def actuator_id(self) -> str:
        ...

    @property
    def supported_artifact_types(self) -> Tuple[str, ...]:
        ...

    @property
    def supported_root_causes(self) -> Tuple[RootCauseType, ...]:
        ...

    @property
    def maximum_causal_reach(self) -> CausalReach:
        ...

    @property
    def transformation_layer(self) -> TransformationLayer:
        ...

    def can_actuate(self, request: RepairActuationRequest, blueprint: Any) -> bool:
        ...

    def actuate(self, request: RepairActuationRequest, blueprint: Any) -> Tuple[Any, RepairActuationResult]:
        ...
