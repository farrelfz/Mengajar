"""
Universal Document Intelligence System V5 — Review Evidence Package Builder.

Phase 6: Assembles complete, multi-modal evidence packages with Markdown and JSON
forensic representations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.review.contracts.enums import ReviewTrigger
from app.review.contracts.evidence import EvidenceSufficiencyResult, ReviewEvidencePackage
from app.review.evidence.lineage_adapter import ReviewLineageAdapter
from app.review.evidence.sufficiency import EvidenceSufficiencyAnalyzer


class EvidencePackageBuilder:
    """Constructs, validates, and serializes ReviewEvidencePackages."""

    @classmethod
    def assemble(
        cls,
        case_id: str,
        artifact_id: str,
        artifact_type: str,
        trigger: ReviewTrigger,
        current_state: str = "OPEN",
        quality_decision: str = "MANUAL_REVIEW_REQUIRED",
        hard_blockers: Sequence[str] = (),
        findings: Sequence[Dict[str, Any]] = (),
        signals: Sequence[Dict[str, Any]] = (),
        render_snapshot_paths: Sequence[str] = (),
        repair_history: Sequence[Any] = (),
        traceability_links: Sequence[Dict[str, Any]] = (),
        provenance_graph: Optional[Dict[str, Any]] = None,
        root_cause_analysis: Optional[Dict[str, Any]] = None,
        benchmark_comparison: Optional[Dict[str, Any]] = None,
        historical_baseline: Optional[Dict[str, float]] = None,
    ) -> ReviewEvidencePackage:
        """Assembles a verified ReviewEvidencePackage."""
        adapted_prov = ReviewLineageAdapter.adapt_quality_provenance(provenance_graph)
        adapted_rep = ReviewLineageAdapter.adapt_repair_history(repair_history)
        bboxes = ReviewLineageAdapter.extract_bounding_boxes(signals)

        sufficiency = EvidenceSufficiencyAnalyzer.evaluate(
            has_renders=bool(render_snapshot_paths),
            bounding_boxes=bboxes,
            findings=findings,
            traceability_links=traceability_links,
            repair_history=adapted_rep,
            provenance_graph=provenance_graph,
            artifact_type=artifact_type,
        )

        # Extract failed strategies
        failed_strats = [
            str(r.get("strategy"))
            for r in adapted_rep
            if not r.get("is_committed", False) and r.get("strategy")
        ]

        return ReviewEvidencePackage(
            case_id=case_id,
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            trigger=trigger,
            current_state=current_state,
            quality_decision=quality_decision,
            hard_blockers=tuple(hard_blockers),
            findings=tuple(findings),
            signals=tuple(signals),
            raw_measurements=tuple(adapted_prov.get("signals", [])),
            render_snapshot_paths=tuple(render_snapshot_paths),
            bounding_boxes=tuple(bboxes),
            semantic_traceability=tuple(traceability_links),
            repair_history=tuple(adapted_rep),
            failed_strategies=tuple(failed_strats),
            root_cause_analysis=root_cause_analysis or {},
            causal_reach={},
            convergence_history=(),
            benchmark_comparison=benchmark_comparison,
            historical_baseline=historical_baseline,
            relevant_safety_invariants=(),
            sufficiency=sufficiency,
        )

    @classmethod
    def generate_markdown_summary(cls, pkg: ReviewEvidencePackage) -> str:
        """Produces evidence.md for human inspection."""
        blockers_str = "\n".join(f"- `{b}`" for b in pkg.hard_blockers) or "None."
        findings_str = "\n".join(
            f"- **[{f.get('severity', 'INFO')}] `{f.get('failure_code', '')}`**: {f.get('message', '')}"
            for f in pkg.findings[:10]
        ) or "None recorded."

        rep_str = "\n".join(
            f"- Iteration {r.get('iteration')}: Strategy `{r.get('strategy')}`, Drift: {r.get('drift_score', 0):.3f}, Committed: {r.get('is_committed')}"
            for r in pkg.repair_history[:10]
        ) or "No previous repair attempts."

        return f"""# REVIEW EVIDENCE PACKAGE
**Case ID:** `{pkg.case_id}`  
**Artifact ID:** `{pkg.artifact_id}`  
**Artifact Type:** `{pkg.artifact_type}`  
**Trigger:** `{pkg.trigger.value}`  
**Decision:** `{pkg.quality_decision}`  
**Evidence Sufficiency:** `{pkg.sufficiency.overall_sufficiency.value}`  
*{pkg.sufficiency.explanation}*

---

## 1. Hard Blockers Remaining
{blockers_str}

---

## 2. Key Diagnostic Findings ({len(pkg.findings)} total)
{findings_str}

---

## 3. Repair Attempt History ({len(pkg.repair_history)} iterations)
{rep_str}

---

## 4. Render Evidence
Available snapshots: `{len(pkg.render_snapshot_paths)}` files.  
Bounding box defects detected: `{len(pkg.bounding_boxes)}`.
"""
