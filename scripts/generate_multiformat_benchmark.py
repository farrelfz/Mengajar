#!/usr/bin/env python3
"""
KIR AI Document Intelligence — Multi-Format Benchmark.

Demonstrates that the exact same semantic material can be rendered into
multiple physical canvas formats (A4 Portrait, A4 Landscape, Presentation 16:9)
without altering the underlying semantic blueprint.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.formats import A4_PORTRAIT, A4_LANDSCAPE, PRESENTATION_16_9
from app.orchestration.production_pipeline import MaterialProductionPipeline
from app.rendering.validation.screenshot_exporter import PDFScreenshotExporter
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


SAMPLE_TEXT = """
# Physics of Rotational Motion: Understanding Torque

## 1. Door Handle Phenomenon
Why is a door handle positioned as far as possible from the hinges?
Opening a door by pushing directly on the hinges requires immense force, while pushing at the edge requires minimal effort.

## 2. Formal Concept & Definition
Torque (tau) is the rotational analog of force, measuring the effectiveness of a force in causing rotational acceleration.
Formula: tau = r * F * sin(theta).

## 3. Rotational Equilibrium
For a body to be in static rotational equilibrium, the net torque acting about any arbitrary pivot point must equal zero.
"""


async def main() -> None:
    base_out = Path("outputs/multiformat_benchmark")
    base_out.mkdir(parents=True, exist_ok=True)

    intel_agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=intel_agent)
    exporter = PDFScreenshotExporter()

    formats = [
        ("a4_portrait", A4_PORTRAIT.id, "A4 Portrait (210x297 mm)"),
        ("a4_landscape", A4_LANDSCAPE.id, "A4 Landscape (297x210 mm)"),
        ("presentation_16_9", PRESENTATION_16_9.id, "Presentation 16:9 (13.33x7.5 in)"),
    ]

    print("\n" + "=" * 80)
    print("KIR AI — MULTI-FORMAT BENCHMARK (SEMANTIC INTENT != PHYSICAL FORMAT)")
    print("=" * 80)

    for sub_name, fmt_id, desc in formats:
        out_dir = base_out / sub_name
        out_dir.mkdir(parents=True, exist_ok=True)

        result = await pipeline.produce_artifact(
            raw_input=SAMPLE_TEXT,
            source_hint="rotational_torque.md",
            domain=KnowledgeDomain.PHYSICS,
            audience=AudienceLevel.HIGH_SCHOOL,
            target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
            target_format=fmt_id,
            output_dir=out_dir,
            output_filename=f"torque_{sub_name}",
        )

        print(f"\n[Format: {desc}]")
        print(f"  Success: {result.success}")
        print(f"  Resolved Format ID: {result.composition.format_id}")
        print(f"  PDF Path: {result.pdf_path}")
        print(f"  Pages: {len(result.composition.pages)}")

        if result.pdf_path:
            shots = exporter.export_pages(result.pdf_path, out_dir / "screenshots")
            print(f"  Screenshots exported: {len(shots)}")

    print("\n" + "=" * 80)
    print("Benchmark complete. Inspecting resulting PDFs...")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
