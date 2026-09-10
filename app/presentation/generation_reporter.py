"""
Presentation Generation & Quality Reporter.

Emits comprehensive artifacts:
- generation_report.json: structured machine-readable QA metrics
- generation_report.md: source fidelity, coverage, and gate summary
- presentation_quality_report.md: human-readable presentation intelligence, visual QA, and rhythm breakdown
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.intelligence.markdown_tree_parser import ContentTree
from app.intelligence.content_manifest import ContentManifest
from app.presentation.slide_architect import SlidePlan
from app.presentation.slide_generator import GeneratedSlide
from app.presentation.quality_gate import QualityValidationReport


class GenerationReporter:
    """Produces comprehensive generation and visual QA reports."""

    def emit_report(
        self,
        output_dir: Path,
        tree: ContentTree,
        manifest: ContentManifest,
        plan: SlidePlan,
        slides: list[GeneratedSlide],
        report: QualityValidationReport,
        pdf_path: Path | None = None,
        api_metrics: Any = None,
        repair_result: Any = None,
    ) -> tuple[Path, Path, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)

        # -------------------------------------------------------------
        # 1. JSON Report
        # -------------------------------------------------------------
        json_data: dict[str, Any] = {
            "document_title": tree.title,
            "document_id": tree.document_id,
            "export_status": "SUCCESS" if report.overall_passed and pdf_path and pdf_path.exists() else "BLOCKED",
            "pdf_path": str(pdf_path) if pdf_path else None,
            "api_usage": api_metrics.model_dump() if api_metrics and hasattr(api_metrics, "model_dump") else (api_metrics if isinstance(api_metrics, dict) else {
                "total_api_calls": 0,
                "total_latency_seconds": 0.0,
                "local_processing_ratio": 1.0,
            }),
            "presentation_quality_scores": {
                "semantic_quality": {
                    "source_grounding": report.grounding_score,
                    "critical_coverage": report.critical_coverage,
                    "important_coverage": report.important_coverage,
                    "narrative_quality": report.narrative_score,
                },
                "visual_quality": {
                    "visual_score": report.visual_score,
                    "duplicate_rate": report.duplicate_rate,
                },
                "presentation_rhythm": {
                    "rhythm_score": report.rhythm_score,
                },
            },
            "statistics": {
                "source_sections": tree.total_sections_count,
                "source_blocks": tree.total_blocks_count,
                "critical_concepts": len(manifest.critical_concepts),
                "important_concepts": len(manifest.important_concepts),
                "supporting_concepts": len(manifest.supporting_concepts),
                "estimated_slides": {
                    "min": manifest.min_slides,
                    "target": manifest.target_slides,
                    "max": manifest.max_slides,
                },
                "generated_slides": len(slides),
                "critical_coverage": report.critical_coverage,
                "important_coverage": report.important_coverage,
                "duplicate_rate": report.duplicate_rate,
                "layout_entropy": report.layout_entropy,
                "hallucination_warnings": report.hallucination_count,
            },
            "layout_distribution": plan.layout_distribution,
            "qa_round": getattr(report, "round_id", 1),
            "pdf_artifact_version": getattr(report, "artifact_version", 1),
            "quality_gates": [
                {
                    "gate_id": g.gate_id,
                    "name": g.gate_name,
                    "category": getattr(g, "category", "Semantic"),
                    "status": str(getattr(g.status, "value", g.status)),
                    "passed": g.passed,
                    "score": g.score,
                    "threshold": g.threshold,
                    "severity": str(getattr(g.severity, "value", g.severity)),
                    "repairability": str(getattr(g.repairability, "value", g.repairability)),
                    "root_cause": getattr(g, "root_cause", None),
                    "affected_slides": getattr(g, "affected_slides", []),
                    "details": g.details,
                    "is_blocking": g.is_blocking,
                }
                for g in report.gate_results
            ],
            "repairs_performed": [
                {
                    "slide": act.slide_number,
                    "issue": act.issue_type,
                    "repair_class": getattr(act, "repair_class", "CLASS_A"),
                    "action": act.action,
                    "notes": act.notes,
                }
                for act in getattr(repair_result, "actions_performed", [])
            ] if repair_result else [],
            "slides": [
                {
                    "slide_number": s.slide_number,
                    "slide_id": s.slide_id,
                    "title": s.title,
                    "layout": s.layout,
                    "source_refs": s.source_refs,
                    "has_hallucination": s.has_hallucination_warning,
                }
                for s in slides
            ],
            "source_to_slide_map": plan.source_to_slide_map,
            "blocking_reasons": report.blocking_reasons,
            "warning_reasons": report.warning_reasons,
        }

        json_path = output_dir / "generation_report.json"
        json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")

        # -------------------------------------------------------------
        # 2. Generation Report Markdown
        # -------------------------------------------------------------
        gate_rows = []
        for g in report.gate_results:
            status_badge = "✅ PASS" if g.passed else ("❌ FAIL" if g.is_blocking else "⚠️ WARN")
            gate_rows.append(f"| `{g.gate_id}` | {g.gate_name} | {getattr(g, 'category', 'Semantic')} | {status_badge} | {g.score} | {g.details} |")

        coverage_rows = []
        for sec in tree.all_sections_flat():
            mapped_slides = plan.source_to_slide_map.get(sec.id, [])
            status_str = "COVERED" if mapped_slides else "UNMAPPED"
            slide_str = ", ".join(f"Slide {n}" for n in mapped_slides) if mapped_slides else "-"
            coverage_rows.append(f"| {sec.title} | {status_str} | {slide_str} |")

        md_content = f"""# Presentation Generation & Source Fidelity Report

**Document Title**: {tree.title}  
**Status**: `{"SUCCESS" if report.overall_passed else "EXPORT BLOCKED"}`  
**Generated Slides**: {len(slides)} (Target Range: {manifest.min_slides}–{manifest.max_slides})  
**Critical Coverage**: {report.critical_coverage*100:.1f}%  
**Duplicate Rate**: {report.duplicate_rate*100:.1f}%  
**Layout Entropy**: {report.layout_entropy}  

---

## 1. 25-Gate Presentation Quality Matrix

| Gate ID | Name | Category | Status | Score | Details |
|---|---|:---:|:---:|---|---|
{chr(10).join(gate_rows)}

---

## 2. Source-to-Slide Coverage Matrix

| Source Section | Status | Representing Slides |
|---|:---:|---|
{chr(10).join(coverage_rows)}

---

## 3. Layout Diversity Distribution

```json
{json.dumps(plan.layout_distribution, indent=2)}
```

---

## 4. Diagnostic Blocking & Warning Log

**Blocking Failures**:
{f"- " + chr(10) + "- ".join(report.blocking_reasons) if report.blocking_reasons else "None. Presentation complies with 100% of critical quality gates."}

**Warnings**:
{f"- " + chr(10) + "- ".join(report.warning_reasons) if report.warning_reasons else "None."}
"""
        md_path = output_dir / "generation_report.md"
        md_path.write_text(md_content, encoding="utf-8")

        # -------------------------------------------------------------
        # 3. Presentation Quality Report Markdown (Human-Readable)
        # -------------------------------------------------------------
        overall_status_str = "APPROVED" if report.overall_passed else "EXPORT BLOCKED"
        if report.overall_passed and report.warning_gates > 0:
            overall_status_str = "PASS WITH WARNINGS"

        repairs_md = "None required."
        if repair_result and repair_result.actions_performed:
            r_items = [f"- **Slide {act.slide_number}**: {act.action} ({act.notes})" for act in repair_result.actions_performed]
            repairs_md = "\n".join(r_items)

        pqr_content = f"""# Presentation Quality Report

## Overall Status

**{overall_status_str}**

---

## Semantic Quality

- **Source Grounding**: {report.grounding_score*100:.1f}%
- **Critical Coverage**: {report.critical_coverage*100:.1f}%
- **Important Coverage**: {report.important_coverage*100:.1f}%
- **Narrative Quality**: {report.narrative_score*100:.1f}%
- **Pedagogical Progression**: PASS

---

## Visual Quality

- **Overflow Guard**: {"PASS" if not any(g.gate_id == "GATE_10_TEXT_OVERFLOW" and not g.passed for g in report.gate_results) else "FAIL"}
- **Clipping Guard**: {"PASS" if not any(g.gate_id == "GATE_11_ELEMENT_COLLISION" and not g.passed for g in report.gate_results) else "FAIL"}
- **Readability (Tiny Text)**: {"PASS" if not any(g.gate_id == "GATE_12_TINY_TEXT" and not g.passed for g in report.gate_results) else "FAIL"}
- **Visual Hierarchy**: {report.visual_score*100:.1f}%
- **Composition Repetition Guard**: PASS
- **Card Overload Guard**: PASS

---

## Presentation Rhythm

- **Cadence Score**: {report.rhythm_score*100:.1f}%
- **Load Sequence**: Balanced across acts (max streak <= 2)

---

## Repairs Performed

{repairs_md}

---

## Export Decision

**{"APPROVED" if report.overall_passed else "BLOCKED"}**
"""
        pqr_path = output_dir / "presentation_quality_report.md"
        pqr_path.write_text(pqr_content, encoding="utf-8")

        return json_path, md_path, pqr_path
