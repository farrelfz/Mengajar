"""
Universal Document Intelligence System V5 — Review Lineage Adapter.

Phase 6: Read-only adapter integrating QualityProvenanceGraph,
TransformationTraceabilityEngine, and RepairTransactionRecords into
a unified forensic timeline without creating a second provenance database.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple


class ReviewLineageAdapter:
    """Extracts and normalizes lineage from existing sovereign engines."""

    @classmethod
    def adapt_quality_provenance(
        cls, provenance_dict: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extracts decision, finding, and signal chains from QualityProvenanceGraph dict."""
        if not provenance_dict:
            return {"decision": {}, "findings": [], "signals": []}

        findings_map = provenance_dict.get("findings_by_id", {})
        signals_map = provenance_dict.get("signals_by_id", {})
        decision_rec = provenance_dict.get("decision_record", {})
        f_to_s = provenance_dict.get("finding_to_signals", {})

        detailed_findings = []
        for fid, f in findings_map.items():
            sig_ids = f_to_s.get(fid, [])
            contributing = [signals_map.get(sid, {}) for sid in sig_ids]
            detailed_findings.append(
                {
                    "finding_id": fid,
                    "failure_code": f.get("failure_code"),
                    "severity": f.get("severity"),
                    "message": f.get("message"),
                    "dimension": f.get("dimension"),
                    "affected_elements": f.get("affected_elements", ()),
                    "affected_pages": f.get("affected_pages", ()),
                    "contributing_signals": contributing,
                }
            )

        return {
            "decision": decision_rec,
            "findings": detailed_findings,
            "signals": list(signals_map.values()),
        }

    @classmethod
    def adapt_repair_history(
        cls, repair_records: Sequence[Any]
    ) -> List[Dict[str, Any]]:
        """Converts RepairTransactionRecord objects or dicts into a chronological mutation log."""
        log: List[Dict[str, Any]] = []
        for rec in repair_records:
            if hasattr(rec, "model_dump"):
                d = rec.model_dump()
            elif isinstance(rec, dict):
                d = dict(rec)
            else:
                d = {
                    "iteration": getattr(rec, "iteration", 0),
                    "strategy": str(getattr(rec, "selected_strategy", "")),
                    "quality_before": getattr(rec, "quality_before", 0.0),
                    "quality_after": getattr(rec, "quality_after", 0.0),
                    "drift_score": getattr(rec, "drift_score", 0.0),
                    "is_committed": getattr(rec, "is_committed", False),
                }
            log.append(d)
        return sorted(log, key=lambda x: x.get("iteration", 0))

    @classmethod
    def extract_bounding_boxes(
        cls, signals: Sequence[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extracts spatial bounding box measurements from raw signals."""
        boxes: List[Dict[str, Any]] = []
        for sig in signals:
            bbox = sig.get("bounding_box") or sig.get("location")
            if bbox:
                boxes.append(
                    {
                        "signal_id": sig.get("signal_id"),
                        "metric_name": sig.get("metric_name"),
                        "page_or_slide": sig.get("page_or_slide", 1),
                        "bounding_box": bbox,
                        "raw_value": sig.get("raw_value"),
                    }
                )
        return boxes
