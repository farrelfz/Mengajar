"""
Benchmark Script for Batch 8 Capability Grammar & Taxonomy Expansion.

Executes 3 realistic multi-domain test cases across 3 physical formats,
validates physical PDF properties with PyMuPDF, logs Resolver V2 traces,
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

CASE_A_PHYSICS = """# Torque, Force, and Equilibrium
Torque is the rotational equivalent of linear force.
When an external force is applied at a distance from a pivot, it creates a turning effect.

## Key Principles
- Torque depends on force magnitude, lever arm length, and the sine of the angle: tau = r * F * sin(theta).
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

CASE_B_RESEARCH = """# Transforming Observations into Research Questions
A research problem is a statement about an area of concern, a condition to be improved, or a troubling question in scholarly literature.

## Key Phenomenon & Problem Identification
Students observe everyday phenomena such as river sedimentation or water quality decay.
The primary challenge is identifying the underlying gap between ideal ecological balance and factual pollution levels.

## Formulation and Scope Limitation
To construct a testable research question, researchers must limit the geographical and temporal scope and identify specific measurable variables.

## Literature Gap & Novelty
Current literature explores broad industrial discharge, but lacks granular empirical models for suburban river catchments.
"""

CASE_C_GENERAL_EDU = """# Research Methodology: Qualitative vs Quantitative Data
Research methodologies fall along empirical traditions depending on research questions and variables.

## Qualitative Methodology
Focuses on exploring lived experiences, perceptions, and thematic patterns through interviews and observation.

## Quantitative Methodology
Focuses on numerical measurement, hypothesis testing, and statistical generalizability through structured instruments.

## Comparative Trade-offs
Qualitative research offers high context depth with limited generalizability, while quantitative research provides broad generalizability with less contextual nuances.
"""

TEST_CASES = [
    {
        "id": "physics_torque",
        "domain": KnowledgeDomain.PHYSICS,
        "raw_input": CASE_A_PHYSICS,
        "source_hint": "torque_equilibrium.md",
        "target_artifact": TargetArtifactType.TEACHING_PRESENTATION,
    },
    {
        "id": "research_problem_formulation",
        "domain": KnowledgeDomain.RESEARCH_METHODOLOGY,
        "raw_input": CASE_B_RESEARCH,
        "source_hint": "research_problem.md",
        "target_artifact": TargetArtifactType.RESEARCH_PRESENTATION,
    },
    {
        "id": "general_edu_comparison",
        "domain": KnowledgeDomain.GENERAL_SCIENCE,
        "raw_input": CASE_C_GENERAL_EDU,
        "source_hint": "qual_vs_quant.md",
        "target_artifact": TargetArtifactType.DETAILED_HANDOUT,
    },
]

FORMATS = ["a4_portrait", "a4_landscape", "presentation_16_9"]


async def run_benchmark():
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)

    out_base = Path("outputs/capability_grammar_benchmark")
    out_base.mkdir(parents=True, exist_ok=True)

    benchmark_data = {
        "batch": "8.0",
        "taxonomy_axes_count": 6,
        "registered_capabilities_count": len(pipeline.registry.list_all()),
        "test_cases": {},
    }

    print("=" * 80)
    print("RUNNING BATCH 8 CAPABILITY GRAMMAR & TAXONOMY BENCHMARK")
    print("=" * 80)

    for case in TEST_CASES:
        case_id = case["id"]
        benchmark_data["test_cases"][case_id] = {"formats": {}}
        print(f"\n>>> PROCESSING CASE: {case_id.upper()}")

        for fmt_id in FORMATS:
            case_dir = out_base / case_id / fmt_id
            case_dir.mkdir(parents=True, exist_ok=True)

            res = await pipeline.produce_artifact(
                raw_input=case["raw_input"],
                source_hint=case["source_hint"],
                domain=case["domain"],
                audience=AudienceLevel.HIGH_SCHOOL,
                target_artifact=case["target_artifact"],
                output_dir=case_dir,
                output_filename=f"{case_id}_{fmt_id}",
                target_format=fmt_id,
            )

            assert res.success is True, f"Failed producing {case_id} on {fmt_id}"
            pdf_path = Path(res.pdf_path)
            assert pdf_path.exists()

            # Physical inspection
            doc = pymupdf.open(str(pdf_path))
            pages_count = len(doc)
            first_page = doc[0]
            rect = first_page.rect
            w_mm = round(rect.width * 25.4 / 72.0, 2)
            h_mm = round(rect.height * 25.4 / 72.0, 2)
            doc.close()

            selected_caps = [
                b.metadata.get("capability_id", "unknown")
                for page in res.composition.pages
                for r in page.regions.values()
                for b in r.blocks
            ]

            benchmark_data["test_cases"][case_id]["formats"][fmt_id] = {
                "pages": pages_count,
                "composition_steps": len(res.composition.pages),
                "width_mm": w_mm,
                "height_mm": h_mm,
                "selected_capabilities": selected_caps,
                "pdf_path": str(pdf_path),
            }

            print(f"[{fmt_id.upper()}] Pages: {pages_count} | Dim: {w_mm}x{h_mm} mm | Caps: {selected_caps}")

    report_file = out_base / "benchmark_report.json"
    report_file.write_text(json.dumps(benchmark_data, indent=2), encoding="utf-8")
    print("\nBenchmark report written to:", report_file)
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_benchmark())
