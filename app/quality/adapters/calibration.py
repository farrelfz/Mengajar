"""
Universal Document Intelligence System V5 — Calibration Quality Signal Adapter.

Phase 3A.1: Ingests Phase 2C adversarial quality calibration reports and defects,
normalizing them into canonical QualitySignal contracts without mutating inputs.
"""

from __future__ import annotations

from typing import Any, List, Optional

from app.quality.adapters.base import BaseSignalAdapter
from app.quality.contracts.provenance import EvidenceReference, EvidenceSourceType
from app.quality.contracts.signals import (
    QualityDomain,
    QualityLocation,
    QualitySignal,
    SignalConfidence,
    SignalSeverity,
)
from app.quality.contracts.taxonomy_mapping import (
    map_legacy_severity,
    map_to_canonical_code,
    map_to_canonical_domain,
)


class CalibrationSignalAdapter(BaseSignalAdapter):
    """Adapts Phase 2C calibrated quality reports to canonical QualitySignals."""

    @classmethod
    def adapt(cls, calibration_data: Any, artifact_type: Optional[str] = None) -> List[QualitySignal]:
        signals: List[QualitySignal] = []
        if calibration_data is None:
            return signals

        art_type = (artifact_type or getattr(calibration_data, "artifact_type", "UNKNOWN")).upper()
        raw_meta = cls._safe_copy_metadata(calibration_data)

        # Ingest defects or findings
        items_to_process = []
        if isinstance(calibration_data, (list, tuple)):
            items_to_process.extend(calibration_data)
        else:
            for attr in ("defects", "findings", "items"):
                found = getattr(calibration_data, attr, None) or raw_meta.get(attr, [])
                if isinstance(found, (list, tuple)):
                    items_to_process.extend(found)

            if not items_to_process:
                if any(k in raw_meta for k in ("code", "failure_code", "finding", "message")):
                    items_to_process = [calibration_data]

        for item in items_to_process:
            if item is None:
                continue

            raw_dict = cls._safe_copy_metadata(item)
            raw_code = getattr(item, "code", getattr(item, "failure_code", raw_dict.get("code", "CALIBRATION_DEFECT")))
            code_str = raw_code.value if hasattr(raw_code, "value") else str(raw_code)
            canonical_code = map_to_canonical_code(code_str)
            domain = map_to_canonical_domain(canonical_code)

            raw_sev = getattr(item, "severity", raw_dict.get("severity", "WARNING"))
            severity = map_legacy_severity(raw_sev)

            # Location extraction
            page_indices = tuple(getattr(item, "affected_pages", getattr(item, "page_indices", raw_dict.get("page_indices", ()))))
            first_idx = page_indices[0] if page_indices else None
            element_id = getattr(item, "element_id", raw_dict.get("element_id"))

            location = QualityLocation(
                artifact_type=art_type,
                slide_index=first_idx if art_type == "PRESENTATION" else None,
                page_index=first_idx if art_type != "PRESENTATION" else None,
                element_id=element_id,
            )

            # Evidence extraction
            raw_ev = getattr(item, "evidence", raw_dict.get("evidence", {}))
            if not isinstance(raw_ev, dict):
                raw_ev = {"evidence_raw": repr(raw_ev)}

            desc = str(getattr(item, "description", getattr(item, "finding", getattr(item, "message", raw_dict.get("description", f"Calibration defect: {code_str}")))))
            raw_val = raw_dict.get("value", raw_dict.get("score", 0.0))
            thresh = raw_dict.get("threshold")

            evidence_ref = EvidenceReference(
                source_type=EvidenceSourceType.CALIBRATION_METRIC,
                description=desc,
                measurement=code_str,
                raw_value=raw_val,
                threshold=thresh,
                page_or_slide=first_idx,
                metadata=raw_ev,
            )

            signals.append(
                QualitySignal(
                    source_engine="calibrated_quality_engine",
                    domain=domain,
                    canonical_code=canonical_code,
                    severity=severity,
                    confidence=SignalConfidence.HIGH,
                    location=location,
                    evidence=(evidence_ref,),
                    raw_value=float(raw_val) if isinstance(raw_val, (int, float)) else 0.0,
                    threshold=float(thresh) if isinstance(thresh, (int, float)) else None,
                    measurement=code_str,
                    description=desc,
                    raw_metadata={
                        "original_failure_code": code_str,
                        "original_severity": str(raw_sev),
                        "adapter": "CalibrationSignalAdapter",
                        "raw_metrics": raw_dict,
                    },
                )
            )

        return signals
