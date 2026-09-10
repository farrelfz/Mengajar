"""
Universal Document Intelligence System V5 — Base Signal Provider Adapter.

Phase 3A.1: Foundation class for signal provider adapters ensuring non-mutating
ingestion, safe metadata extraction, and canonical QualitySignal synthesis.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional

from app.quality.contracts.provenance import EvidenceReference, EvidenceSourceType
from app.quality.contracts.signals import QualityLocation, QualitySignal, SignalConfidence, SignalSeverity


class BaseSignalAdapter:
    """Base class for all quality signal adapters."""

    @classmethod
    def _safe_copy_metadata(cls, obj: Any) -> Dict[str, Any]:
        """Safely extracts a dictionary representation of an object without mutating it."""
        if obj is None:
            return {}
        if isinstance(obj, dict):
            return copy.deepcopy(obj)
        if hasattr(obj, "model_dump"):
            return copy.deepcopy(obj.model_dump(mode="json"))
        if hasattr(obj, "__dict__"):
            return copy.deepcopy({k: v for k, v in obj.__dict__.items() if not k.startswith("_")})
        return {"raw_repr": repr(obj)}

    @classmethod
    def _extract_bounding_box(cls, raw_box: Any) -> Optional[tuple[float, float, float, float]]:
        """Safely parse bounding box into 4-tuple of floats."""
        if not raw_box or not isinstance(raw_box, (list, tuple)) or len(raw_box) != 4:
            return None
        try:
            x0, y0, x1, y1 = (float(v) for v in raw_box)
            if x0 <= x1 and y0 <= y1:
                return (x0, y0, x1, y1)
        except (ValueError, TypeError):
            pass
        return None
