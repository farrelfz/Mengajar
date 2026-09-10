"""
Universal Document Intelligence System V5 — Quality Signal Normalizer.

Phase 3A.1: Converts heterogeneous diagnostic outputs from Phase 2B (fidelity),
Phase 2C (semantic calibration), Phase 3A (rendered physical inspection), and legacy
presentation gates into uniform canonical QualitySignal objects.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.quality.causal.contracts import QualitySignal
from app.quality.causal.taxonomy import CanonicalFailureSeverity


class QualitySignalNormalizer:
    """Normalizes raw inspection data into immutable QualitySignal instances."""

    @classmethod
    def from_rendered_inspection(cls, inspection: Any) -> List[QualitySignal]:
        """Ingests a Phase 3A RenderedArtifactInspection object."""
        signals: List[QualitySignal] = []
        artifact_type = getattr(inspection, "artifact_type", "UNKNOWN")

        # Ingest defects
        all_defects = (
            list(getattr(inspection, "critical_failures", []))
            + list(getattr(inspection, "major_warnings", []))
            + list(getattr(inspection, "minor_warnings", []))
        )

        for defect in all_defects:
            code_str = getattr(defect.code, "value", str(defect.code))
            sev_str = getattr(defect.severity, "value", str(defect.severity)).upper()
            
            canonical_sev = CanonicalFailureSeverity.INFO
            if sev_str == "CRITICAL":
                canonical_sev = CanonicalFailureSeverity.CRITICAL
            elif sev_str in ("MAJOR", "ERROR"):
                canonical_sev = CanonicalFailureSeverity.MAJOR
            elif sev_str == "MINOR":
                canonical_sev = CanonicalFailureSeverity.MINOR

            signals.append(
                QualitySignal(
                    source_engine="rendered_quality_engine",
                    source_phase="PHASE_3A",
                    artifact_type=artifact_type,
                    page_indices=tuple(getattr(defect, "page_indices", ())),
                    dimension=cls._infer_dimension(code_str),
                    metric_name=code_str,
                    metric_value=defect.evidence.get("font_size", defect.evidence.get("overlap_area", True)),
                    threshold=str(defect.evidence.get("threshold", "")),
                    comparison="<" if "TOO_SMALL" in code_str else ">",
                    severity=canonical_sev,
                    description=getattr(defect, "description", ""),
                    evidence=dict(getattr(defect, "evidence", {})),
                    diagnostic_context={"repair_guidance": getattr(defect, "repair_guidance", "")},
                )
            )

        # Ingest key scalar metrics as informational signals
        if hasattr(inspection, "geometry_metrics"):
            gm = inspection.geometry_metrics
            signals.append(
                QualitySignal(
                    source_engine="pdf_geometry_inspector",
                    source_phase="PHASE_3A",
                    artifact_type=artifact_type,
                    dimension="geometry",
                    metric_name="min_observed_font_size",
                    metric_value=gm.min_observed_font_size,
                    threshold="11.0" if artifact_type == "PRESENTATION" else "8.5",
                    comparison=">=",
                    severity=CanonicalFailureSeverity.INFO,
                    description=f"Minimum observed font size: {gm.min_observed_font_size:.1f}pt",
                )
            )

        return signals

    @classmethod
    def from_phase_2c_report(cls, report: Any) -> List[QualitySignal]:
        """Ingests a Phase 2C ArtifactQualityReport object."""
        signals: List[QualitySignal] = []
        artifact_type = getattr(report, "artifact_type", "UNKNOWN")

        # Ingest findings
        findings = getattr(report, "findings", [])
        for f in findings:
            finding_text = getattr(f, "finding", str(f))
            sev_str = getattr(f, "severity", "warning").upper()
            
            canonical_sev = CanonicalFailureSeverity.INFO
            if sev_str in ("CRITICAL", "BLOCKING"):
                canonical_sev = CanonicalFailureSeverity.CRITICAL
            elif sev_str in ("MAJOR", "ERROR", "WARNING"):
                canonical_sev = CanonicalFailureSeverity.MAJOR
            elif sev_str == "MINOR":
                canonical_sev = CanonicalFailureSeverity.MINOR

            signals.append(
                QualitySignal(
                    source_engine="phase_2c_calibration_engine",
                    source_phase="PHASE_2C",
                    artifact_type=artifact_type,
                    dimension=getattr(f, "dimension", "semantic"),
                    metric_name=getattr(f, "metric_name", "quality_finding"),
                    metric_value=getattr(f, "observed_value", True),
                    threshold=str(getattr(f, "expected_threshold", "")),
                    severity=canonical_sev,
                    description=finding_text,
                    evidence={"details": getattr(f, "details", "")},
                )
            )

        return signals

    @classmethod
    def from_fidelity_report(cls, fidelity_report: Any) -> List[QualitySignal]:
        """Ingests a Phase 2B ArtifactFidelityReport."""
        signals: List[QualitySignal] = []
        artifact_type = getattr(fidelity_report, "artifact_type", "UNKNOWN")

        for viol in getattr(fidelity_report, "violations", []):
            signals.append(
                QualitySignal(
                    source_engine="unified_fidelity_validator",
                    source_phase="PHASE_2B",
                    artifact_type=artifact_type,
                    dimension="contract_fidelity",
                    metric_name="fidelity_violation",
                    metric_value=False,
                    severity=CanonicalFailureSeverity.CRITICAL,
                    description=str(viol),
                )
            )

        for warn in getattr(fidelity_report, "warnings", []):
            signals.append(
                QualitySignal(
                    source_engine="unified_fidelity_validator",
                    source_phase="PHASE_2B",
                    artifact_type=artifact_type,
                    dimension="contract_fidelity",
                    metric_name="fidelity_warning",
                    metric_value=False,
                    severity=CanonicalFailureSeverity.MAJOR,
                    description=str(warn),
                )
            )

        return signals

    @classmethod
    def _infer_dimension(cls, code_str: str) -> str:
        code_u = code_str.upper()
        if any(w in code_u for w in ("CLIPPING", "COLLISION", "BOUNDARY", "MARGIN")):
            return "visual_geometry"
        elif any(w in code_u for w in ("FONT", "TEXT_TOO_SMALL", "READABILITY")):
            return "readability"
        elif any(w in code_u for w in ("DENSITY", "VOID", "WALL_OF_TEXT")):
            return "density_balance"
        elif any(w in code_u for w in ("MONOTONY", "STREAK", "DUPLICATE")):
            return "composition_rhythm"
        elif any(w in code_u for w in ("WORKSPACE", "SPOILING", "QUIZ", "INQUIRY")):
            return "pedagogy"
        elif any(w in code_u for w in ("SCIENTIFIC", "CITATION", "EVIDENCE", "BAB")):
            return "academic_rigor"
        return "general"
