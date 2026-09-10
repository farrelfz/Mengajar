"""
Universal Document Intelligence System V5 — Rollback & Snapshot Management.

Phase 3B: Minimal, deterministic artifact-level snapshotting and instant rollback
upon detecting regressions or hard blocker introduction.
"""

from __future__ import annotations

import copy
import hashlib
import time
import uuid
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class ArtifactSnapshot(BaseModel):
    """Immutable snapshot capturing complete blueprint state before mutation."""
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    snapshot_id: str = Field(default_factory=lambda: f"snp_{uuid.uuid4().hex[:8]}")
    blueprint_state: Any
    state_hash: str
    created_at: float = Field(default_factory=time.time)


class SnapshotManager:
    """Manages creation, hashing, and restoration of minimal artifact snapshots."""

    @classmethod
    def create_snapshot(cls, blueprint: Any) -> ArtifactSnapshot:
        """Creates a deep copy snapshot of the current blueprint state."""
        bp_copy = copy.deepcopy(blueprint)
        state_hash = cls.compute_state_hash(bp_copy)
        return ArtifactSnapshot(
            blueprint_state=bp_copy,
            state_hash=state_hash,
        )

    @classmethod
    def restore_snapshot(cls, snapshot: ArtifactSnapshot) -> Any:
        """Returns a restored copy of the snapshot blueprint."""
        return copy.deepcopy(snapshot.blueprint_state)

    @classmethod
    def compute_state_hash(cls, blueprint: Any) -> str:
        """Computes deterministic SHA-256 fingerprint of blueprint data."""
        if hasattr(blueprint, "model_dump_json"):
            serialized = blueprint.model_dump_json()
        elif hasattr(blueprint, "dict"):
            import json
            serialized = json.dumps(blueprint.dict(), sort_keys=True)
        else:
            serialized = repr(blueprint)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
