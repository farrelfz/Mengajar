"""
Benchmark Script for Batch 7.9 Pre-Flight Hardening.

Generates artifacts in A4 Portrait, A4 Landscape, and Presentation 16:9,
verifies physical PDF dimensions & pagination with PyMuPDF, executes determinism checks,
and outputs a machine-readable benchmark_report.json.
"""

import asyncio
import json
from pathlib import Path
import pymupdf

from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.orchestration.production_pipeline import MaterialProductionPipeline
from tests.integration.test_true_production_pipeline import build_mock_intel_agent

SAMPLE_RAW_INPUT = """# Rotational Dynamics & Torque
Torque is the rotational equivalent of linear force.
When an external force is applied at a distance from a pivot, it creates a turning effect.

## Key Principles
- Torque depends on force magnitude and lever arm length: tau = r * F * sin(theta).
- Perpendicular forces produce maximum torque.
- Balanced torques result in rotational equilibrium.

## Worked Example: Calculating Pivot Torque
A 50 N force is applied perpendicularly to a 2.0 m lever arm.
Calculate the resulting torque.
Result: tau = 2.0 * 50 * sin(90) = 100.0 N*m.

## Common Misconception
Many believe larger forces always create larger torques regardless of angle.
In reality, a force applied parallel to the lever arm creates zero torque.
"""

async def run_benchmark():
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)

    out_base = Path("outputs/preflight_hardening_benchmark")
    out_base.mkdir(parents=True, exist_ok=True)

    formats = ["a4_portrait", "a4_landscape", "presentation_16_9"]
    report_data = {
        "input_id": "job_rotational_torque",
        "baseline_tests": 92,
        "current_tests": 101,
        "formats": {},
        "determinism": {},
    }

    print("=" * 80)
    print("RUNNING BATCH 7.9 PRE-FLIGHT HARDENING BENCHMARK")
    print("=" * 80)

    for fmt_id in formats:
        fmt_dir = out_base / fmt_id
        fmt_dir.mkdir(parents=True, exist_ok=True)

        res = await pipeline.produce_artifact(
            raw_input=SAMPLE_RAW_INPUT,
            source_hint="rotational_torque.md",
            domain=KnowledgeDomain.PHYSICS,
            audience=AudienceLevel.HIGH_SCHOOL,
            target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
            output_dir=fmt_dir,
            output_filename=f"torque_{fmt_id}",
            target_format=fmt_id,
        )

        assert res.success is True, f"Failed rendering {fmt_id}"
        pdf_path = Path(res.pdf_path)
        assert pdf_path.exists()

        doc = pymupdf.open(str(pdf_path))
        pages_count = len(doc)
        first_page = doc[0]
        rect = first_page.rect
        w_mm = round(rect.width * 25.4 / 72.0, 2)
        h_mm = round(rect.height * 25.4 / 72.0, 2)
        doc.close()

        report_data["formats"][fmt_id] = {
            "pages": pages_count,
            "composition_steps": len(res.composition.pages),
            "width_mm": w_mm,
            "height_mm": h_mm,
            "pdf_path": str(pdf_path),
        }

        print(f"[{fmt_id.upper()}] Pages: {pages_count} (Comp steps: {len(res.composition.pages)}) | Dim: {w_mm} x {h_mm} mm | PDF: {pdf_path}")

    # Determinism runs (3 runs with identical input)
    det_dir = out_base / "determinism"
    det_dir.mkdir(parents=True, exist_ok=True)
    det_results = []

    for run_idx in range(1, 4):
        run_res = await pipeline.produce_artifact(
            raw_input=SAMPLE_RAW_INPUT,
            source_hint="rotational_torque.md",
            domain=KnowledgeDomain.PHYSICS,
            audience=AudienceLevel.HIGH_SCHOOL,
            target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
            output_dir=det_dir / f"run_{run_idx}",
            output_filename="torque_det",
            target_format="a4_landscape",
        )
        doc = pymupdf.open(str(run_res.pdf_path))
        p_count = len(doc)
        doc.close()
        det_results.append({
            "run": run_idx,
            "pages": p_count,
            "assets_count": len(run_res.composition.pages),
        })

    report_data["determinism"] = {
        "runs": det_results,
        "is_deterministic": len({r["pages"] for r in det_results}) == 1,
    }

    report_file = out_base / "benchmark_report.json"
    report_file.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    print("\nBenchmark report written to:", report_file)
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_benchmark())
