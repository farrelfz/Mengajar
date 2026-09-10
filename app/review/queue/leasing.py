"""
Universal Document Intelligence System V5 — Review Case Lease Manager.

Phase 6: Enforces concurrent review lease locks with expiration timeouts,
preventing race conditions and stale locked cases.
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class CaseLease(BaseModel):
    """Temporary ownership lock assigned to a reviewer for an open case."""
    model_config = ConfigDict(frozen=True)

    lease_id: str = Field(default_factory=lambda: f"lse_{uuid.uuid4().hex[:8]}")
    case_id: str
    reviewer_id: str
    leased_at: float = Field(default_factory=time.time)
    duration_seconds: float = 1800.0  # 30 minutes default
    is_active: bool = True

    @property
    def expires_at(self) -> float:
        return self.leased_at + self.duration_seconds

    def is_expired(self, current_time: Optional[float] = None) -> bool:
        now = current_time if current_time is not None else time.time()
        return not self.is_active or now >= self.expires_at


class LeaseManager:
    """Manages acquisition, verification, and expiration of case leases."""

    def __init__(self, default_duration_seconds: float = 1800.0) -> None:
        self.default_duration = default_duration_seconds
        self._leases_by_case: Dict[str, CaseLease] = {}

    def acquire_lease(
        self,
        case_id: str,
        reviewer_id: str,
        duration_seconds: Optional[float] = None,
        current_time: Optional[float] = None,
    ) -> Optional[CaseLease]:
        """Attempts to acquire a lease. Returns CaseLease if successful, None if locked."""
        now = current_time if current_time is not None else time.time()
        dur = duration_seconds or self.default_duration

        existing = self._leases_by_case.get(case_id)
        if existing and not existing.is_expired(now):
            if existing.reviewer_id != reviewer_id:
                # Locked by someone else
                return None
            # Already leased by same reviewer: refresh duration
            new_lease = existing.model_copy(update={"leased_at": now, "duration_seconds": dur, "is_active": True})
            self._leases_by_case[case_id] = new_lease
            return new_lease

        lease = CaseLease(
            case_id=case_id,
            reviewer_id=reviewer_id,
            leased_at=now,
            duration_seconds=dur,
            is_active=True,
        )
        self._leases_by_case[case_id] = lease
        return lease

    def release_lease(self, case_id: str, reviewer_id: str) -> bool:
        """Releases an active lease. Returns True if released, False if not matching."""
        existing = self._leases_by_case.get(case_id)
        if existing and existing.reviewer_id == reviewer_id:
            self._leases_by_case[case_id] = existing.model_copy(update={"is_active": False})
            return True
        return False

    def get_active_lease(self, case_id: str, current_time: Optional[float] = None) -> Optional[CaseLease]:
        now = current_time if current_time is not None else time.time()
        existing = self._leases_by_case.get(case_id)
        if existing and not existing.is_expired(now):
            return existing
        return None
