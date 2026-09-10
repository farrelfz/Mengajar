"""
Universal Document Intelligence System V5 — Immutable Review Provenance Ledger.

Phase 6: Append-only forensic ledger recording all human determinations,
adjudications, and directives with cryptographic tamper-evidence.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.review.provenance.hash_chain import HashChainValidator


class ReviewProvenanceEntry(BaseModel):
    """Immutable single entry in the review provenance ledger."""
    model_config = ConfigDict(frozen=True)

    entry_id: str = Field(default_factory=lambda: f"ple_{uuid.uuid4().hex[:8]}")
    case_id: str
    artifact_id: str
    event_type: str
    timestamp: float = Field(default_factory=time.time)
    actor_id: str
    actor_type: str = "HUMAN_REVIEWER"
    previous_state: Optional[str] = None
    new_state: str = ""
    decision_digest: Optional[str] = None
    directive_digest: Optional[str] = None
    evidence_digest: Optional[str] = None
    previous_hash: str = HashChainValidator.GENESIS_HASH
    entry_hash: str = ""


class ReviewProvenanceLedger:
    """Manages appending and verifying entries in the immutable ledger file."""

    def __init__(self, ledger_path: Optional[Path] = None) -> None:
        self.ledger_path = ledger_path or Path("artifacts/review_provenance/ledger.jsonl")
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def get_last_hash(self) -> str:
        """Reads the hash of the last entry in the ledger, or returns GENESIS_HASH."""
        if not self.ledger_path.exists() or self.ledger_path.stat().st_size == 0:
            return HashChainValidator.GENESIS_HASH

        last_line = ""
        with open(self.ledger_path, "r", encoding="utf-8") as fp:
            for line in fp:
                if line.strip():
                    last_line = line

        if not last_line:
            return HashChainValidator.GENESIS_HASH

        try:
            data = json.loads(last_line)
            return data.get("entry_hash", HashChainValidator.GENESIS_HASH)
        except Exception:
            return HashChainValidator.GENESIS_HASH

    def append_entry(
        self,
        case_id: str,
        artifact_id: str,
        event_type: str,
        actor_id: str,
        actor_type: str = "HUMAN_REVIEWER",
        previous_state: Optional[str] = None,
        new_state: str = "",
        decision_digest: Optional[str] = None,
        directive_digest: Optional[str] = None,
        evidence_digest: Optional[str] = None,
        timestamp: Optional[float] = None,
    ) -> ReviewProvenanceEntry:
        """Appends a new cryptographically chained entry to the ledger."""
        prev_hash = self.get_last_hash()
        ts = timestamp or time.time()
        eid = f"ple_{uuid.uuid4().hex[:8]}"

        content = {
            "entry_id": eid,
            "case_id": case_id,
            "artifact_id": artifact_id,
            "event_type": event_type,
            "timestamp": ts,
            "actor_id": actor_id,
            "actor_type": actor_type,
            "previous_state": previous_state,
            "new_state": new_state,
            "decision_digest": decision_digest,
            "directive_digest": directive_digest,
            "evidence_digest": evidence_digest,
            "previous_hash": prev_hash,
        }

        entry_hash = HashChainValidator.compute_entry_hash(content, prev_hash)

        entry = ReviewProvenanceEntry(
            entry_id=eid,
            case_id=case_id,
            artifact_id=artifact_id,
            event_type=event_type,
            timestamp=ts,
            actor_id=actor_id,
            actor_type=actor_type,
            previous_state=previous_state,
            new_state=new_state,
            decision_digest=decision_digest,
            directive_digest=directive_digest,
            evidence_digest=evidence_digest,
            previous_hash=prev_hash,
            entry_hash=entry_hash,
        )

        with open(self.ledger_path, "a", encoding="utf-8") as fp:
            fp.write(entry.model_dump_json() + "\n")

        return entry

    def read_all_entries(self) -> List[Dict[str, Any]]:
        """Reads all raw JSON entries from the ledger."""
        if not self.ledger_path.exists():
            return []
        entries: List[Dict[str, Any]] = []
        with open(self.ledger_path, "r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def verify_ledger_integrity(self) -> Tuple[bool, int, Optional[str]]:
        """Verifies the complete cryptographic chain of the ledger on disk."""
        entries = self.read_all_entries()
        return HashChainValidator.verify_chain(entries)
