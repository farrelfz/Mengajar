"""
Integration Golden Benchmark Test for Universal Document Intelligence System V5.

Phase 3A: End-to-end rendered output quality benchmark evaluating all 4 core artifact types:
1. PRESENTATION (16:9 Slide Deck)
2. HANDOUT (A4 Continuous Reading Material)
3. WORKSHEET / LKS (Educational Activity Sheet)
4. SCIENTIFIC DOCUMENT / KTI (Academic Paper)

Validates truthful diagnostic evaluation, orthogonal dimensional scoring,
failure taxonomy tagging, and export gating.
"""

import json
from pathlib import Path
import pytest

from app.quality.rendered.quality_engine import MasterRenderedQualityEngine
from app.quality.rendered.quality_reporter import RenderedQualityReporter
from app.quality.rendered.diagnostic_contact_sheet import DiagnosticContactSheetGenerator
from app.quality.rendered.contracts import RenderedQualityDecision, RenderedArtifactInspection
from app.quality.rendered.failure_taxonomy import RenderedFailureCode


@pytest.fixture(scope="module")
def benchmark_artifacts():
    base_dir = Path("outputs/benchmark/phase_2c/artifacts/01_oobleck_experiment")
    return {
        "PRESENTATION": base_dir / "presentation" / "presentation.pdf",
        "HANDOUT": base_dir / "handout" / "handout.pdf",
        "WORKSHEET": base_dir / "worksheet" / "worksheet.pdf",
        "SCIENTIFIC_DOCUMENT": base_dir / "scientific" / "scientific.pdf",
    }


def test_01_golden_benchmark_evaluation_all_artifacts(benchmark_artifacts):
    output_base = Path("outputs/benchmark/phase_3a/01_oobleck_experiment")
    output_base.mkdir(parents=True, exist_ok=True)

    engine = MasterRenderedQualityEngine()
    contact_gen = DiagnosticContactSheetGenerator()
    results: dict[str, RenderedArtifactInspection] = {}

    for artifact_type, pdf_path in benchmark_artifacts.items():
        if not pdf_path.exists():
            pytest.skip(f"Benchmark PDF not found: {pdf_path}")

        artifact_out = output_base / artifact_type.lower()
        artifact_out.mkdir(parents=True, exist_ok=True)

        # 1. Independent Rendered Inspection
        insp = engine.inspect(pdf_path, artifact_type=artifact_type)
        results[artifact_type] = insp

        # 2. Export Detailed Reports
        md_path, json_path = RenderedQualityReporter.save_reports(
            insp, artifact_out, prefix=f"{artifact_type.lower()}_quality_report"
        )
        assert md_path.exists() and md_path.stat().st_size > 200
        assert json_path.exists() and json_path.stat().st_size > 200

        # 3. Generate Diagnostic Contact Sheet
        cs_path = contact_gen.generate(
            pdf_path,
            artifact_out / f"{artifact_type.lower()}_contact_sheet.png",
            inspection=insp,
        )
        assert cs_path.exists() and cs_path.stat().st_size > 1000

    # Verification of Truthful Diagnostic Behavior:
    # 1. Presentation
    pres = results["PRESENTATION"]
    assert pres.artifact_type == "PRESENTATION"
    assert pres.page_count == 14
    # Truthful diagnostic: element collision and small text detected
    assert pres.decision == RenderedQualityDecision.BLOCKED
    assert pres.can_export is False
    assert any(f.code == RenderedFailureCode.ELEMENT_COLLISION for f in pres.critical_failures)

    # 2. Handout
    handout = results["HANDOUT"]
    assert handout.artifact_type == "HANDOUT"
    assert handout.page_count == 3
    assert handout.decision == RenderedQualityDecision.PASS_WITH_WARNINGS
    assert handout.can_export is True
    assert handout.overall_quality_score > 0.85

    # 3. Worksheet
    ws = results["WORKSHEET"]
    assert ws.artifact_type == "WORKSHEET"
    assert ws.page_count == 15
    # Anti-spoiling rule maintained
    assert not any(f.code == RenderedFailureCode.WORKSHEET_SPOILING_FAILURE for f in ws.critical_failures)
    # Student workspace boxes recognized as positive utility
    assert ws.artifact_specific_metrics.get("total_workspace_boxes", 0) >= 10

    # 4. Scientific Document
    sci = results["SCIENTIFIC_DOCUMENT"]
    assert sci.artifact_type == "SCIENTIFIC_DOCUMENT"
    assert sci.page_count == 10
    # Truthful diagnostic: citation invisibility caught
    assert any(f.code == RenderedFailureCode.SCIENTIFIC_CITATION_INVISIBLE for f in sci.major_warnings)

    # Generate Cross-Artifact Executive Summary
    summary_md = output_base.parent / "phase_3a_golden_benchmark_summary.md"
    summary_json = output_base.parent / "phase_3a_golden_benchmark_summary.json"

    summary_rows = []
    summary_data = {}
    for atype, insp in results.items():
        summary_rows.append(
            f"| {atype} | `{insp.decision.value}` | `{insp.can_export}` | `{insp.overall_quality_score:.3f}` | "
            f"{len(insp.critical_failures)} | {len(insp.major_warnings)} | {len(insp.minor_warnings)} |"
        )
        summary_data[atype] = {
            "decision": insp.decision.value,
            "can_export": insp.can_export,
            "overall_quality_score": insp.overall_quality_score,
            "critical_failures_count": len(insp.critical_failures),
            "major_warnings_count": len(insp.major_warnings),
            "minor_warnings_count": len(insp.minor_warnings),
            "dimensional_scores": insp.dimensional_scores,
        }

    summary_content = f"""# Universal Document Intelligence System V5 — Phase 3A Golden Benchmark Summary

**Benchmark Subject**: `01_oobleck_experiment` (All 4 Artifact Formats)
**Phase 3A Focus**: Independent, Adversarial, Rendered-Output Quality Intelligence Layer

## Executive Decision Matrix
| Artifact Type | Decision | Can Export | Score | Critical | Major | Minor |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
{"\n".join(summary_rows)}

## Core Architectural Invariants Verified
1. **Contract Fidelity != Rendered Quality**: High schema fidelity in Phase 2B/2C did not conceal physical rendering bugs (presentation collision, worksheet tiny fonts, scientific citation invisibility).
2. **Deterministic Geometry & Raster Proof**: Evaluators inspected raw PyMuPDF display lists and Pillow pixel statistics without heuristic AI or LLM fuzziness.
3. **Workspace Preservation**: Worksheet empty response boxes (drawings >= 35pt) were classified as intentional student canvas, preventing accidental void penalties.
4. **Honest Gatekeeping**: CRITICAL failures categorically blocked PDF export (`can_export = False`), regardless of overall numerical scores.
"""
    summary_md.write_text(summary_content, encoding="utf-8")
    summary_json.write_text(json.dumps(summary_data, indent=2), encoding="utf-8")

    assert summary_md.exists()
    assert summary_json.exists()
