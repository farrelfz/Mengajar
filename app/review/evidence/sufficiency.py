"""
Universal Document Intelligence System V5 — Evidence Sufficiency Analyzer.

Phase 6: Evaluates whether available evidence across 5 key dimensions
is adequate for an expert reviewer to make a responsible epistemic decision.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence
from app.review.contracts.enums import EvidenceSufficiencyLevel
from app.review.contracts.evidence import EvidenceSufficiencyResult


class EvidenceSufficiencyAnalyzer:
    """Deterministically assesses evidence completeness without scoring document quality."""

    @classmethod
    def evaluate(
        cls,
        has_renders: bool,
        bounding_boxes: Sequence[Dict[str, Any]],
        findings: Sequence[Dict[str, Any]],
        traceability_links: Sequence[Dict[str, Any]],
        repair_history: Sequence[Dict[str, Any]],
        provenance_graph: Optional[Dict[str, Any]],
        artifact_type: str,
    ) -> EvidenceSufficiencyResult:
        missing: List[str] = []

        # 1. Geometric Evidence
        # Required if any finding mentions layout, overflow, collision, or clipping
        layout_defect = any(
            any(k in str(f.get("message", "")).lower() for k in ("overflow", "collis", "clip", "bound", "layout"))
            for f in findings
        )
        geo_ok = True
        if layout_defect and not bounding_boxes and not has_renders:
            geo_ok = False
            missing.append("Bounding box coordinates or visual renders missing for spatial/geometry findings.")

        # 2. Semantic Evidence
        sem_ok = True
        if not findings and not repair_history:
            sem_ok = False
            missing.append("Zero defect findings or diagnostic context available.")

        # 3. Traceability Evidence (critical for scientific documents and handouts)
        trace_ok = True
        if artifact_type.upper() in ("SCIENTIFIC_DOCUMENT", "KTI"):
            citation_defect = any(
                "citation" in str(f.get("message", "")).lower() or "unsupported" in str(f.get("message", "")).lower()
                for f in findings
            )
            if citation_defect and not traceability_links:
                trace_ok = False
                missing.append("Claim-to-source traceability links missing for citation integrity investigation.")

        # 4. Repair History Evidence
        repair_ok = True
        # If case came from convergence failure, repair history is strictly required
        if any("CONVERGENCE" in str(f.get("failure_code", "")) for f in findings) and not repair_history:
            repair_ok = False
            missing.append("Repair transaction history missing for convergence failure analysis.")

        # 5. Provenance Completeness
        prov_ok = provenance_graph is not None and bool(provenance_graph)
        if not prov_ok:
            missing.append("Quality decision provenance graph is missing or unpopulated.")

        # Aggregate Sufficiency Level
        failures = [geo_ok, sem_ok, trace_ok, repair_ok, prov_ok].count(False)

        if failures == 0:
            level = EvidenceSufficiencyLevel.SUFFICIENT
            expl = "Complete multi-modal evidence available across all 5 evaluation dimensions."
        elif failures <= 2 and has_renders:
            level = EvidenceSufficiencyLevel.PARTIALLY_SUFFICIENT
            expl = f"Partially sufficient evidence; {len(missing)} dimensions incomplete: " + "; ".join(missing)
        else:
            level = EvidenceSufficiencyLevel.INSUFFICIENT
            expl = f"Insufficient evidence for responsible review: " + "; ".join(missing)

        return EvidenceSufficiencyResult(
            overall_sufficiency=level,
            geometric_evidence=geo_ok,
            semantic_evidence=sem_ok,
            traceability_evidence=trace_ok,
            repair_history_evidence=repair_ok,
            provenance_completeness=prov_ok,
            missing_evidence_details=tuple(missing),
            explanation=expl,
        )
