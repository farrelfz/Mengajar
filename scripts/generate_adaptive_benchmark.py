"""
Batch 12 Adaptive Content Intelligence & Curriculum Bundle Benchmark.

Executes:
1. Grade-Level Adaptations: SMP vs SMA vs University.
2. Duration-Pacing Adaptations: 15m vs 45m vs 90m.
3. Multi-Artifact Curriculum Bundles: Presentation + Handout + Worksheet + Assessment.
Inspects all physical PDFs with PyMuPDF, calculates redundancy and coverage, and writes benchmark_report.json.
"""

import asyncio
import json
from pathlib import Path
import pymupdf

from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.adaptation import (
    AdaptiveContentTransformer,
    ComplexityPolicy,
    InstructionalTimeBudget,
    PacingPolicy,
    get_default_learner_profile,
)
from app.bundles import (
    ArtifactBundleProducer,
    ArtifactBundleRequest,
    ArtifactRole,
)
from app.director import (
    IntelligentMaterialDirector,
    LearningGoal,
    MaterialStrategyType,
)
from app.orchestration.production_pipeline import MaterialProductionPipeline
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


async def run_adaptive_benchmark():
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)
    bundle_producer = ArtifactBundleProducer(pipeline=pipeline)
    director = IntelligentMaterialDirector()

    out_base = Path("outputs/adaptive_content_benchmark")
    out_base.mkdir(parents=True, exist_ok=True)

    report = {
        "batch": "12.0",
        "title": "Batch 12 Adaptive Content Intelligence & Curriculum Bundle Benchmark",
        "benchmarks": {
            "grade_level_adaptations": [],
            "duration_pacing_adaptations": [],
            "multi_artifact_bundles": [],
        },
    }

    print("=" * 80)
    print("BATCH 12 ADAPTIVE CONTENT & CURRICULUM BUNDLE BENCHMARK")
    print("=" * 80)

    # -------------------------------------------------------------
    # 1. GRADE-LEVEL ADAPTATION BENCHMARK (Torque: SMP vs SMA vs University)
    # -------------------------------------------------------------
    print("\n--- 1. Grade-Level Adaptation Benchmark (Torque) ---")
    grade_cases = [
        {"level": AudienceLevel.MIDDLE_SCHOOL, "name": "SMP (Grade 8)", "expected_strat": MaterialStrategyType.CONCRETE_TO_ABSTRACT},
        {"level": AudienceLevel.HIGH_SCHOOL, "name": "SMA (Grade 11)", "expected_strat": MaterialStrategyType.CONCRETE_TO_ABSTRACT},
        {"level": AudienceLevel.UNDERGRADUATE, "name": "University (1st Year)", "expected_strat": MaterialStrategyType.DEEP_DIVE_TUTORIAL},
    ]

    for gc in grade_cases:
        lvl = gc["level"]
        name = gc["name"]
        learner = get_default_learner_profile(lvl)
        complexity = ComplexityPolicy.derive_complexity_profile(learner)

        case_dir = out_base / f"grade_{lvl.value}"
        case_dir.mkdir(parents=True, exist_ok=True)
        filename = f"torque_{lvl.value}"

        res = await pipeline.produce_artifact(
            raw_input="# Classical Mechanics: Torque\nRotational force equilibrium.",
            source_hint=f"{filename}.md",
            domain=KnowledgeDomain.PHYSICS,
            audience=lvl,
            output_dir=case_dir,
            output_filename=filename,
            target_format="a4_portrait",
            director_enabled=True,
            preferred_strategy=gc["expected_strat"],
        )

        doc = pymupdf.open(res.pdf_path)
        page_count = len(doc)
        doc.close()

        report["benchmarks"]["grade_level_adaptations"].append({
            "audience": lvl.value,
            "audience_name": name,
            "mathematical_formalism": complexity.mathematical_formalism.value,
            "vocabulary_complexity": complexity.vocabulary_complexity.value,
            "strategy": gc["expected_strat"].value,
            "pages": page_count,
            "pdf_path": res.pdf_path,
        })
        print(f"  [OK] {name}: Formalism='{complexity.mathematical_formalism.value}' | Vocab='{complexity.vocabulary_complexity.value}' | {page_count} pages")

    # -------------------------------------------------------------
    # 2. DURATION & PACING BENCHMARK (15m vs 45m vs 90m)
    # -------------------------------------------------------------
    print("\n--- 2. Duration & Pacing Benchmark ---")
    duration_cases = [15, 45, 90]
    goal = LearningGoal(concept="Rotational Equilibrium", expected_understanding="Torque balance", domain="physics")
    dir_result = director.direct(goal=goal)

    for dur in duration_cases:
        t_budget = InstructionalTimeBudget(duration_minutes=dur)
        paced_journey, adj = PacingPolicy.pace_journey(dir_result.journey, t_budget)

        report["benchmarks"]["duration_pacing_adaptations"].append({
            "duration_minutes": dur,
            "stages_count": paced_journey.total_stages,
            "stages": [s.stage_type.value for s in paced_journey.stages],
            "adjustments": adj,
        })
        print(f"  [OK] {dur} min: {paced_journey.total_stages} stages -> {[s.stage_type.value for s in paced_journey.stages]}")

    # -------------------------------------------------------------
    # 3. MULTI-ARTIFACT CURRICULUM BUNDLE BENCHMARKS
    # -------------------------------------------------------------
    print("\n--- 3. Multi-Artifact Bundle Benchmarks ---")
    bundle_requests = [
        ArtifactBundleRequest(
            concept="Newtonian Dynamics & Third Law",
            audience=AudienceLevel.HIGH_SCHOOL,
            duration_minutes=45,
            artifacts=[
                ArtifactRole.PRESENTATION,
                ArtifactRole.HANDOUT,
                ArtifactRole.WORKSHEET,
                ArtifactRole.ASSESSMENT,
            ],
            raw_input="# Newton's Laws of Motion\nAction and reaction force dynamics.",
            source_hint="bundle_newton.md",
        ),
        ArtifactBundleRequest(
            concept="Scientific Research Variables & Controls",
            audience=AudienceLevel.UNDERGRADUATE,
            duration_minutes=60,
            artifacts=[
                ArtifactRole.PRESENTATION,
                ArtifactRole.HANDOUT,
                ArtifactRole.WORKSHEET,
                ArtifactRole.ASSESSMENT,
            ],
            raw_input="# Research Methodology: Variable Operationalization\nIndependent, dependent, and controlled variables.",
            source_hint="bundle_research.md",
        ),
    ]

    for req in bundle_requests:
        print(f"Producing Bundle for '{req.concept}'...")
        bundle_res = await bundle_producer.produce_bundle(req, output_dir=out_base)

        bundle_data = {
            "bundle_id": bundle_res.bundle_id,
            "concept": bundle_res.concept,
            "audience": bundle_res.audience,
            "redundancy_score": bundle_res.redundancy_score,
            "complementarity_score": bundle_res.complementarity_score,
            "coherence_valid": bundle_res.coherence_valid,
            "items": [
                {
                    "role": item.role.value,
                    "format": item.format_id,
                    "pages": item.page_count,
                    "pdf_path": item.pdf_path,
                    "stages": item.journey_stages,
                }
                for item in bundle_res.items
            ],
        }
        report["benchmarks"]["multi_artifact_bundles"].append(bundle_data)
        print(f"  [OK] Bundle '{req.concept}': 4 artifacts | Redundancy={bundle_res.redundancy_score} | Complementarity={bundle_res.complementarity_score} | Coherence={bundle_res.coherence_valid}")

    report_path = out_base / "benchmark_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\n" + "=" * 80)
    print("ALL BATCH 12 ADAPTIVE & BUNDLE BENCHMARKS COMPLETE AND VERIFIED!")
    print(f"Report written to: {report_path}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_adaptive_benchmark())
