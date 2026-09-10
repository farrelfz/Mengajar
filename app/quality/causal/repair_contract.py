"""
Universal Document Intelligence System V5 — Repair Proposal & Transaction Contract.

Phase 3A.2: Immutable contracts for repair proposals, transactions, and rollback
state tracking (Contract Hardening Only - No repair execution).
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.causal.taxonomy import CanonicalFailureDomain, FailureScope
from app.quality.causal.contracts import QualityLocation, QualitySnapshot


class RepairTransactionStatus(str, Enum):
    """The 9 canonical repair transaction lifecycle states."""
    PROPOSED = "PROPOSED"
    AUTHORIZED = "AUTHORIZED"
    SNAPSHOT_CREATED = "SNAPSHOT_CREATED"
    APPLIED = "APPLIED"
    RENDERED = "RENDERED"
    REVALIDATED = "REVALIDATED"
    ACCEPTED = "ACCEPTED"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED = "FAILED"


class RepairProposal(BaseModel):
    """Immutable contract specifying a proposed repair action without executing it."""
    model_config = ConfigDict(frozen=True)

    proposal_id: str = Field(default_factory=lambda: f"prop_{uuid.uuid4().hex[:8]}")
    target_signal_ids: Tuple[str, ...]
    target_domain: CanonicalFailureDomain
    target_scope: FailureScope
    target_location: QualityLocation
    repair_action_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    expected_impact: str
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: float = Field(default_factory=time.time)


class RepairTransaction(BaseModel):
    """Transactional container tracking repair lifecycle, pre/post snapshots, and rollback."""
    model_config = ConfigDict(frozen=True)

    transaction_id: str = Field(default_factory=lambda: f"tx_{uuid.uuid4().hex[:8]}")
    proposal: RepairProposal
    initial_snapshot: QualitySnapshot
    post_repair_snapshot: Optional[QualitySnapshot] = None
    status: RepairTransactionStatus = RepairTransactionStatus.PROPOSED
    applied_at: Optional[float] = None
    revalidated_at: Optional[float] = None
    rollback_reason: Optional[str] = None
    history: Tuple[Tuple[RepairTransactionStatus, float, str], ...] = Field(default_factory=tuple)

    def advance_status(
        self,
        new_status: RepairTransactionStatus,
        note: str = "",
        post_snapshot: Optional[QualitySnapshot] = None,
        rollback_reason: Optional[str] = None,
    ) -> RepairTransaction:
        """Returns a new immutable RepairTransaction updated to new_status."""
        now = time.time()
        new_history = self.history + ((new_status, now, note),)
        
        applied_timestamp = self.applied_at
        if new_status == RepairTransactionStatus.APPLIED and applied_timestamp is None:
            applied_timestamp = now

        reval_timestamp = self.revalidated_at
        if new_status == RepairTransactionStatus.REVALIDATED and reval_timestamp is None:
            reval_timestamp = now

        return RepairTransaction(
            transaction_id=self.transaction_id,
            proposal=self.proposal,
            initial_snapshot=self.initial_snapshot,
            post_repair_snapshot=post_snapshot if post_snapshot is not None else self.post_repair_snapshot,
            status=new_status,
            applied_at=applied_timestamp,
            revalidated_at=reval_timestamp,
            rollback_reason=rollback_reason if rollback_reason is not None else self.rollback_reason,
            history=new_history,
        )
