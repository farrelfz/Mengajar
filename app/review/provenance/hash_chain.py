"""
Universal Document Intelligence System V5 — Cryptographic Hash Chain.

Phase 6: Mathematical verification of append-only review ledger integrity.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Sequence, Tuple


class HashChainValidator:
    """Computes and verifies cryptographic hash chains for ledger entries."""

    GENESIS_HASH = "0" * 64

    @classmethod
    def compute_entry_hash(cls, entry_content: Dict[str, Any], previous_hash: str) -> str:
        """Computes SHA-256 hash chaining entry content to the previous entry hash."""
        # Sort keys to ensure deterministic JSON serialization
        canonical_content = json.dumps(entry_content, sort_keys=True, separators=(",", ":"))
        combined = f"{canonical_content}:{previous_hash}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    @classmethod
    def verify_chain(cls, entries: Sequence[Dict[str, Any]]) -> Tuple[bool, int, Optional[str]]:
        """
        Verifies cryptographic integrity of a sequence of entries.
        Returns (is_valid, verified_count, error_message).
        """
        if not entries:
            return True, 0, None

        expected_prev_hash = cls.GENESIS_HASH
        for idx, entry in enumerate(entries):
            stored_hash = entry.get("entry_hash")
            stored_prev_hash = entry.get("previous_hash")

            if stored_prev_hash != expected_prev_hash:
                return (
                    False,
                    idx,
                    f"Hash chain broken at entry index {idx}: expected previous hash "
                    f"'{expected_prev_hash[:12]}...', found '{stored_prev_hash[:12] if stored_prev_hash else 'None'}...'.",
                )

            # Strip entry_hash before recomputing
            content = {k: v for k, v in entry.items() if k != "entry_hash"}
            recomputed_hash = cls.compute_entry_hash(content, expected_prev_hash)

            if recomputed_hash != stored_hash:
                return (
                    False,
                    idx,
                    f"Entry tampering detected at index {idx}: recomputed hash does not match stored entry_hash.",
                )

            expected_prev_hash = stored_hash

        return True, len(entries), None
