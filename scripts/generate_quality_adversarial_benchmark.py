"""
Batch 15.5 Adversarial Quality Benchmark: Good vs Bad Cases.

Generates real production runs across 5 Good Cases and 6 Deliberately Degraded/Bad Cases,
calculates mean score separation, gate distributions, and writes benchmark_report.json.
"""

import asyncio
import json
from pathlib import Path
import pymupdf

from app.blueprints.content import (
    AudienceLevel,
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    KnowledgeDomain,
    LearningObjective,
)
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.blueprints.pedagogical import (
    PedagogicalBlueprint,
    PedagogicalPattern,
    PedagogicalStep,
    SemanticStepType,
)
from app.blueprints.production import (
    ProductionBlueprint,
    ProductionRequirement,
    TargetArtifactType,
)
from app.composition.schemas import (
    ContentBlock,
    DocumentComposition,
    PageComposition,
    PageRegion,
    RegionRole,
)
from app.design.schemas import ComponentFamily
from app.director.contracts import (
    LearningJourney,
    LearningStage,
    LearningStageType,
    MaterialStrategyType,
)
from app.intelligence.schemas import DocumentMode
from app.orchestration.production_pipeline import MaterialProductionPipeline
from app.quality.engine import QualityEvaluationEngine
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


async def run_adversarial_benchmark():
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)

    out_base = Path("outputs/quality_adversarial_benchmark")
    out_base.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("BATCH 15.5 ADVERSARIAL QUALITY BENCHMARK: GOOD VS BAD DISCRIMINATION")
    print("=" * 80)

    # 1. GOOD PRODUCTION RUNS (5 Canonical Domains)
    good_cases_defs = [
        {
            "id": "good_physics",
            "name": "Physics: Rotational Torque",
            "input": "# Classical Mechanics: Rotational Dynamics & Torque\nAnalyzing moment of inertia, torque equilibrium, and rotational acceleration.",
            "source": "physics_rotational.md",
            "domain": KnowledgeDomain.PHYSICS,
            "audience": AudienceLevel.HIGH_SCHOOL,
            "artifact": TargetArtifactType.TEACHING_PRESENTATION,
            "format": "presentation_16_9",
        },
        {
            "id": "good_research",
            "name": "Research Education: Problem Formulation",
            "input": "# Research Methodology: Formulating Academic Research Problems\nTechniques for discovering authentic gaps in existing peer-reviewed literature.",
            "source": "research_problem.md",
            "domain": KnowledgeDomain.RESEARCH_METHODOLOGY,
            "audience": AudienceLevel.UNDERGRADUATE,
            "artifact": TargetArtifactType.DETAILED_HANDOUT,
            "format": "a4_portrait",
        },
        {
            "id": "good_writing",
            "name": "Academic Writing: Abstract & Introduction",
            "input": "# Academic Writing Mastery: Structuring Research Introductions\nCrafting persuasive problem statements and scholarly significance.",
            "source": "academic_writing.md",
            "domain": KnowledgeDomain.EDUCATION,
            "audience": AudienceLevel.UNDERGRADUATE,
            "artifact": TargetArtifactType.DETAILED_HANDOUT,
            "format": "a4_portrait",
        },
        {
            "id": "good_experiment",
            "name": "Experiment Design: Controlled Variables",
            "input": "# Scientific Method: Designing Controlled Laboratory Experiments\nIsolating independent variables, controlling confounders, and data reliability.",
            "source": "experiment_design.md",
            "domain": KnowledgeDomain.GENERAL_SCIENCE,
            "audience": AudienceLevel.HIGH_SCHOOL,
            "artifact": TargetArtifactType.STUDENT_WORKSHEET,
            "format": "a4_landscape",
        },
        {
            "id": "good_data_literacy",
            "name": "Data Literacy: Statistical Distributions",
            "input": "# Data Literacy: Understanding Statistical Distributions & Variance\nNormal distributions, standard deviation, and avoiding data misinterpretation.",
            "source": "data_literacy.md",
            "domain": KnowledgeDomain.MATHEMATICS,
            "audience": AudienceLevel.UNDERGRADUATE,
            "artifact": TargetArtifactType.TEACHING_PRESENTATION,
            "format": "presentation_16_9",
        },
    ]

    good_results = []
    print("\n[SECTION 1: EVALUATING GOOD PRODUCTION CASES]")
    for gc in good_cases_defs:
        res = await pipeline.produce_artifact(
            raw_input=gc["input"],
            source_hint=gc["source"],
            domain=gc["domain"],
            audience=gc["audience"],
            target_artifact=gc["artifact"],
            output_dir=out_base / "good",
            output_filename=gc["id"],
            target_format=gc["format"],
            director_enabled=True,
            evaluate_quality=True,
        )
        q_rep = res.quality_report
        good_results.append({
            "case_id": gc["id"],
            "name": gc["name"],
            "format": gc["format"],
            "score": q_rep.overall_score if q_rep else 0.0,
            "quality_level": q_rep.quality_level.value if q_rep else "unknown",
            "decision": res.quality_gate.decision.value if res.quality_gate else "unknown",
            "can_proceed": res.quality_gate.can_proceed if res.quality_gate else False,
            "findings_count": len(q_rep.findings) if q_rep else 0,
        })
        print(f"  [GOOD] {gc['name']}: Score = {q_rep.overall_score if q_rep else 0.0} ({q_rep.quality_level.value if q_rep else ''}) | Decision = {res.quality_gate.decision.value if res.quality_gate else ''}")

    # 2. ADVERSARIAL / DEFECTIVE CASES
    bad_results = []
    print("\n[SECTION 2: EVALUATING ADVERSARIAL / DEFECTIVE CASES]")

    # Bad Case 1: Empty Structure
    empty_comp = DocumentComposition(document_id="doc_bad_empty", title="Empty", mode=DocumentMode.A4_PORTRAIT, theme_reference="default", source_blueprint_id="bp", pages=[])
    r_empty = QualityEvaluationEngine.evaluate_artifact("bad_empty", composition=empty_comp, target_format="a4_portrait")
    bad_results.append({
        "case_id": "bad_empty_structure",
        "defect": "Empty page composition",
        "score": r_empty.overall_score,
        "quality_level": r_empty.quality_level.value,
        "decision": r_empty.gate_result.decision.value,
        "can_proceed": r_empty.gate_result.can_proceed,
        "critical_count": len(r_empty.gate_result.critical_findings),
    })
    print(f"  [BAD] Empty Structure: Score = {r_empty.overall_score} | Decision = {r_empty.gate_result.decision.value}")

    # Bad Case 2: Semantic Incompleteness
    bad_sem_content = ContentBlueprint(blueprint_id="bp_bad_sem", metadata=ContentMetadata(title="No Concepts"), objectives=[LearningObjective(id="o1", objective="No Concept Grounding", target_concept="Quantum")], concepts=[], facts=[])
    bad_sem_pedagogy = PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="Rat", sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")])
    bad_sem_prod = ProductionBlueprint(target_artifact=TargetArtifactType.TEACHING_PRESENTATION, requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")])
    bad_sem_bp = SemanticMaterialBlueprint(material_id="m_bad_sem", content=bad_sem_content, pedagogy=bad_sem_pedagogy, production=bad_sem_prod)
    r_sem = QualityEvaluationEngine.evaluate_artifact("bad_sem", material_bp=bad_sem_bp, target_format="a4_portrait")
    bad_results.append({
        "case_id": "bad_semantic_incompleteness",
        "defect": "Zero defined concepts with targeted objectives",
        "score": r_sem.overall_score,
        "quality_level": r_sem.quality_level.value,
        "decision": r_sem.gate_result.decision.value,
        "can_proceed": r_sem.gate_result.can_proceed,
        "critical_count": len(r_sem.gate_result.critical_findings),
    })
    print(f"  [BAD] Semantic Incompleteness: Score = {r_sem.overall_score} | Decision = {r_sem.gate_result.decision.value}")

    # Bad Case 3: Pedagogical Sequence Inversion
    bad_journey = LearningJourney(journey_id="j_bad", strategy=MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE, stages=[
        LearningStage(stage_type=LearningStageType.WORKED_EXAMPLE, title="Math problem", purpose="Problem"),
        LearningStage(stage_type=LearningStageType.CONCEPT_FORMALIZATION, title="Theory", purpose="Theory"),
    ])
    r_ped = QualityEvaluationEngine.evaluate_artifact("bad_ped", journey=bad_journey, target_format="a4_portrait")
    bad_results.append({
        "case_id": "bad_pedagogical_inversion",
        "defect": "Worked example placed before concept formalization",
        "score": r_ped.overall_score,
        "quality_level": r_ped.quality_level.value,
        "decision": r_ped.gate_result.decision.value,
        "can_proceed": r_ped.gate_result.can_proceed,
        "critical_count": len(r_ped.gate_result.critical_findings),
    })
    print(f"  [BAD] Pedagogical Inversion: Score = {r_ped.overall_score} | Decision = {r_ped.gate_result.decision.value}")

    # Bad Case 4: Extreme Density Overload
    dense_text = "Extreme wall of text without formatting or breathing room. " * 50  # ~2500 chars on 16:9
    dense_comp = DocumentComposition(
        document_id="doc_dense",
        title="Dense",
        mode=DocumentMode.PRESENTATION_16_9,
        theme_reference="default",
        source_blueprint_id="bp",
        pages=[PageComposition(page_number=1, page_type="content", composition_type="single_region", regions={RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content=dense_text)])})],
    )
    r_dens = QualityEvaluationEngine.evaluate_artifact("bad_dens", composition=dense_comp, target_format="presentation_16_9")
    bad_results.append({
        "case_id": "bad_density_overload",
        "defect": "2500 characters on single 16:9 presentation slide",
        "score": r_dens.overall_score,
        "quality_level": r_dens.quality_level.value,
        "decision": r_dens.gate_result.decision.value,
        "can_proceed": r_dens.gate_result.can_proceed,
        "critical_count": len(r_dens.gate_result.critical_findings),
    })
    print(f"  [BAD] Density Overload: Score = {r_dens.overall_score} | Decision = {r_dens.gate_result.decision.value}")

    # Bad Case 5: Quadruple Redundancy
    dup_span = "Identical substantial text span copied across four separate pages repeatedly without variation."
    dup_pages = [
        PageComposition(page_number=i, page_type="content", composition_type="single_region", regions={RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=[f"u{i}"], raw_content=dup_span)])})
        for i in range(1, 5)
    ]
    dup_comp = DocumentComposition(document_id="doc_dup", title="Dup", mode=DocumentMode.A4_PORTRAIT, theme_reference="default", source_blueprint_id="bp", pages=dup_pages)
    r_dup = QualityEvaluationEngine.evaluate_artifact("bad_dup", composition=dup_comp, target_format="a4_portrait")
    bad_results.append({
        "case_id": "bad_quad_redundancy",
        "defect": "Verbatim paragraph duplicate across 4 sequential pages",
        "score": r_dup.overall_score,
        "quality_level": r_dup.quality_level.value,
        "decision": r_dup.gate_result.decision.value,
        "can_proceed": r_dup.gate_result.can_proceed,
        "critical_count": len(r_dup.gate_result.critical_findings),
    })
    print(f"  [BAD] Quad Redundancy: Score = {r_dup.overall_score} | Decision = {r_dup.gate_result.decision.value}")

    # Bad Case 6: Format Geometry Corruption
    bad_fmt_pdf = out_base / "bad" / "corrupted_geometry.pdf"
    bad_fmt_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc_bad = pymupdf.open()
    doc_bad.new_page(width=960.0, height=540.0)  # Landscape slide created
    doc_bad.save(str(bad_fmt_pdf))
    doc_bad.close()
    r_fmt = QualityEvaluationEngine.evaluate_artifact("bad_fmt", pdf_path=bad_fmt_pdf, target_format="a4_portrait")
    bad_results.append({
        "case_id": "bad_format_corruption",
        "defect": "Physical PDF geometry (16:9) violates target format (A4 Portrait)",
        "score": r_fmt.overall_score,
        "quality_level": r_fmt.quality_level.value,
        "decision": r_fmt.gate_result.decision.value,
        "can_proceed": r_fmt.gate_result.can_proceed,
        "critical_count": len(r_fmt.gate_result.critical_findings),
    })
    print(f"  [BAD] Format Corruption: Score = {r_fmt.overall_score} | Decision = {r_fmt.gate_result.decision.value}")

    # 3. SCORE SEPARATION ANALYSIS
    good_scores = [g["score"] for g in good_results]
    bad_scores = [b["score"] for b in bad_results]
    mean_good = sum(good_scores) / len(good_scores)
    mean_bad = sum(bad_scores) / len(bad_scores)
    separation = mean_good - mean_bad

    gate_dist = {
        "good_can_proceed_rate": sum(1 for g in good_results if g["can_proceed"]) / len(good_results),
        "bad_rejection_rate": sum(1 for b in bad_results if not b["can_proceed"]) / len(bad_results),
    }

    report_payload = {
        "batch": "15.5",
        "title": "Adversarial Quality Validation & Discrimination Benchmark",
        "mean_good_score": round(mean_good, 3),
        "mean_bad_score": round(mean_bad, 3),
        "score_separation": round(separation, 3),
        "gate_distribution": gate_dist,
        "good_cases": good_results,
        "bad_cases": bad_results,
        "verdict": "VERDICT_A_ACCEPTANCE" if separation >= 0.25 and gate_dist["bad_rejection_rate"] >= 0.80 else "VERDICT_B_PARTIAL",
    }

    report_file = out_base / "benchmark_report.json"
    report_file.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")

    print("\n" + "=" * 80)
    print(f"ADVERSARIAL BENCHMARK COMPLETE!")
    print(f"Mean Good Score: {mean_good:.3f} | Mean Bad Score: {mean_bad:.3f} | Separation: +{separation:.3f}")
    print(f"Good Proceed Rate: {gate_dist['good_can_proceed_rate']*100:.1f}% | Bad Rejection Rate: {gate_dist['bad_rejection_rate']*100:.1f}%")
    print(f"Saved to: {report_file}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_adversarial_benchmark())
