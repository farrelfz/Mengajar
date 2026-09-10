"""
Universal Document Intelligence System V5 — File-Backed Review Queue Registry.

Phase 6: High-performance, atomic, zero-database queue registry storing
immutable JSON case manifests in artifacts/review_queue/.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from app.review.contracts.enums import ReviewState
from app.review.contracts.review_case import ReviewCase
from app.review.queue.leasing import LeaseManager


class ReviewQueueRegistry:
    """Coordinates case ingestion, file persistence, indexing, and leasing."""

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.base_dir = base_dir or Path("artifacts/review_queue")
        self.cases_dir = self.base_dir / "cases"
        self.leases_dir = self.base_dir / "leases"
        self.resolved_dir = self.base_dir / "resolved"

        # Ensure directories exist
        self.cases_dir.mkdir(parents=True, exist_ok=True)
        self.leases_dir.mkdir(parents=True, exist_ok=True)
        self.resolved_dir.mkdir(parents=True, exist_ok=True)

        self._index: Dict[str, ReviewCase] = {}
        self.lease_manager = LeaseManager()
        self.rebuild_index()

    def rebuild_index(self) -> int:
        """Loads all case manifests from disk into the fast in-memory index."""
        self._index.clear()
        count = 0
        for p in self.cases_dir.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    case = ReviewCase.model_validate(data)
                    self._index[case.case_id] = case
                    count += 1
            except Exception:
                continue
        return count

    def register_case(self, case: ReviewCase) -> ReviewCase:
        """Persists a new ReviewCase atomically and updates the index."""
        self._atomic_save(case)
        self._index[case.case_id] = case
        return case

    def get_case(self, case_id: str) -> Optional[ReviewCase]:
        return self._index.get(case_id)

    def list_cases(
        self,
        state: Optional[ReviewState] = None,
        min_priority: float = 0.0,
    ) -> List[ReviewCase]:
        """Lists cases filtered by state and minimum priority, sorted by priority descending."""
        now = time.time()
        results: List[ReviewCase] = []

        for case in self._index.values():
            # Check for lease expiration on LEASED or UNDER_REVIEW cases
            if case.current_state in (ReviewState.LEASED, ReviewState.UNDER_REVIEW):
                lease = self.lease_manager.get_active_lease(case.case_id, now)
                if not lease or lease.is_expired(now):
                    # Auto-expire lease and return case to OPEN
                    case = case.model_copy(
                        update={
                            "current_state": ReviewState.OPEN,
                            "assigned_reviewer_id": None,
                            "lease_expires_at": None,
                            "updated_at": now,
                        }
                    )
                    self._atomic_save(case)
                    self._index[case.case_id] = case

            if state and case.current_state != state:
                continue
            if case.priority_score < min_priority:
                continue
            results.append(case)

        return sorted(results, key=lambda c: c.priority_score, reverse=True)

    def update_case(self, case: ReviewCase) -> ReviewCase:
        """Updates an existing case atomically."""
        updated = case.model_copy(update={"updated_at": time.time()})
        self._atomic_save(updated)
        self._index[updated.case_id] = updated
        return updated

    def lease_case(
        self,
        case_id: str,
        reviewer_id: str,
        duration_seconds: float = 1800.0,
    ) -> Tuple[bool, Optional[ReviewCase], str]:
        """Acquires a lease lock on an open case for a specific reviewer."""
        case = self.get_case(case_id)
        if not case:
            return False, None, f"Case {case_id} not found."

        if case.current_state not in (ReviewState.OPEN, ReviewState.LEASED):
            return False, case, f"Case {case_id} is in state {case.current_state.value}; cannot lease."

        now = time.time()
        lease = self.lease_manager.acquire_lease(
            case_id=case_id,
            reviewer_id=reviewer_id,
            duration_seconds=duration_seconds,
            current_time=now,
        )
        if not lease:
            return False, case, f"Case {case_id} is currently locked by another reviewer."

        updated_case = case.model_copy(
            update={
                "current_state": ReviewState.LEASED,
                "assigned_reviewer_id": reviewer_id,
                "lease_expires_at": lease.expires_at,
                "updated_at": now,
            }
        )
        self.update_case(updated_case)
        return True, updated_case, "Lease acquired successfully."

    def release_case_lease(self, case_id: str, reviewer_id: str) -> bool:
        """Releases a reviewer lease and sets case back to OPEN."""
        ok = self.lease_manager.release_lease(case_id, reviewer_id)
        if ok:
            case = self.get_case(case_id)
            if case and case.current_state in (ReviewState.LEASED, ReviewState.UNDER_REVIEW):
                updated_case = case.model_copy(
                    update={
                        "current_state": ReviewState.OPEN,
                        "assigned_reviewer_id": None,
                        "lease_expires_at": None,
                        "updated_at": time.time(),
                    }
                )
                self.update_case(updated_case)
            return True
        return False

    def _atomic_save(self, case: ReviewCase) -> None:
        """Writes case JSON atomically using a temporary file and os.replace."""
        dest = self.cases_dir / f"{case.case_id}.json"
        tmp = self.cases_dir / f".{case.case_id}.tmp"
        payload = case.model_dump_json(indent=2)
        with open(tmp, "w", encoding="utf-8") as fp:
            fp.write(payload)
        os.replace(tmp, dest)
