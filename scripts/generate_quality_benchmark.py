"""
Batch 15 Quality Evaluation & Quality Gate Benchmark.

Executes end-to-end production with automated multi-dimensional quality evaluation,
inspects physical PDF geometry with PyMuPDF, and writes quality_report.json.
"""

import asyncio
import json
from pathlib import Path
import pymupdf

from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.orchestration.production_pipeline import MaterialProductionPipeline
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


async def run_quality_benchmark():
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)

    out_base = Path("outputs/quality_evaluation_benchmark")
    out_base.mkdir(parents=True, exist_ok=True)

    report_data = {
        "batch": "15.0",
        "title": "Batch 15 Multi-Dimensional Quality Evaluation Benchmark",
        "benchmarks": [],
    }

    print("=" * 80)
    print("BATCH 15 QUALITY EVALUATION BENCHMARK")
    print("=" * 80)

    test_cases = [
        {
            "name": "Physics: Rotational Dynamics",
            "input": "# Classical Mechanics: Rotational Torque\nAnalyzing torque, lever arms, and equilibrium dynamics.",
            "source": "physics_torque.md",
            "domain": KnowledgeDomain.PHYSICS,
            "audience": AudienceLevel.HIGH_SCHOOL,
            "artifact": TargetArtifactType.TEACHING_PRESENTATION,
            "format": "presentation_16_9",
            "filename": "physics_torque_presentation",
        },
        {
            "name": "Research Education: Problem Formulation",
            "input": "# Research Methodology: Formulating Problems\nTechniques for discovering authentic gaps in academic literature.",
            "source": "research_problem.md",
            "domain": KnowledgeDomain.RESEARCH_METHODOLOGY,
            "audience": AudienceLevel.UNDERGRADUATE,
            "artifact": TargetArtifactType.DETAILED_HANDOUT,
            "format": "a4_portrait",
            "filename": "research_problem_handout",
        },
    ]

    for tc in test_cases:
        print(f"\nProducing & Evaluating: {tc['name']} ({tc['format']})...")
        res = await pipeline.produce_artifact(
            raw_input=tc["input"],
            source_hint=tc["source"],
            domain=tc["domain"],
            audience=tc["audience"],
            target_artifact=tc["artifact"],
            output_dir=out_base,
            output_filename=tc["filename"],
            target_format=tc["format"],
            director_enabled=True,
            evaluate_quality=True,
        )

        doc = pymupdf.open(res.pdf_path)
        page_count = len(doc)
        rect = doc[0].rect
        width_pt, height_pt = rect.width, rect.height
        doc.close()

        q_rep = res.quality_report
        q_gate = res.quality_gate

        case_entry = {
            "case_name": tc["name"],
            "format": tc["format"],
            "pdf_path": res.pdf_path,
            "page_count": page_count,
            "geometry_pt": [width_pt, height_pt],
            "quality_score": q_rep.overall_score if q_rep else None,
            "gate_decision": q_gate.decision.value if q_gate else None,
            "can_proceed": q_gate.can_proceed if q_gate else None,
            "findings_count": len(q_rep.findings) if q_rep else 0,
            "findings": [
                {
                    "dimension": f.dimension.value,
                    "severity": f.severity.value,
                    "finding": f.finding,
                    "recommendation": f.recommendation,
                }
                for f in (q_rep.findings if q_rep else [])
            ],
            "dimensional_scores": q_rep.gate_result.score.dimensional_scores if q_rep else {},
        }
        report_data["benchmarks"].append(case_entry)

        print(f"  [OK] Decision: {case_entry['gate_decision']} | Score: {case_entry['quality_score']} | Pages: {page_count} | Geometry: {width_pt:.1f}x{height_pt:.1f} pt")

    json_path = out_base / "quality_report.json"
    json_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    print("\n" + "=" * 80)
    print(f"BATCH 15 QUALITY BENCHMARK COMPLETE! Saved to {json_path}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_quality_benchmark())
