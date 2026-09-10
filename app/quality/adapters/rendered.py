"""
Universal Document Intelligence System V5 — Rendered Quality Signal Adapter.

Phase 3A.1: Ingests Phase 3A physical rendered PDF inspection results and
normalizes them into canonical QualitySignal contracts without mutating inputs.
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


class RenderedQualitySignalAdapter(BaseSignalAdapter):
    """Adapts physical rendered inspection results to canonical QualitySignals."""

    @classmethod
    def adapt(cls, inspection: Any, artifact_type: Optional[str] = None) -> List[QualitySignal]:
        signals: List[QualitySignal] = []
        if inspection is None:
            return signals

        art_type = (artifact_type or getattr(inspection, "artifact_type", "UNKNOWN")).upper()
        raw_meta = cls._safe_copy_metadata(inspection)

        # Collect all defects from various potential attribute structures
        all_defects = []
        for attr in ("critical_failures", "major_warnings", "minor_warnings", "defects", "page_defects"):
            items = getattr(inspection, attr, None) or raw_meta.get(attr, [])
            if isinstance(items, (list, tuple)):
                all_defects.extend(items)

        for defect in all_defects:
            if defect is None:
                continue

            d_dict = cls._safe_copy_metadata(defect)
            raw_code = getattr(defect, "code", d_dict.get("code", "RENDER_DEFECT"))
            code_str = raw_code.value if hasattr(raw_code, "value") else str(raw_code)
            canonical_code = map_to_canonical_code(code_str)
            domain = map_to_canonical_domain(canonical_code)

            raw_sev = getattr(defect, "severity", d_dict.get("severity", "WARNING"))
            severity = map_legacy_severity(raw_sev)

            # Location extraction
            page_indices = tuple(getattr(defect, "page_indices", d_dict.get("page_indices", ())))
            first_idx = page_indices[0] if page_indices else None
            element_id = getattr(defect, "element_id", d_dict.get("element_id"))

            raw_ev = dict(getattr(defect, "evidence", d_dict.get("evidence", {})))
            bbox = cls._extract_bounding_box(raw_ev.get("bounding_box", d_dict.get("bounding_box")))

            location = QualityLocation(
                artifact_type=art_type,
                slide_index=first_idx if art_type == "PRESENTATION" else None,
                page_index=first_idx if art_type != "PRESENTATION" else None,
                bounding_box=bbox,
                element_id=element_id,
            )

            # Measurement & threshold extraction
            meas_name = code_str.lower()
            raw_val = raw_ev.get("actual", raw_ev.get("font_size", raw_ev.get("overlap_area", True)))
            thresh = raw_ev.get("threshold")
            unit = "pt" if "font" in code_str.lower() else ("pt2" if "area" in code_str.lower() else None)
            comp = "<" if "TOO_SMALL" in code_str else (">" if "CLIPPING" in code_str or "COLLISION" in code_str else "==")

            desc = str(getattr(defect, "description", d_dict.get("description", f"Render defect: {code_str}")))

            evidence_ref = EvidenceReference(
                source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
                description=desc,
                measurement=meas_name,
                measurement_unit=unit,
                raw_value=raw_val,
                threshold=thresh,
                comparison_operator=comp,
                page_or_slide=first_idx,
                bounding_box=bbox,
                metadata=raw_ev,
            )

            signals.append(
                QualitySignal(
                    source_engine="master_rendered_quality_engine",
                    domain=domain,
                    canonical_code=canonical_code,
                    severity=severity,
                    confidence=SignalConfidence.DEFINITIVE,
                    location=location,
                    evidence=(evidence_ref,),
                    raw_value=raw_val if isinstance(raw_val, (int, float)) else 0.0,
                    threshold=float(thresh) if isinstance(thresh, (int, float)) else None,
                    measurement=meas_name,
                    description=desc,
                    raw_metadata={
                        "original_failure_code": code_str,
                        "original_severity": str(raw_sev),
                        "adapter": "RenderedQualitySignalAdapter",
                        "repair_guidance": getattr(defect, "repair_guidance", d_dict.get("repair_guidance", "")),
                        "raw_metrics": d_dict,
                    },
                )
            )

        return signals
