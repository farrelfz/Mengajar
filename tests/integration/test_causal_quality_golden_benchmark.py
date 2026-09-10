"""
Integration Golden Benchmark Test for Phase 3A.1: Causal Attribution & Authority Consolidation.

Validates end-to-end execution of UnifiedQualityAuthority across the four golden
Oobleck artifacts, generating causal diagnostic reports and verifying failure clusters.
"""

import json
from pathlib import Path
import pytest

from app.quality.rendered.quality_engine import MasterRenderedQualityEngine
from app.quality.causal import (
    UnifiedQualityAuthority,
    CausalQualityReporter,
    UnifiedDecisionStatus,
    ArchitectureLayer,
)


@pytest.fixture(scope="module")
def benchmark_artifacts():
    base_dir = Path("outputs/benchmark/phase_2c/artifacts/01_oobleck_experiment")
    return {
        "PRESENTATION": base_dir / "presentation" / "presentation.pdf",
        "HANDOUT": base_dir / "handout" / "handout.pdf",
        "WORKSHEET": base_dir / "worksheet" / "worksheet.pdf",
        "SCIENTIFIC_DOCUMENT": base_dir / "scientific" / "scientific.pdf",
    }


def test_01_causal_golden_benchmark_evaluation(benchmark_artifacts):
    output_base = Path("outputs/benchmark/phase_3a_1/01_oobleck_experiment")
    output_base.mkdir(parents=True, exist_ok=True)

    rendered_engine = MasterRenderedQualityEngine()
    assessments = {}

    for artifact_type, pdf_path in benchmark_artifacts.items():
        if not pdf_path.exists():
            pytest.skip(f"Benchmark PDF not found: {pdf_path}")

        artifact_out = output_base / artifact_type.lower()
        artifact_out.mkdir(parents=True, exist_ok=True)

        # 1. Ingest physical rendered inspection
        insp = rendered_engine.inspect(pdf_path, artifact_type=artifact_type)

        # 2. Run UnifiedQualityAuthority
        assessment = UnifiedQualityAuthority.evaluate_artifact(
            artifact_type=artifact_type,
            rendered_inspection=insp,
        )
        assessments[artifact_type] = assessment

        # 3. Export Causal Reports
        md_path, json_path = CausalQualityReporter.save_reports(
            assessment, artifact_out, prefix=f"{artifact_type.lower()}_causal_report"
        )
        assert md_path.exists() and md_path.stat().st_size > 200
        assert json_path.exists() and json_path.stat().st_size > 200

    # 4. Verify Causal Insights on Golden Fixtures:
    # A. Presentation
    pres = assessments["PRESENTATION"]
    assert pres.decision == UnifiedDecisionStatus.BLOCKED
    assert pres.can_export is False
    assert pres.repair_required is True
    assert len(pres.failure_clusters) >= 1
    # Check that root cause is attributed
    assert any(c.primary_root_cause is not None for c in pres.failure_clusters)

    # B. Handout
    handout = assessments["HANDOUT"]
    assert handout.decision == UnifiedDecisionStatus.PASS_WITH_WARNINGS
    assert handout.can_export is True
    assert handout.page_count == 3

    # C. Worksheet
    ws = assessments["WORKSHEET"]
    assert ws.decision == UnifiedDecisionStatus.NEEDS_REPAIR
    assert ws.can_export is False
    assert ws.page_count == 15

    # D. Scientific Document
    sci = assessments["SCIENTIFIC_DOCUMENT"]
    assert sci.decision == UnifiedDecisionStatus.NEEDS_REPAIR
    assert sci.can_export is False
    assert sci.page_count == 10
    # Citations suppressed at composition/render layer
    assert any(c.primary_root_cause.cause_layer == ArchitectureLayer.COMPOSITION for c in sci.failure_clusters if c.primary_root_cause)

    # 5. Generate Master Executive Causal Summary
    summary_md = output_base.parent / "phase_3a_1_golden_benchmark_causal_summary.md"
    summary_json = output_base.parent / "phase_3a_1_golden_benchmark_causal_summary.json"

    rows = []
    summary_data = {}
    for atype, asm in assessments.items():
        top_cause = asm.failure_clusters[0].primary_root_cause.cause_code if asm.failure_clusters and asm.failure_clusters[0].primary_root_cause else "NONE"
        top_layer = asm.failure_clusters[0].primary_root_cause.cause_layer.value if asm.failure_clusters and asm.failure_clusters[0].primary_root_cause else "NONE"
        rows.append(
            f"| {atype} | `{asm.decision.value}` | `{asm.can_export}` | `{asm.overall_quality_score:.3f}` | "
            f"`{top_cause}` | `{top_layer}` | {len(asm.failure_clusters)} |"
        )
        summary_data[atype] = {
            "decision": asm.decision.value,
            "can_export": asm.can_export,
            "overall_quality_score": asm.overall_quality_score,
            "top_root_cause": top_cause,
            "owning_layer": top_layer,
            "clusters_count": len(asm.failure_clusters),
            "failures_count": len(asm.failures),
        }

    summary_content = f"""# Universal Document Intelligence System V5 — Phase 3A.1 Golden Benchmark Causal Summary

**Benchmark Subject**: `01_oobleck_experiment` (All 4 Artifact Formats)
**Phase 3A.1 Focus**: Quality Authority Consolidation & Causal Failure Attribution

## Executive Decision & Causal Attribution Matrix
| Artifact Type | Decision | Can Export | Score | Top Root Cause | Owning Layer | Clusters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
{"\n".join(rows)}

## Core Causal Findings
1. **Symptom vs Root Cause Separated**: Detected physical defects (font sizes, collisions, invisible citations) are linked to architectural layers rather than treated as superficial styling issues.
2. **Authority Unified**: A single authority (`UnifiedQualityAuthority`) issued authoritative lifecycle decisions.
3. **Safe Repair Boundaries Established**: Every cluster defines permitted and forbidden repair actions for future Phase 3B.
"""
    summary_md.write_text(summary_content, encoding="utf-8")
    summary_json.write_text(json.dumps(summary_data, indent=2), encoding="utf-8")

    assert summary_md.exists()
    assert summary_json.exists()
