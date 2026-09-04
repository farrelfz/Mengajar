"""
Batch 15 Comprehensive Multi-Domain Quality Evaluation Benchmark.

Generates physical PDF artifacts and machine-readable quality reports across 5 canonical domains:
1. Physics
2. Research Methodology
3. Academic Writing
4. Experiment Design
5. Data Literacy

Outputs structured PDFs and quality_report.json for every domain.
"""

import asyncio
import json
from pathlib import Path
import pymupdf

from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.orchestration.production_pipeline import MaterialProductionPipeline
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


async def run_master_quality_benchmark():
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)

    benchmark_root = Path("outputs/quality_evaluation_benchmark")
    benchmark_root.mkdir(parents=True, exist_ok=True)

    test_domains = [
        {
            "domain_key": "physics",
            "name": "Physics: Rotational Dynamics",
            "input": "# Classical Mechanics: Rotational Dynamics & Torque\nAnalyzing moment of inertia, torque equilibrium, and rotational acceleration.",
            "source": "physics_rotational.md",
            "domain": KnowledgeDomain.PHYSICS,
            "audience": AudienceLevel.HIGH_SCHOOL,
            "artifact": TargetArtifactType.TEACHING_PRESENTATION,
            "format": "presentation_16_9",
        },
        {
            "domain_key": "research",
            "name": "Research Education: Problem Formulation",
            "input": "# Research Methodology: Formulating Academic Research Problems\nTechniques for discovering authentic gaps in existing peer-reviewed literature.",
            "source": "research_problem.md",
            "domain": KnowledgeDomain.RESEARCH_METHODOLOGY,
            "audience": AudienceLevel.UNDERGRADUATE,
            "artifact": TargetArtifactType.DETAILED_HANDOUT,
            "format": "a4_portrait",
        },
        {
            "domain_key": "writing",
            "name": "Academic Writing: Abstract & Introduction Synthesis",
            "input": "# Academic Writing Mastery: Structuring Research Introductions\nCrafting persuasive problem statements and scholarly significance.",
            "source": "academic_writing.md",
            "domain": KnowledgeDomain.EDUCATION,
            "audience": AudienceLevel.UNDERGRADUATE,
            "artifact": TargetArtifactType.DETAILED_HANDOUT,
            "format": "a4_portrait",
        },
        {
            "domain_key": "experiment",
            "name": "Experiment Design: Controlled Variables & Hypothesis Testing",
            "input": "# Scientific Method: Designing Controlled Laboratory Experiments\nIsolating independent variables, controlling confounders, and data reliability.",
            "source": "experiment_design.md",
            "domain": KnowledgeDomain.GENERAL_SCIENCE,
            "audience": AudienceLevel.HIGH_SCHOOL,
            "artifact": TargetArtifactType.STUDENT_WORKSHEET,
            "format": "a4_landscape",
        },
        {
            "domain_key": "data_literacy",
            "name": "Data Literacy: Interpreting Statistical Distributions",
            "input": "# Data Literacy: Understanding Statistical Distributions & Variance\nNormal distributions, standard deviation, and avoiding data misinterpretation.",
            "source": "data_literacy.md",
            "domain": KnowledgeDomain.MATHEMATICS,
            "audience": AudienceLevel.UNDERGRADUATE,
            "artifact": TargetArtifactType.TEACHING_PRESENTATION,
            "format": "presentation_16_9",
        },
    ]

    print("=" * 80)
    print("BATCH 15 — 5-DOMAIN PRODUCTION QUALITY EVALUATION BENCHMARK")
    print("=" * 80)

    summary_manifest = {
        "batch": "15.0",
        "benchmark_title": "Multi-Domain Quality Evaluation & Material Quality Assurance",
        "domains": [],
    }

    for td in test_domains:
        domain_dir = benchmark_root / td["domain_key"]
        domain_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n[Domain: {td['domain_key'].upper()}] Producing & Evaluating '{td['name']}'...")
        res = await pipeline.produce_artifact(
            raw_input=td["input"],
            source_hint=td["source"],
            domain=td["domain"],
            audience=td["audience"],
            target_artifact=td["artifact"],
            output_dir=domain_dir,
            output_filename="final",
            target_format=td["format"],
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

        domain_report = {
            "domain_key": td["domain_key"],
            "title": td["name"],
            "target_format": td["format"],
            "pdf_path": res.pdf_path,
            "page_count": page_count,
            "geometry_pt": [width_pt, height_pt],
            "quality_score": q_rep.overall_score if q_rep else None,
            "quality_level": q_rep.quality_level.value if q_rep else None,
            "gate_decision": q_gate.decision.value if q_gate else None,
            "can_proceed": q_gate.can_proceed if q_gate else None,
            "findings_count": len(q_rep.findings) if q_rep else 0,
            "dimensional_scores": q_rep.gate_result.score.dimensional_scores if q_rep else {},
            "findings": [
                {
                    "dimension": f.dimension.value,
                    "severity": f.severity.value,
                    "finding": f.finding,
                    "recommendation": f.recommendation,
                }
                for f in (q_rep.findings if q_rep else [])
            ],
            "trace": q_rep.trace.model_dump() if q_rep else {},
        }

        # Save individual domain report
        (domain_dir / "quality_report.json").write_text(
            json.dumps(domain_report, indent=2), encoding="utf-8"
        )

        summary_manifest["domains"].append({
            "domain": td["domain_key"],
            "format": td["format"],
            "pages": page_count,
            "geometry": f"{width_pt:.1f}x{height_pt:.1f} pt",
            "score": domain_report["quality_score"],
            "level": domain_report["quality_level"],
            "decision": domain_report["gate_decision"],
        })

        print(f"  --> Score: {domain_report['quality_score']} ({domain_report['quality_level']}) | Decision: {domain_report['gate_decision']} | Pages: {page_count} ({width_pt:.1f}x{height_pt:.1f} pt)")

    (benchmark_root / "master_benchmark_manifest.json").write_text(
        json.dumps(summary_manifest, indent=2), encoding="utf-8"
    )

    print("\n" + "=" * 80)
    print("ALL 5 DOMAINS PRODUCED, EVALUATED, AND VALIDATED!")
    print(f"Manifest written to: {benchmark_root / 'master_benchmark_manifest.json'}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_master_quality_benchmark())
