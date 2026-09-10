"""
Universal Document Intelligence System V5 — Rendered Quality Reporter.

Phase 3A: Generates machine-readable JSON and human-readable Markdown
diagnostic reports for rendered output inspections.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

from app.quality.rendered.contracts import (
    RenderedArtifactInspection,
    RenderedQualityDecision,
)


class RenderedQualityReporter:
    """Serializes RenderedArtifactInspection into JSON and Markdown reports."""

    @classmethod
    def to_markdown(cls, inspection: RenderedArtifactInspection) -> str:
        lines = [
            f"# Rendered Artifact Quality Report — {inspection.artifact_type}",
            f"**Inspection ID**: `{inspection.inspection_id}`",
            f"**PDF Path**: `{inspection.rendered_pdf_path}`",
            f"**Pages Rendered**: {inspection.page_count} (Dimensions: {inspection.page_dimensions[0]:.1f} x {inspection.page_dimensions[1]:.1f} pt)",
            "",
            "## Quality Decision",
            f"**Decision**: `{inspection.decision.value}` | **Can Export**: `{inspection.can_export}`",
            f"**Rationale**: {inspection.rationale}",
            f"**Overall Quality Score**: `{inspection.overall_quality_score:.3f}`",
            "",
            "## Dimensional Score Breakdown",
            "| Dimension | Score | Status |",
            "| :--- | :---: | :--- |",
        ]

        for dim, score in inspection.dimensional_scores.items():
            status_icon = "✅ PASS" if score >= 0.85 else ("⚠️ WARN" if score >= 0.70 else "🛑 CRITICAL")
            lines.append(f"| {dim.replace('_', ' ').title()} | `{score:.3f}` | {status_icon} |")

        lines.extend([
            "",
            "## Structural Metrics",
            f"- **Blank Pages Count**: {inspection.structural_metrics.blank_pages_count}",
            f"- **Total Text Blocks**: {inspection.structural_metrics.total_text_blocks}",
            f"- **Total Images Count**: {inspection.structural_metrics.total_images_count}",
            f"- **Format Dimensions Match**: `{inspection.structural_metrics.format_dimensions_match}`",
            "",
            "## Geometry Metrics",
            f"- **Text Clipping Instances**: {inspection.geometry_metrics.text_clipping_instances}",
            f"- **Tiny Text Spans Count**: {inspection.geometry_metrics.tiny_text_spans_count}",
            f"- **Element Collision Count**: {inspection.geometry_metrics.element_collision_count}",
            f"- **Mean Margin**: `{inspection.geometry_metrics.mean_margin_pt:.1f} pt`",
            f"- **Observed Font Sizes**: `{inspection.geometry_metrics.min_observed_font_size:.1f} pt` to `{inspection.geometry_metrics.max_observed_font_size:.1f} pt`",
            "",
            "## Raster Metrics",
            f"- **Mean Visual Density**: `{inspection.raster_metrics.mean_visual_density:.3f}`",
            f"- **Blank Region Ratio**: `{inspection.raster_metrics.blank_region_ratio:.3f}`",
            f"- **Visual Balance Score**: `{inspection.raster_metrics.visual_balance_score:.3f}`",
            f"- **Edge Density**: `{inspection.raster_metrics.edge_density:.3f}`",
            "",
            "## Typography & Hierarchy",
            f"- **Headline to Body Ratio**: `{inspection.hierarchy_metrics.headline_to_body_ratio:.2f}`",
            f"- **Hierarchy Contrast Score**: `{inspection.hierarchy_metrics.hierarchy_contrast_score:.3f}`",
            "",
            "## Content Density & Whitespace",
            f"- **Mean Occupancy Ratio**: `{inspection.density_metrics.mean_occupancy_ratio:.3f}`",
            f"- **Whitespace Ratio**: `{inspection.density_metrics.whitespace_ratio:.3f}`",
            f"- **Overloaded Pages Count**: {inspection.density_metrics.overloaded_pages_count}",
            f"- **Sparse Pages Count**: {inspection.density_metrics.suspiciously_sparse_pages_count}",
            "",
            "## Composition & Repetition",
            f"- **Layout Diversity Score**: `{inspection.repetition_metrics.layout_diversity_score:.3f}`",
            f"- **Max Repetition Streak**: {inspection.repetition_metrics.max_repetition_streak}",
            f"- **Near-Duplicate Pages Count**: {inspection.repetition_metrics.near_duplicate_pages_count}",
            "",
            "## Artifact-Specific Metrics",
        ])

        for k, v in inspection.artifact_specific_metrics.items():
            lines.append(f"- **{k.replace('_', ' ').title()}**: `{v}`")

        # Defects Summary
        lines.extend([
            "",
            "## Defects & Failure Taxonomy",
            f"### Critical Failures ({len(inspection.critical_failures)})",
        ])
        if inspection.critical_failures:
            for f in inspection.critical_failures:
                lines.append(f"- 🛑 `[{f.code.value}]` (Pages {list(f.page_indices)}): {f.description} [Repair: `{f.recommended_future_repair.value}`]")
        else:
            lines.append("- *Zero critical failures detected.*")

        lines.extend([
            "",
            f"### Major Warnings ({len(inspection.major_warnings)})",
        ])
        if inspection.major_warnings:
            for f in inspection.major_warnings:
                lines.append(f"- ⚠️ `[{f.code.value}]` (Pages {list(f.page_indices)}): {f.description} [Repair: `{f.recommended_future_repair.value}`]")
        else:
            lines.append("- *Zero major warnings detected.*")

        lines.extend([
            "",
            f"### Minor Warnings ({len(inspection.minor_warnings)})",
        ])
        if inspection.minor_warnings:
            for f in inspection.minor_warnings:
                lines.append(f"- ℹ️ `[{f.code.value}]` (Pages {list(f.page_indices)}): {f.description}")
        else:
            lines.append("- *Zero minor warnings detected.*")

        # Diagnostic Page Samples
        lines.extend([
            "",
            "## Diagnostic Page Overview",
        ])
        for p in inspection.page_details[:10]:  # Show first 10 pages for conciseness
            fail_notes = f" | Defects: {[f.code.value for f in p.failures]}" if p.failures else ""
            lines.append(
                f"- **Page {p.page_number}**: Occupancy `{p.occupancy_ratio:.2f}` ({p.density_status}) | "
                f"Text: {p.text_length} chars | Fonts: `{p.min_font_size:.1f}-{p.max_font_size:.1f} pt`{fail_notes}"
            )
        if len(inspection.page_details) > 10:
            lines.append(f"- *... and {len(inspection.page_details) - 10} additional pages.*")

        lines.append("")
        return "\n".join(lines)

    @classmethod
    def save_reports(
        cls,
        inspection: RenderedArtifactInspection,
        output_dir: Path,
        prefix: str = "rendered_quality_report",
    ) -> Tuple[Path, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        md_path = output_dir / f"{prefix}.md"
        json_path = output_dir / f"{prefix}.json"

        md_content = cls.to_markdown(inspection)
        md_path.write_text(md_content, encoding="utf-8")

        json_data = inspection.model_dump()
        json_path.write_text(json.dumps(json_data, indent=2, default=str), encoding="utf-8")

        return md_path, json_path
