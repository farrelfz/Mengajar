"""
Universal Document Intelligence System V5 — Fidelity Quality Signal Adapter.

Phase 3A.1: Ingests Phase 2B artifact fidelity reports and structural validations,
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
    map_to_canonical_code,
    map_to_canonical_domain,
)


class FidelitySignalAdapter(BaseSignalAdapter):
    """Adapts Phase 2B fidelity evaluation reports to canonical QualitySignals."""

    @classmethod
    def adapt(cls, fidelity_report: Any, artifact_type: Optional[str] = None) -> List[QualitySignal]:
        signals: List[QualitySignal] = []
        if fidelity_report is None:
            return signals

        raw_meta = cls._safe_copy_metadata(fidelity_report)
        art_type = (artifact_type or getattr(fidelity_report, "artifact_type", raw_meta.get("artifact_type", "UNKNOWN"))).upper()

        # 1. Dropped source units check
        meta_dict = getattr(fidelity_report, "metadata", raw_meta.get("metadata", {})) or {}
        dropped_units = (
            getattr(fidelity_report, "dropped_source_units", None)
            or raw_meta.get("dropped_source_units")
            or meta_dict.get("dropped_source_units", [])
        )
        if dropped_units:
            evidence_ref = EvidenceReference(
                source_type=EvidenceSourceType.FIDELITY_REPORT,
                description=f"Detected {len(dropped_units)} dropped source units during transformation.",
                measurement="dropped_source_units_count",
                raw_value=len(dropped_units),
                threshold=0,
                comparison_operator=">",
                metadata={"dropped_units": list(dropped_units)},
            )
            canonical_code = map_to_canonical_code("DROPPED_SOURCE_UNITS")
            signals.append(
                QualitySignal(
                    source_engine="unified_fidelity_validator",
                    domain=QualityDomain.FIDELITY,
                    canonical_code=canonical_code,
                    severity=SignalSeverity.BLOCKING,
                    confidence=SignalConfidence.DEFINITIVE,
                    location=QualityLocation(artifact_type=art_type, source_unit_ids=tuple(str(u) for u in dropped_units)),
                    evidence=(evidence_ref,),
                    raw_value=float(len(dropped_units)),
                    threshold=0.0,
                    measurement="dropped_source_units",
                    description=evidence_ref.description,
                    raw_metadata={
                        "original_failure_code": "DROPPED_SOURCE_UNITS",
                        "adapter": "FidelitySignalAdapter",
                        "dropped_units": list(dropped_units),
                    },
                )
            )

        # 2. Unresolved slots check
        unresolved_slots = getattr(fidelity_report, "unresolved_slots", raw_meta.get("unresolved_slots", []))
        if unresolved_slots:
            evidence_ref = EvidenceReference(
                source_type=EvidenceSourceType.FIDELITY_REPORT,
                description=f"Detected {len(unresolved_slots)} unresolved blueprint slots.",
                measurement="unresolved_slots_count",
                raw_value=len(unresolved_slots),
                threshold=0,
                comparison_operator=">",
                metadata={"unresolved_slots": list(unresolved_slots)},
            )
            canonical_code = map_to_canonical_code("UNRESOLVED_SLOTS")
            signals.append(
                QualitySignal(
                    source_engine="unified_fidelity_validator",
                    domain=QualityDomain.FIDELITY,
                    canonical_code=canonical_code,
                    severity=SignalSeverity.ERROR,
                    confidence=SignalConfidence.DEFINITIVE,
                    location=QualityLocation(artifact_type=art_type),
                    evidence=(evidence_ref,),
                    raw_value=float(len(unresolved_slots)),
                    threshold=0.0,
                    measurement="unresolved_slots",
                    description=evidence_ref.description,
                    raw_metadata={
                        "original_failure_code": "UNRESOLVED_SLOTS",
                        "adapter": "FidelitySignalAdapter",
                        "unresolved_slots": list(unresolved_slots),
                    },
                )
            )

        # 3. Explicit fidelity findings if present
        findings = getattr(fidelity_report, "findings", raw_meta.get("findings", []))
        for item in findings:
            if item is None:
                continue
            f_dict = cls._safe_copy_metadata(item)
            raw_code = getattr(item, "code", getattr(item, "failure_code", f_dict.get("code", "FIDELITY_DEFECT")))
            code_str = raw_code.value if hasattr(raw_code, "value") else str(raw_code)
            canonical_code = map_to_canonical_code(code_str)
            domain = map_to_canonical_domain(canonical_code)
            desc = str(getattr(item, "finding", getattr(item, "message", getattr(item, "description", f"Fidelity finding: {code_str}"))))

            evidence_ref = EvidenceReference(
                source_type=EvidenceSourceType.FIDELITY_REPORT,
                description=desc,
                measurement=code_str,
                metadata=f_dict,
            )
            signals.append(
                QualitySignal(
                    source_engine="unified_fidelity_validator",
                    domain=domain,
                    canonical_code=canonical_code,
                    severity=SignalSeverity.ERROR,
                    confidence=SignalConfidence.HIGH,
                    location=QualityLocation(artifact_type=art_type),
                    evidence=(evidence_ref,),
                    description=desc,
                    raw_metadata={
                        "original_failure_code": code_str,
                        "adapter": "FidelitySignalAdapter",
                        "raw_metrics": f_dict,
                    },
                )
            )

        return signals
