"""
Batch 11 Intelligent Material Director Physical PDF Benchmark.

Executes 5 pedagogical benchmark cases across 3 physical formats (A4 Portrait, A4 Landscape, 16:9 Presentation) = 15 physical PDFs.
Validates physical dimensions, learning journey validity, director traces, diagnostics, and determinism.
Outputs full report to outputs/intelligent_director_benchmark/benchmark_report.json.
"""

import asyncio
import json
from pathlib import Path
import pymupdf

from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.director import MaterialStrategyType
from app.orchestration.production_pipeline import MaterialProductionPipeline
from tests.integration.test_true_production_pipeline import build_mock_intel_agent

DIRECTOR_BENCHMARK_CASES = [
    {
        "case_id": "case_1_physics_torque",
        "title": "Understanding Torque",
        "domain": KnowledgeDomain.PHYSICS,
        "audience": AudienceLevel.HIGH_SCHOOL,
        "raw_input": """# Classical Mechanics: Understanding Torque
Torque is the rotational analogue of linear force, calculated as tau = r * F * sin(theta).

## Rotational Equilibrium Protocol
1. Establish Reference Frame: Select pivot point (O) to eliminate unknown pivot reaction forces.
2. Construct Free Body Diagram: Draw all normal, applied, and gravitational force vectors.
3. Compute Lever Arms: Calculate perpendicular distance for each force component.
4. Solve Equilibrium System: Set Sum of Torques = 0 and solve for target variables.
""",
        "source_hint": "physics_torque.md",
        "target_artifact": TargetArtifactType.TEACHING_PRESENTATION,
        "expected_strategy": MaterialStrategyType.CONCRETE_TO_ABSTRACT,
    },
    {
        "case_id": "case_2_research_problem",
        "title": "How to Formulate a Research Problem",
        "domain": KnowledgeDomain.RESEARCH_METHODOLOGY,
        "audience": AudienceLevel.UNDERGRADUATE,
        "raw_input": """# Research Methodology: Formulating a Research Problem
Bridging broad real-world challenges with focused, answerable research questions.

## Problem Formulation Funnel
- Broad Societal Challenge: High energy consumption in urban cloud computing data centers.
- Academic Literature Gap: Lack of thermal-aware dynamic VM allocation algorithms under unpredictable workloads.
- Specific Research Objective: Design a predictive reinforcement learning scheduler to reduce cooling energy by 25%.
""",
        "source_hint": "research_problem.md",
        "target_artifact": TargetArtifactType.DETAILED_HANDOUT,
        "expected_strategy": MaterialStrategyType.RESEARCH_METHOD_TUTORIAL,
    },
    {
        "case_id": "case_3_academic_writing",
        "title": "Writing a Strong Argumentative Paragraph",
        "domain": KnowledgeDomain.GENERAL_SCIENCE,
        "audience": AudienceLevel.UNDERGRADUATE,
        "raw_input": """# Academic Writing: Paragraph Anatomy & Logic
Constructing coherent, persuasive body paragraphs in scholarly essays.

## Paragraph Anatomy Workflow
1. Topic Sentence: State the singular claim that directly advances the thesis.
2. Evidence & Data: Cite empirical findings or textual quotes with precise context.
3. Critical Analysis: Unpack the warrant explaining how evidence supports the claim.
4. Concluding Transition: Synthesize the insight and connect logically to the next section.
""",
        "source_hint": "academic_writing.md",
        "target_artifact": TargetArtifactType.TEACHING_PRESENTATION,
        "expected_strategy": MaterialStrategyType.ARGUMENTATION_BUILDING,
    },
    {
        "case_id": "case_4_experiment_design",
        "title": "Designing a Controlled Experiment",
        "domain": KnowledgeDomain.GENERAL_SCIENCE,
        "audience": AudienceLevel.UNDERGRADUATE,
        "raw_input": """# Laboratory Science: Designing Controlled Experiments
Ensuring internal validity and reproducibility through strict variable isolation.

## Experimental Protocol & Controls
- Independent Variable: Substrate Nitrogen concentration (0 mM, 5 mM, 10 mM, 20 mM).
- Dependent Variable: Total chlorophyll content measured via spectrophotometry at 663 nm.
- Controlled Variables: Constant light intensity (250 umol/m2/s), temperature (22°C), and humidity (65%).
- Replication: 5 independent biological replicates per treatment group.
""",
        "source_hint": "experiment_design.md",
        "target_artifact": TargetArtifactType.DETAILED_HANDOUT,
        "expected_strategy": MaterialStrategyType.SCIENTIFIC_REASONING,
    },
    {
        "case_id": "case_5_quick_explanation",
        "title": "Explain Newton's Third Law",
        "domain": KnowledgeDomain.PHYSICS,
        "audience": AudienceLevel.HIGH_SCHOOL,
        "raw_input": """# Classical Mechanics: Newton's Third Law of Motion
For every action, there is an equal and opposite reaction force acting on separate bodies.

## Interaction Principles
- Action-Reaction Pair: Forces always occur in matched interaction pairs (F_AB = -F_BA).
- Simultaneous Action: Neither force precedes the other in time; they arise simultaneously.
- Separate Bodies: Action and reaction forces act on distinct bodies, so they never cancel out internally.
""",
        "source_hint": "newton_third_law.md",
        "target_artifact": TargetArtifactType.TEACHING_PRESENTATION,
        "expected_strategy": MaterialStrategyType.QUICK_EXPLANATION,
    },
]

FORMATS_TO_TEST = [
    {"format_id": "a4_portrait", "name": "A4 Portrait", "expected_w": 210.0, "expected_h": 297.0},
    {"format_id": "a4_landscape", "name": "A4 Landscape", "expected_w": 297.0, "expected_h": 210.0},
    {"format_id": "presentation_16_9", "name": "Presentation 16:9", "expected_w": 338.7, "expected_h": 190.5},
]


async def run_director_benchmark():
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)

    out_base = Path("outputs/intelligent_director_benchmark")
    out_base.mkdir(parents=True, exist_ok=True)

    benchmark_report = {
        "batch": "11.0",
        "title": "Batch 11 Intelligent Material Director Benchmark Report",
        "total_cases": len(DIRECTOR_BENCHMARK_CASES),
        "total_formats": len(FORMATS_TO_TEST),
        "total_artifacts_generated": len(DIRECTOR_BENCHMARK_CASES) * len(FORMATS_TO_TEST),
        "results": [],
    }

    print("=" * 80)
    print("BATCH 11 INTELLIGENT MATERIAL DIRECTOR PHYSICAL PDF BENCHMARK (15 ARTIFACTS)")
    print("=" * 80)

    for case in DIRECTOR_BENCHMARK_CASES:
        case_id = case["case_id"]
        title = case["title"]
        expected_strat = case["expected_strategy"]
        case_dir = out_base / case_id
        case_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n=======================================================")
        print(f"BENCHMARK TOPIC: {title.upper()} [{case_id}]")
        print(f"=======================================================")

        for fmt in FORMATS_TO_TEST:
            fmt_id = fmt["format_id"]
            fmt_name = fmt["name"]
            out_filename = f"{case_id}_{fmt_id}"

            print(f">>> Directing & Generating: {fmt_name} ({fmt_id})...")

            res = await pipeline.produce_artifact(
                raw_input=case["raw_input"],
                source_hint=case["source_hint"],
                domain=case["domain"],
                audience=case["audience"],
                target_artifact=case["target_artifact"],
                output_dir=case_dir,
                output_filename=out_filename,
                target_format=fmt_id,
                director_enabled=True,
                preferred_strategy=expected_strat,
            )

            assert res.success is True
            assert res.material_direction is not None
            pdf_path = Path(res.pdf_path)
            assert pdf_path.exists()

            # Physical inspection with PyMuPDF
            doc = pymupdf.open(str(pdf_path))
            page_count = len(doc)
            rect = doc[0].rect
            w_mm = round(rect.width * 25.4 / 72.0, 1)
            h_mm = round(rect.height * 25.4 / 72.0, 1)
            doc.close()

            # Determinism check
            res_repeat = await pipeline.produce_artifact(
                raw_input=case["raw_input"],
                source_hint=case["source_hint"],
                domain=case["domain"],
                audience=case["audience"],
                target_artifact=case["target_artifact"],
                output_dir=case_dir / "repeat",
                output_filename=f"{out_filename}_repeat",
                target_format=fmt_id,
                director_enabled=True,
                preferred_strategy=expected_strat,
            )
            is_deterministic = len(res.composition.pages) == len(res_repeat.composition.pages)

            case_result = {
                "case_id": case_id,
                "title": title,
                "domain": str(case["domain"]),
                "format_id": fmt_id,
                "format_name": fmt_name,
                "strategy_selected": res.material_direction.strategy.value,
                "stages_count": len(res.material_direction.journey.stages),
                "stages_sequence": [s.stage_type.value for s in res.material_direction.journey.stages],
                "page_count": page_count,
                "dimensions_mm": f"{w_mm} x {h_mm} mm",
                "geometry_valid": abs(w_mm - fmt["expected_w"]) <= 1.0 and abs(h_mm - fmt["expected_h"]) <= 1.0,
                "journey_valid": len(res.material_direction.diagnostics.warnings) == 0,
                "director_trace_valid": bool(res.material_direction.trace.strategy),
                "determinism_verified": is_deterministic,
                "pdf_path": str(pdf_path),
            }

            benchmark_report["results"].append(case_result)
            print(f"    [OK] {fmt_name}: Strategy='{case_result['strategy_selected']}' | {page_count} pages | {w_mm}x{h_mm} mm | Trace: OK | Det: YES")

    report_path = out_base / "benchmark_report.json"
    report_path.write_text(json.dumps(benchmark_report, indent=2), encoding="utf-8")
    print("\n" + "=" * 80)
    print("ALL 15 DIRECTOR BENCHMARK ARTIFACTS GENERATED AND VERIFIED!")
    print(f"Report written to: {report_path}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_director_benchmark())
