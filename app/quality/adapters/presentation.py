"""
Universal Document Intelligence System V5 — Presentation Quality Signal Adapter.

Phase 3A.1: Ingests presentation quality gate and visual QA results,
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


class PresentationQualitySignalAdapter(BaseSignalAdapter):
    """Adapts legacy PresentationQualityGate and VisualQA outputs."""

    @classmethod
    def adapt(cls, gate_result: Any, artifact_type: str = "PRESENTATION") -> List[QualitySignal]:
        signals: List[QualitySignal] = []
        if gate_result is None:
            return signals

        raw_meta = cls._safe_copy_metadata(gate_result)
        findings = (
            getattr(gate_result, "findings", [])
            or getattr(gate_result, "blocking_reasons", [])
            or getattr(gate_result, "warning_reasons", [])
            or raw_meta.get("findings", [])
        )

        for finding in findings:
            if finding is None:
                continue

            if isinstance(finding, str):
                desc = finding
                code_str = "PRESENTATION_DEFECT"
                sev = SignalSeverity.WARNING
                f_dict = {"message": finding}
                slide_idx = None
            else:
                f_dict = cls._safe_copy_metadata(finding)
                desc = str(getattr(finding, "message", None) or getattr(finding, "description", None) or getattr(finding, "finding", None) or f_dict.get("description", "Presentation defect"))
                raw_code = (
                    getattr(finding, "rule_id", None)
                    or f_dict.get("rule_id")
                    or getattr(finding, "code", None)
                    or f_dict.get("code")
                    or getattr(finding, "failure_code", None)
                    or f_dict.get("failure_code", "PRESENTATION_DEFECT")
                )
                code_str = raw_code.value if hasattr(raw_code, "value") else str(raw_code)
                raw_sev = getattr(finding, "severity", None) or f_dict.get("severity", "WARNING")
                sev = map_legacy_severity(raw_sev)
                slide_idx = getattr(finding, "slide_index", None) or getattr(finding, "page_number", None) or f_dict.get("slide_index")

            canonical_code = map_to_canonical_code(code_str)
            domain = map_to_canonical_domain(canonical_code)

            location = QualityLocation(
                artifact_type="PRESENTATION",
                slide_index=slide_idx,
            )

            evidence_ref = EvidenceReference(
                source_type=EvidenceSourceType.LEGACY_GATE,
                description=desc,
                measurement="presentation_gate_rule",
                page_or_slide=slide_idx,
                metadata=f_dict,
            )

            signals.append(
                QualitySignal(
                    source_engine="presentation_quality_gate",
                    domain=domain,
                    canonical_code=canonical_code,
                    severity=sev,
                    confidence=SignalConfidence.HIGH,
                    location=location,
                    evidence=(evidence_ref,),
                    description=desc,
                    raw_metadata={
                        "original_failure_code": code_str,
                        "adapter": "PresentationQualitySignalAdapter",
                        "raw_metrics": f_dict,
                    },
                )
            )

        return signals
