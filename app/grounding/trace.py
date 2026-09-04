"""
Grounding Trace and Explainability Auditor.
"""

from __future__ import annotations

from typing import Any
from app.grounding.contracts import GroundingReport


class GroundingTraceAuditor:
    """Serializes grounding diagnostic decisions for explainability logs."""

    @classmethod
    def serialize_report(cls, report: GroundingReport) -> dict[str, Any]:
        return {
            "claims_total": report.claims_total,
            "claims_grounded": report.claims_grounded,
            "claims_partial": report.claims_partial,
            "claims_unsupported": report.claims_unsupported,
            "claims_contradicted": report.claims_contradicted,
            "overall_score": report.score.overall_score,
            "coverage_score": report.score.coverage,
            "consistency_score": report.score.consistency,
            "findings_count": len(report.findings),
            "findings": [f.model_dump() for f in report.findings],
            "trace_decisions": report.trace.decisions,
        }
