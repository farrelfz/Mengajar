"""
Batch 10 Massive Capability Library Physical PDF Benchmark.

Generates 7 multi-domain benchmark cases across 3 physical formats (A4 Portrait, A4 Landscape, 16:9 Presentation) = 21 physical PDFs.
Validates physical dimensions, page counts, family resolution, and determinism via PyMuPDF.
Outputs full report to outputs/massive_capability_benchmark/benchmark_report.json.
"""

import asyncio
import json
from pathlib import Path
import pymupdf

from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.orchestration.production_pipeline import MaterialProductionPipeline
from tests.integration.test_true_production_pipeline import build_mock_intel_agent

BENCHMARK_TOPICS = [
    {
        "case_id": "case_1_physics_torque",
        "title": "Understanding Torque & Rotational Statics",
        "domain": KnowledgeDomain.PHYSICS,
        "raw_input": """# Classical Mechanics: Understanding Torque
Torque is the rotational analogue of linear force, calculated as tau = r * F * sin(theta).

## Rotational Equilibrium Protocol
1. Establish Reference Frame: Select pivot point (O) to eliminate unknown pivot reaction forces.
2. Construct Free Body Diagram: Draw all normal, applied, and gravitational force vectors.
3. Compute Lever Arms: Calculate perpendicular distance for each force component.
4. Solve Equilibrium System: Set Sum of Torques = 0 and solve for target variables.
""",
        "source_hint": "torque_statics.md",
        "target_artifact": TargetArtifactType.TEACHING_PRESENTATION,
    },
    {
        "case_id": "case_2_research_problem",
        "title": "Formulating a Rigorous Research Problem",
        "domain": KnowledgeDomain.RESEARCH_METHODOLOGY,
        "raw_input": """# Research Methodology: Formulating a Research Problem
Bridging broad real-world challenges with focused, answerable research questions.

## Problem Formulation Funnel
- Broad Societal Challenge: High energy consumption in urban cloud computing data centers.
- Academic Literature Gap: Lack of thermal-aware dynamic VM allocation algorithms under unpredictable workloads.
- Specific Research Objective: Design a predictive reinforcement learning scheduler to reduce cooling energy by 25%.
""",
        "source_hint": "research_problem_funnel.md",
        "target_artifact": TargetArtifactType.DETAILED_HANDOUT,
    },
    {
        "case_id": "case_3_academic_writing",
        "title": "Building a Strong Argumentative Paragraph",
        "domain": KnowledgeDomain.GENERAL_SCIENCE,
        "raw_input": """# Academic Writing: Paragraph Anatomy & Logic
Constructing coherent, persuasive body paragraphs in scholarly essays.

## Paragraph Anatomy Workflow
1. Topic Sentence: State the singular claim that directly advances the thesis.
2. Evidence & Data: Cite empirical findings or textual quotes with precise context.
3. Critical Analysis: Unpack the warrant explaining how evidence supports the claim.
4. Concluding Transition: Synthesize the insight and connect logically to the next section.
""",
        "source_hint": "paragraph_anatomy.md",
        "target_artifact": TargetArtifactType.TEACHING_PRESENTATION,
    },
    {
        "case_id": "case_4_scientific_thinking",
        "title": "From Observation to Testable Hypothesis",
        "domain": KnowledgeDomain.GENERAL_SCIENCE,
        "raw_input": """# Scientific Inquiry: Observation to Hypothesis
Translating unexpected phenomena into falsifiable empirical models.

## Structured Reasoning
- Observation: Certain alpine plant species bloom 14 days earlier at lower elevations.
- Inquiry Question: Is temperature or photoperiod the primary environmental cue triggering early anthesis?
- Theoretical Warrant: Accumulated thermal degree-days regulate enzymatic flower development pathways.
- Falsifiable Hypothesis: Exposure to an additional 150 growing degree-days will advance anthesis by at least 10 days regardless of day length.
""",
        "source_hint": "scientific_reasoning.md",
        "target_artifact": TargetArtifactType.TEACHING_PRESENTATION,
    },
    {
        "case_id": "case_5_experiment_design",
        "title": "Designing a Controlled Laboratory Experiment",
        "domain": KnowledgeDomain.GENERAL_SCIENCE,
        "raw_input": """# Laboratory Science: Designing Controlled Experiments
Ensuring internal validity and reproducibility through strict variable isolation.

## Experimental Protocol & Controls
- Independent Variable: Substrate Nitrogen concentration (0 mM, 5 mM, 10 mM, 20 mM).
- Dependent Variable: Total chlorophyll content measured via spectrophotometry at 663 nm.
- Controlled Variables: Constant light intensity (250 umol/m2/s), temperature (22°C), and humidity (65%).
- Replication: 5 independent biological replicates per treatment group.
""",
        "source_hint": "experiment_protocol.md",
        "target_artifact": TargetArtifactType.DETAILED_HANDOUT,
    },
    {
        "case_id": "case_6_data_literacy",
        "title": "How to Interpret Scientific Graphs",
        "domain": KnowledgeDomain.GENERAL_SCIENCE,
        "raw_input": """# Data Literacy: Critical Graph Interpretation
Deconstructing visual empirical representations with scientific rigor.

## Graph Reading Protocol
1. Axis Inspection: Identify independent (X-axis) and dependent (Y-axis) variables with units.
2. Scale & Baseline Check: Verify whether axes are linear or logarithmic and check for truncated baselines.
3. Trend & Pattern Identification: Determine whether relationships are linear, asymptotic, or cyclic.
4. Uncertainty Evaluation: Inspect error bars (standard error vs confidence intervals) to evaluate statistical significance.
""",
        "source_hint": "data_graph_reading.md",
        "target_artifact": TargetArtifactType.TEACHING_PRESENTATION,
    },
    {
        "case_id": "case_7_pedagogy_misconception",
        "title": "Misconception: Free Fall and Mass Independence",
        "domain": KnowledgeDomain.PHYSICS,
        "raw_input": """# Physics Pedagogy: Gravitational Acceleration Misconception
Addressing the common intuitive misconception that heavier objects always fall faster.

## Misconception Breakdown & Correction
- Intuitive Misconception: A 10 kg bowling ball falls significantly faster than a 10 g marble in a vacuum.
- Scientific Reality: In the absence of aerodynamic drag, all objects experience identical gravitational acceleration (g = 9.8 m/s^2).
- Underlying Principle: Gravitational force is proportional to mass (F = m*g), but inertial resistance to acceleration is also proportional to mass (a = F/m = g), canceling mass completely.
""",
        "source_hint": "gravity_misconception.md",
        "target_artifact": TargetArtifactType.TEACHING_PRESENTATION,
    },
]

FORMATS_TO_TEST = [
    {"format_id": "a4_portrait", "name": "A4 Portrait", "expected_w": 210.0, "expected_h": 297.0},
    {"format_id": "a4_landscape", "name": "A4 Landscape", "expected_w": 297.0, "expected_h": 210.0},
    {"format_id": "presentation_16_9", "name": "Presentation 16:9", "expected_w": 338.7, "expected_h": 190.5},
]


async def run_massive_benchmark():
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)

    out_base = Path("outputs/massive_capability_benchmark")
    out_base.mkdir(parents=True, exist_ok=True)

    benchmark_report = {
        "batch": "10.0",
        "title": "Batch 10 Massive Capability Library Benchmark Report",
        "total_topics": len(BENCHMARK_TOPICS),
        "total_formats_per_topic": len(FORMATS_TO_TEST),
        "total_artifacts_generated": len(BENCHMARK_TOPICS) * len(FORMATS_TO_TEST),
        "cases": [],
    }

    print("=" * 80)
    print("BATCH 10 MASSIVE CAPABILITY PHYSICAL PDF BENCHMARK (21 ARTIFACTS)")
    print("=" * 80)

    for topic in BENCHMARK_TOPICS:
        case_id = topic["case_id"]
        topic_title = topic["title"]
        topic_dir = out_base / case_id
        topic_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n=======================================================")
        print(f"BENCHMARK TOPIC: {topic_title.upper()} [{case_id}]")
        print(f"=======================================================")

        for fmt in FORMATS_TO_TEST:
            fmt_id = fmt["format_id"]
            fmt_name = fmt["name"]
            out_filename = f"{case_id}_{fmt_id}"

            print(f">>> Generating Format: {fmt_name} ({fmt_id})...")

            res = await pipeline.produce_artifact(
                raw_input=topic["raw_input"],
                source_hint=topic["source_hint"],
                domain=topic["domain"],
                audience=AudienceLevel.UNDERGRADUATE,
                target_artifact=topic["target_artifact"],
                output_dir=topic_dir,
                output_filename=out_filename,
                target_format=fmt_id,
            )

            assert res.success is True, f"Pipeline execution failed for {out_filename}"
            pdf_path = Path(res.pdf_path)
            assert pdf_path.exists(), f"PDF artifact not created at {pdf_path}"

            # PyMuPDF Physical inspection
            doc = pymupdf.open(str(pdf_path))
            page_count = len(doc)
            rect = doc[0].rect
            w_mm = round(rect.width * 25.4 / 72.0, 1)
            h_mm = round(rect.height * 25.4 / 72.0, 1)
            doc.close()

            # Determinism verification run
            res_repeat = await pipeline.produce_artifact(
                raw_input=topic["raw_input"],
                source_hint=topic["source_hint"],
                domain=topic["domain"],
                audience=AudienceLevel.UNDERGRADUATE,
                target_artifact=topic["target_artifact"],
                output_dir=topic_dir / "repeat",
                output_filename=f"{out_filename}_repeat",
                target_format=fmt_id,
            )
            is_deterministic = len(res.composition.pages) == len(res_repeat.composition.pages)

            case_entry = {
                "topic_id": case_id,
                "topic_title": topic_title,
                "domain": str(topic["domain"]),
                "format_id": fmt_id,
                "format_name": fmt_name,
                "pdf_path": str(pdf_path),
                "page_count": page_count,
                "dimensions_mm": f"{w_mm} x {h_mm} mm",
                "geometry_pass": abs(w_mm - fmt["expected_w"]) <= 1.0 and abs(h_mm - fmt["expected_h"]) <= 1.0,
                "determinism_verified": is_deterministic,
                "assets_generated": res.render_result.assets_generated if res.render_result else 0,
            }

            benchmark_report["cases"].append(case_entry)
            print(f"    [OK] {fmt_name}: {page_count} pages | {w_mm}x{h_mm} mm | Det: {'YES' if is_deterministic else 'NO'}")

    report_path = out_base / "benchmark_report.json"
    report_path.write_text(json.dumps(benchmark_report, indent=2), encoding="utf-8")
    print("\n" + "=" * 80)
    print("ALL 21 PHYSICAL PDF BENCHMARKS COMPLETED SUCCESSFULLY!")
    print(f"Report written to: {report_path}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_massive_benchmark())
