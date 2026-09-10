"""
Universal Document Intelligence System V5 — Quality Signal Normalizer & Adapters.

Phase 3A.2: Standardized adapters translating heterogeneous diagnostic outputs
(Phase 2B Fidelity, Phase 2C Calibration, Phase 3A Rendered Quality, Legacy Gates)
into immutable canonical QualitySignal contracts without mutating source inputs.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.quality.causal.contracts import QualityLocation, QualitySignal
from app.quality.causal.provenance import EvidenceReference, EvidenceSourceType
from app.quality.causal.taxonomy import (
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalSeverity,
    DetectionConfidence,
    get_domain_for_code,
)


class BaseSignalAdapter:
    """Base adapter guaranteeing non-mutating ingest and original metadata preservation."""

    @classmethod
    def _safe_copy_metadata(cls, obj: Any) -> Dict[str, Any]:
        """Safely extracts a dictionary representation of an object without mutating it."""
        if isinstance(obj, dict):
            return copy.deepcopy(obj)
        if hasattr(obj, "model_dump"):
            return copy.deepcopy(obj.model_dump(mode="json"))
        if hasattr(obj, "__dict__"):
            return copy.deepcopy({k: v for k, v in obj.__dict__.items() if not k.startswith("_")})
        return {"repr": repr(obj)}


class CalibrationSignalAdapter(BaseSignalAdapter):
    """Normalizes Phase 2C adversarial calibration evaluation findings."""

    @classmethod
    def adapt(cls, calibration_data: Any, artifact_type: str = "UNKNOWN") -> List[QualitySignal]:
        signals: List[QualitySignal] = []
        if calibration_data is None:
            return signals

        # Support list of defects or object with defects attribute
        defects = calibration_data
        if hasattr(calibration_data, "defects"):
            defects = getattr(calibration_data, "defects")
        elif hasattr(calibration_data, "findings"):
            defects = getattr(calibration_data, "findings")

        if not isinstance(defects, (list, tuple)):
            defects = [calibration_data]

        for item in defects:
            if item is None:
                continue

            raw_dict = cls._safe_copy_metadata(item)
            code_str = str(getattr(item, "code", getattr(item, "failure_code", raw_dict.get("code", "CALIBRATION_DEFECT"))))
            if hasattr(code_str, "value"):
                code_str = code_str.value

            sev_str = str(getattr(item, "severity", raw_dict.get("severity", "WARNING"))).upper()
            if hasattr(sev_str, "value"):
                sev_str = sev_str.value

            canonical_sev = CanonicalSeverity.WARNING
            if "CRITICAL" in sev_str or "BLOCKING" in sev_str:
                canonical_sev = CanonicalSeverity.CRITICAL
            elif "MAJOR" in sev_str or "ERROR" in sev_str:
                canonical_sev = CanonicalSeverity.MAJOR
            elif "MINOR" in sev_str:
                canonical_sev = CanonicalSeverity.MINOR
            elif "INFO" in sev_str:
                canonical_sev = CanonicalSeverity.INFO

            page_indices = tuple(getattr(item, "affected_pages", getattr(item, "page_indices", raw_dict.get("page_indices", ()))))
            first_idx = page_indices[0] if page_indices else None

            location = QualityLocation(
                artifact_type=getattr(item, "artifact_type", raw_dict.get("artifact_type", artifact_type)),
                slide_index=first_idx if artifact_type.upper() == "PRESENTATION" else None,
                page_index=first_idx if artifact_type.upper() != "PRESENTATION" else None,
                element_id=getattr(item, "element_id", raw_dict.get("element_id")),
            )

            domain = get_domain_for_code(code_str)

            # Build evidence reference
            raw_ev = getattr(item, "evidence", raw_dict.get("evidence", {}))
            if not isinstance(raw_ev, dict):
                raw_ev = {"evidence_raw": repr(raw_ev)}

            evidence_ref = EvidenceReference(
                source_type=EvidenceSourceType.CALIBRATION_METRIC,
                description=str(getattr(item, "description", raw_dict.get("description", f"Calibration defect: {code_str}"))),
                measurement=code_str,
                raw_value=raw_dict.get("value", raw_dict.get("score")),
                threshold=raw_dict.get("threshold"),
                metadata=raw_ev,
            )

            # Map to canonical failure code
            try:
                canonical_code = CanonicalFailureCode(code_str)
            except ValueError:
                canonical_code = CanonicalFailureCode.LAYOUT_MONOTONY

            raw_meta = {
                "original_failure_code": code_str,
                "original_severity": sev_str,
                "adapter": "CalibrationSignalAdapter",
                "source_phase": "PHASE_2C",
                "raw_metrics": raw_dict,
            }

            signals.append(
                QualitySignal(
                    source_engine="adversarial_calibration_engine",
                    failure_domain=domain,
                    failure_code=canonical_code,
                    severity=canonical_sev,
                    detection_confidence=DetectionConfidence.HIGH,
                    location=location,
                    evidence=(evidence_ref,),
                    description=evidence_ref.description,
                    raw_metadata=raw_meta,
                )
            )

        return signals


class RenderedSignalAdapter(BaseSignalAdapter):
    """Normalizes Phase 3A physical rendered output inspection findings."""

    @classmethod
    def adapt(cls, inspection: Any, artifact_type: Optional[str] = None) -> List[QualitySignal]:
        signals: List[QualitySignal] = []
        if inspection is None:
            return signals

        art_type = artifact_type or getattr(inspection, "artifact_type", "UNKNOWN")

        all_defects = (
            list(getattr(inspection, "critical_failures", []))
            + list(getattr(inspection, "major_warnings", []))
            + list(getattr(inspection, "minor_warnings", []))
        )

        for defect in all_defects:
            raw_dict = cls._safe_copy_metadata(defect)
            code_raw = getattr(defect, "code", raw_dict.get("code", "RENDER_DEFECT"))
            code_str = code_raw.value if hasattr(code_raw, "value") else str(code_raw)

            sev_raw = getattr(defect, "severity", raw_dict.get("severity", "CRITICAL"))
            sev_str = (sev_raw.value if hasattr(sev_raw, "value") else str(sev_raw)).upper()

            canonical_sev = CanonicalSeverity.CRITICAL
            if "CRITICAL" in sev_str:
                canonical_sev = CanonicalSeverity.CRITICAL
            elif "BLOCKING" in sev_str:
                canonical_sev = CanonicalSeverity.BLOCKING
            elif "MAJOR" in sev_str or "ERROR" in sev_str:
                canonical_sev = CanonicalSeverity.MAJOR
            elif "MINOR" in sev_str:
                canonical_sev = CanonicalSeverity.MINOR
            elif "INFO" in sev_str:
                canonical_sev = CanonicalSeverity.INFO

            page_indices = tuple(getattr(defect, "page_indices", raw_dict.get("page_indices", ())))
            first_idx = page_indices[0] if page_indices else None

            # Bounding box extraction if present
            raw_ev = dict(getattr(defect, "evidence", raw_dict.get("evidence", {})))
            bbox = None
            if "bounding_box" in raw_ev and isinstance(raw_ev["bounding_box"], (list, tuple)) and len(raw_ev["bounding_box"]) == 4:
                bbox = tuple(float(x) for x in raw_ev["bounding_box"])

            location = QualityLocation(
                artifact_type=art_type,
                slide_index=first_idx if art_type.upper() == "PRESENTATION" else None,
                page_index=first_idx if art_type.upper() != "PRESENTATION" else None,
                bounding_box=bbox,
                element_id=getattr(defect, "element_id", raw_dict.get("element_id")),
            )

            # Measurement & threshold extraction
            meas_name = code_str.lower()
            raw_val = raw_ev.get("font_size", raw_ev.get("overlap_area", raw_ev.get("actual", True)))
            thresh = raw_ev.get("threshold")
            unit = "pt" if "font" in code_str.lower() else ("pt2" if "area" in code_str.lower() else None)
            comp = "<" if "TOO_SMALL" in code_str else (">" if "CLIPPING" in code_str or "COLLISION" in code_str else "==")

            evidence_ref = EvidenceReference(
                source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
                description=str(getattr(defect, "description", raw_dict.get("description", f"Render defect: {code_str}"))),
                measurement=meas_name,
                measurement_unit=unit,
                raw_value=raw_val,
                threshold=thresh,
                comparison_operator=comp,
                page_or_slide=first_idx,
                bounding_box=bbox,
                metadata=raw_ev,
            )

            try:
                canonical_code = CanonicalFailureCode(code_str)
            except ValueError:
                canonical_code = CanonicalFailureCode.RENDER_SCALE_FAILURE

            raw_meta = {
                "original_failure_code": code_str,
                "original_severity": sev_str,
                "adapter": "RenderedSignalAdapter",
                "source_phase": "PHASE_3A",
                "repair_guidance": getattr(defect, "repair_guidance", raw_dict.get("repair_guidance", "")),
                "raw_metrics": raw_dict,
            }

            signals.append(
                QualitySignal(
                    source_engine="master_rendered_quality_engine",
                    failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
                    failure_code=canonical_code,
                    severity=canonical_sev,
                    detection_confidence=DetectionConfidence.HIGH,
                    location=location,
                    evidence=(evidence_ref,),
                    description=evidence_ref.description,
                    raw_metadata=raw_meta,
                )
            )

        return signals


class LegacyPresentationGateAdapter(BaseSignalAdapter):
    """Normalizes findings emitted by legacy presentation quality gates."""

    @classmethod
    def adapt(cls, gate_result: Any, artifact_type: str = "PRESENTATION") -> List[QualitySignal]:
        signals: List[QualitySignal] = []
        if gate_result is None:
            return signals

        raw_dict = cls._safe_copy_metadata(gate_result)
        findings = (
            getattr(gate_result, "findings", [])
            or getattr(gate_result, "blocking_reasons", [])
            or getattr(gate_result, "warning_reasons", [])
            or raw_dict.get("findings", [])
        )

        for finding in findings:
            if isinstance(finding, str):
                desc = finding
                code_str = "LEGACY_GATE_REASON"
                sev = CanonicalSeverity.WARNING
                f_meta = {"message": finding}
            else:
                f_dict = cls._safe_copy_metadata(finding)
                desc = getattr(finding, "message", getattr(finding, "description", f_dict.get("description", "Legacy finding")))
                code_str = str(getattr(finding, "rule_id", getattr(finding, "code", f_dict.get("code", "PRESENTATION_RHYTHM_FAILURE"))))
                sev_raw = str(getattr(finding, "severity", f_dict.get("severity", "WARNING"))).upper()
                sev = CanonicalSeverity.CRITICAL if "BLOCK" in sev_raw or "CRIT" in sev_raw else CanonicalSeverity.WARNING
                f_meta = f_dict

            evidence_ref = EvidenceReference(
                source_type=EvidenceSourceType.LEGACY_GATE,
                description=desc,
                measurement="legacy_rule_status",
                metadata=f_meta,
            )

            try:
                canonical_code = CanonicalFailureCode(code_str)
            except ValueError:
                canonical_code = CanonicalFailureCode.PRESENTATION_RHYTHM_FAILURE

            domain = get_domain_for_code(canonical_code)

            location = QualityLocation(
                artifact_type=artifact_type,
            )

            raw_meta = {
                "original_failure_code": code_str,
                "original_severity": sev.value,
                "adapter": "LegacyPresentationGateAdapter",
                "source_phase": "LEGACY_GATE",
                "raw_metrics": f_meta,
            }

            signals.append(
                QualitySignal(
                    source_engine="presentation_quality_gate",
                    failure_domain=domain,
                    failure_code=canonical_code,
                    severity=sev,
                    detection_confidence=DetectionConfidence.MEDIUM,
                    location=location,
                    evidence=(evidence_ref,),
                    description=desc,
                    raw_metadata=raw_meta,
                )
            )

        return signals


class FidelitySignalAdapter(BaseSignalAdapter):
    """Normalizes Phase 2B structural/fidelity evaluation reports."""

    @classmethod
    def adapt(cls, fidelity_report: Any, artifact_type: str = "UNKNOWN") -> List[QualitySignal]:
        signals: List[QualitySignal] = []
        if fidelity_report is None:
            return signals

        raw_dict = cls._safe_copy_metadata(fidelity_report)
        art_type = getattr(fidelity_report, "artifact_type", raw_dict.get("artifact_type", artifact_type))

        # Check dropped elements / source units
        dropped_units = getattr(fidelity_report, "dropped_source_units", raw_dict.get("dropped_source_units", []))
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
            signals.append(
                QualitySignal(
                    source_engine="fidelity_validator",
                    failure_domain=CanonicalFailureDomain.SEMANTIC_TRACEABILITY,
                    failure_code=CanonicalFailureCode.TRACEABILITY_BREAK,
                    severity=CanonicalSeverity.CRITICAL,
                    detection_confidence=DetectionConfidence.HIGH,
                    location=QualityLocation(artifact_type=art_type, source_unit_ids=tuple(dropped_units)),
                    evidence=(evidence_ref,),
                    description=evidence_ref.description,
                    raw_metadata={
                        "original_failure_code": "DROPPED_SOURCE_UNITS",
                        "original_severity": "CRITICAL",
                        "adapter": "FidelitySignalAdapter",
                        "source_phase": "PHASE_2B",
                    },
                )
            )

        # Check capacity/slot mismatches
        slot_issues = getattr(fidelity_report, "unresolved_slots", raw_dict.get("unresolved_slots", []))
        if slot_issues:
            evidence_ref = EvidenceReference(
                source_type=EvidenceSourceType.FIDELITY_REPORT,
                description=f"Detected {len(slot_issues)} unresolved blueprint slots.",
                measurement="unresolved_slots_count",
                raw_value=len(slot_issues),
                threshold=0,
                comparison_operator=">",
                metadata={"unresolved_slots": list(slot_issues)},
            )
            signals.append(
                QualitySignal(
                    source_engine="fidelity_validator",
                    failure_domain=CanonicalFailureDomain.BLUEPRINT_INTEGRITY,
                    failure_code=CanonicalFailureCode.UNRESOLVED_SLOT,
                    severity=CanonicalSeverity.MAJOR,
                    detection_confidence=DetectionConfidence.HIGH,
                    location=QualityLocation(artifact_type=art_type),
                    evidence=(evidence_ref,),
                    description=evidence_ref.description,
                    raw_metadata={
                        "original_failure_code": "UNRESOLVED_SLOTS",
                        "original_severity": "MAJOR",
                        "adapter": "FidelitySignalAdapter",
                        "source_phase": "PHASE_2B",
                    },
                )
            )

        return signals


class QualitySignalNormalizer:
    """Universal normalizer coordinating multi-source diagnostic adapters."""

    @classmethod
    def from_rendered_inspection(cls, inspection: Any, artifact_type: Optional[str] = None) -> List[QualitySignal]:
        return RenderedSignalAdapter.adapt(inspection, artifact_type=artifact_type)

    @classmethod
    def from_calibration(cls, calibration_data: Any, artifact_type: str = "UNKNOWN") -> List[QualitySignal]:
        return CalibrationSignalAdapter.adapt(calibration_data, artifact_type=artifact_type)

    @classmethod
    def from_legacy_gate(cls, gate_result: Any, artifact_type: str = "PRESENTATION") -> List[QualitySignal]:
        return LegacyPresentationGateAdapter.adapt(gate_result, artifact_type=artifact_type)

    @classmethod
    def from_fidelity_report(cls, fidelity_report: Any, artifact_type: str = "UNKNOWN") -> List[QualitySignal]:
        return FidelitySignalAdapter.adapt(fidelity_report, artifact_type=artifact_type)
