"""
Universal Document Intelligence System V5 — Legacy Document Quality Signal Adapter.

Phase 3A.1: Ingests legacy QualityEvaluationEngine reports and findings,
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
    map_to_canonical_dimension,
    map_to_canonical_domain,
)


class LegacyDocumentQualitySignalAdapter(BaseSignalAdapter):
    """Adapts legacy QualityEvaluationEngine outputs and QualityReports."""

    @classmethod
    def adapt(cls, quality_report: Any, artifact_type: Optional[str] = None) -> List[QualitySignal]:
        signals: List[QualitySignal] = []
        if quality_report is None:
            return signals

        raw_meta = cls._safe_copy_metadata(quality_report)
        art_type = (artifact_type or getattr(quality_report, "artifact_type", raw_meta.get("artifact_type", "UNKNOWN"))).upper()

        findings = getattr(quality_report, "findings", raw_meta.get("findings", []))
        for item in findings:
            if item is None:
                continue

            f_dict = cls._safe_copy_metadata(item)
            dim_raw = getattr(item, "dimension", f_dict.get("dimension", ""))
            dim_str = dim_raw.value if hasattr(dim_raw, "value") else str(dim_raw)
            domain = map_to_canonical_domain(dim_str)

            raw_sev = getattr(item, "severity", f_dict.get("severity", "WARNING"))
            severity = map_legacy_severity(raw_sev)

            raw_code = getattr(item, "failure_code", f_dict.get("failure_code", dim_str))
            code_str = raw_code.value if hasattr(raw_code, "value") else str(raw_code)
            canonical_code = map_to_canonical_code(code_str)

            desc = str(getattr(item, "finding", getattr(item, "message", getattr(item, "description", f_dict.get("finding", "Legacy document finding")))))
            affected_sec = getattr(item, "affected_section", f_dict.get("affected_section"))

            # Page extraction from section or evidence
            page_idx = None
            if affected_sec and "page" in str(affected_sec).lower():
                parts = str(affected_sec).lower().replace("page", "").strip().split()
                if parts and parts[0].isdigit():
                    page_idx = int(parts[0])

            raw_ev = getattr(item, "evidence", f_dict.get("evidence", {}))
            if not isinstance(raw_ev, dict):
                raw_ev = {"raw_evidence": repr(raw_ev)}
            if page_idx is None and "page_number" in raw_ev:
                page_idx = int(raw_ev["page_number"])

            location = QualityLocation(
                artifact_type=art_type,
                slide_index=page_idx if art_type == "PRESENTATION" else None,
                page_index=page_idx if art_type != "PRESENTATION" else None,
                section_index=None,
            )

            evidence_ref = EvidenceReference(
                source_type=EvidenceSourceType.LEGACY_DOCUMENT_EVALUATOR,
                description=desc,
                measurement=dim_str,
                page_or_slide=page_idx,
                metadata=raw_ev,
            )

            signals.append(
                QualitySignal(
                    source_engine="legacy_quality_evaluation_engine",
                    domain=domain,
                    canonical_code=canonical_code,
                    severity=severity,
                    confidence=SignalConfidence.HIGH,
                    location=location,
                    evidence=(evidence_ref,),
                    raw_value=float(getattr(item, "score_impact", f_dict.get("score_impact", 0.0))),
                    measurement=dim_str,
                    description=desc,
                    raw_metadata={
                        "original_failure_code": code_str,
                        "legacy_dimension": dim_str,
                        "adapter": "LegacyDocumentQualitySignalAdapter",
                        "raw_metrics": f_dict,
                    },
                )
            )

        return signals
