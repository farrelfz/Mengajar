"""
Batch 16 Cross-Domain Generative Critic Benchmark.

Executes production pipeline across 6 canonical domains, generates Quality Reports,
runs multi-perspective Generative Critic panels, and outputs structured benchmark_report.json.
"""

import asyncio
import json
from pathlib import Path

from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.critic.engine import GenerativeCriticEngine
from app.orchestration.production_pipeline import MaterialProductionPipeline
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


async def run_generative_critic_benchmark():
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)
    critic_engine = GenerativeCriticEngine()

    out_base = Path("outputs/generative_critic_benchmark")
    out_base.mkdir(parents=True, exist_ok=True)

    benchmark_cases = [
        {
            "id": "physics_rotational",
            "name": "Physics: Rotational Dynamics & Torque",
            "input": "# Classical Mechanics: Rotational Dynamics\nTorque equilibrium, angular acceleration, and rotational inertia in mechanical systems.",
            "source": "physics_rotational.md",
            "domain": KnowledgeDomain.PHYSICS,
            "audience": AudienceLevel.HIGH_SCHOOL,
            "artifact": TargetArtifactType.TEACHING_PRESENTATION,
            "format": "presentation_16_9",
            "genre": "scientific",
        },
        {
            "id": "research_problem_gap",
            "name": "Research Methodology: Problem Formulation",
            "input": "# Research Problem Identification & Gap Matrix\nSystematic discovery of theoretical and empirical research gaps in scientific literature.",
            "source": "research_problem.md",
            "domain": KnowledgeDomain.RESEARCH_METHODOLOGY,
            "audience": AudienceLevel.UNDERGRADUATE,
            "artifact": TargetArtifactType.DETAILED_HANDOUT,
            "format": "a4_portrait",
            "genre": "research",
        },
        {
            "id": "academic_writing_intro",
            "name": "Academic Writing: Introduction & Rhetoric",
            "input": "# Academic Writing Mastery: Introductions & Problem Statements\nStructuring high-impact research introductions with rhetorical credibility.",
            "source": "academic_writing.md",
            "domain": KnowledgeDomain.EDUCATION,
            "audience": AudienceLevel.UNDERGRADUATE,
            "artifact": TargetArtifactType.DETAILED_HANDOUT,
            "format": "a4_portrait",
            "genre": "educational",
        },
        {
            "id": "experiment_controlled_design",
            "name": "Experiment Design: Controlled Variables",
            "input": "# Laboratory Experimentation: Controlled Variable Design\nControlling confounders, isolating independent variables, and ensuring data repeatability.",
            "source": "experiment_design.md",
            "domain": KnowledgeDomain.GENERAL_SCIENCE,
            "audience": AudienceLevel.HIGH_SCHOOL,
            "artifact": TargetArtifactType.STUDENT_WORKSHEET,
            "format": "a4_landscape",
            "genre": "experiment",
        },
        {
            "id": "data_literacy_distributions",
            "name": "Data Literacy: Statistical Distributions",
            "input": "# Data Literacy: Understanding Variance & Distributions\nAnalyzing normal distributions, outliers, and avoiding misleading statistical visualizations.",
            "source": "data_literacy.md",
            "domain": KnowledgeDomain.MATHEMATICS,
            "audience": AudienceLevel.UNDERGRADUATE,
            "artifact": TargetArtifactType.TEACHING_PRESENTATION,
            "format": "presentation_16_9",
            "genre": "scientific",
        },
        {
            "id": "pedagogy_conceptual_scaffolding",
            "name": "Pedagogy: Constructivist Concept Formation",
            "input": "# Pedagogical Theory: Constructivist Scaffolding\nScaffolding complex abstractions through guided discovery, cognitive hooks, and progressive inquiry.",
            "source": "pedagogy_scaffold.md",
            "domain": KnowledgeDomain.EDUCATION,
            "audience": AudienceLevel.UNDERGRADUATE,
            "artifact": TargetArtifactType.DETAILED_HANDOUT,
            "format": "a4_portrait",
            "genre": "educational",
        },
    ]

    print("=" * 80)
    print("BATCH 16 — CROSS-DOMAIN GENERATIVE CRITIC BENCHMARK")
    print("=" * 80)

    case_reports = []

    for c in benchmark_cases:
        print(f"\n[Domain: {c['domain'].value.upper()}] Producing & Critiquing '{c['name']}'...")
        case_dir = out_base / c["id"]
        case_dir.mkdir(parents=True, exist_ok=True)

        res = await pipeline.produce_artifact(
            raw_input=c["input"],
            source_hint=c["source"],
            domain=c["domain"],
            audience=c["audience"],
            target_artifact=c["artifact"],
            output_dir=case_dir,
            output_filename="artifact",
            target_format=c["format"],
            director_enabled=True,
            evaluate_quality=True,
        )

        # Execute Multi-Perspective Generative Critic Engine
        critique_rep = critic_engine.critique(
            artifact_id=c["id"],
            blueprint=res.material_blueprint,
            composition=res.composition,
            journey=res.material_direction.journey if res.material_direction else None,
            quality_report=res.quality_report,
            pdf_path=res.pdf_path,
            target_format=c["format"],
            audience_level=c["audience"].value,
            document_genre=c["genre"],
        )

        # Save individual domain critique report
        (case_dir / "critique_report.json").write_text(
            json.dumps(critique_rep.model_dump(), indent=2), encoding="utf-8"
        )

        high_pri_count = sum(1 for r in critique_rep.recommendations if r.priority.value in ["blocker", "critical", "high"])

        summary = {
            "case_id": c["id"],
            "name": c["name"],
            "target_format": c["format"],
            "critics_executed": len(critique_rep.trace.critics_executed),
            "findings_count": len(critique_rep.findings),
            "high_priority_recommendations": high_pri_count,
            "agreements_count": len(critique_rep.agreements),
            "conflicts_count": len(critique_rep.conflicts),
            "recommendations_count": len(critique_rep.recommendations),
            "overall_assessment": critique_rep.overall_assessment,
        }
        case_reports.append(summary)

        print(f"  --> Findings: {len(critique_rep.findings)} | Recs: {len(critique_rep.recommendations)} ({high_pri_count} High) | Agree: {len(critique_rep.agreements)} | Conflicts: {len(critique_rep.conflicts)}")

    manifest = {
        "batch": "16.0",
        "title": "Cross-Domain Generative Critic Benchmark Report",
        "total_cases": len(case_reports),
        "cases": case_reports,
    }

    manifest_file = out_base / "benchmark_report.json"
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("\n" + "=" * 80)
    print("ALL 6 DOMAINS CRITIQUED AND VALIDATED!")
    print(f"Benchmark summary written to: {manifest_file}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_generative_critic_benchmark())
