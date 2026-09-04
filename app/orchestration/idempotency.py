"""
Idempotency: SHA-256 fingerprinting for deterministic duplicate prevention and result reuse.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any
from pydantic import BaseModel, Field
from app.orchestration.contracts import ProductionJobRequest, ProductionJobResult


class IdempotencyRecord(BaseModel):
    key: str
    job_id: str
    result: ProductionJobResult


class IdempotencyRegistry:
    """Stores execution results indexed by cryptographic fingerprint."""

    _RECORDS: dict[str, IdempotencyRecord] = {}

    @classmethod
    def compute_key(cls, request: ProductionJobRequest) -> str:
        payload = {
            "raw_input": request.raw_input.strip(),
            "domain": request.metadata.domain,
            "audience": request.metadata.audience_level,
            "format": request.metadata.target_format,
            "profile": request.metadata.profile,
            "seed": request.metadata.seed,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @classmethod
    def get_result(cls, key: str) -> ProductionJobResult | None:
        rec = cls._RECORDS.get(key)
        return rec.result if rec else None

    @classmethod
    def record_result(cls, key: str, job_id: str, result: ProductionJobResult) -> None:
        cls._RECORDS[key] = IdempotencyRecord(key=key, job_id=job_id, result=result)

    @classmethod
    def clear(cls) -> None:
        cls._RECORDS.clear()
