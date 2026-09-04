"""
Unit tests for Improvement Comparator calculating finding and score deltas.
"""

import pytest
from app.blueprints.content import ContentBlueprint, ContentMetadata
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.blueprints.pedagogical import PedagogicalBlueprint, PedagogicalPattern
from app.blueprints.production import ProductionBlueprint, TargetArtifactType
from app.composition.schemas import DocumentComposition, PageComposition
from app.critic.contracts import CritiqueConfidence, CritiqueFinding, CritiquePerspective, CritiqueReport, CritiqueSeverity
from app.intelligence.schemas import DocumentMode
from app.quality.contracts import QualityGateDecision, QualityGateResult, QualityReport, QualityScore
from app.refinement.contracts import RefinedArtifactBundle, RefinementCandidate
from app.refinement.evaluator import ImprovementComparator


def test_comparator_detects_resolved_findings_and_score_gain():
    bp = SemanticMaterialBlueprint(material_id="m1", content=ContentBlueprint(blueprint_id="b", metadata=ContentMetadata(title="T")), pedagogy=PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="R"), production=ProductionBlueprint(target_artifact=TargetArtifactType.DETAILED_HANDOUT))
    comp = DocumentComposition(document_id="d1", title="T", mode=DocumentMode.A4_PORTRAIT, theme_reference="default", source_blueprint_id="b", pages=[PageComposition(page_number=1, page_type="content", composition_type="single_region", regions={})])
    bundle = RefinedArtifactBundle(artifact_id="art1", blueprint=bp, composition=comp)

    # Base candidate: score 0.70 with finding f1
    cand_base = RefinementCandidate(
        candidate_id="cand_base",
        parent_artifact_id="root",
        iteration=0,
        patches=[],
        artifact_bundle=bundle,
        quality_report=QualityReport(job_id="j0", overall_score=0.70, gate_result=QualityGateResult(decision=QualityGateDecision.NEEDS_REFINEMENT, score=QualityScore(overall_score=0.70), passed=False, gate_reasoning="Needs work")),
        critique_report=CritiqueReport(artifact_id="art1", overall_assessment="Needs work", findings=[CritiqueFinding(id="f1", perspective=CritiquePerspective.PEDAGOGICAL, title="Order", observation="O", diagnosis="D", why_it_matters="W", severity=CritiqueSeverity.HIGH, confidence=CritiqueConfidence.HIGH, improvement_direction="Fix order")]),
    )

    # New candidate: score 0.85 with finding f1 resolved
    cand_new = RefinementCandidate(
        candidate_id="cand_iter1",
        parent_artifact_id="cand_base",
        iteration=1,
        patches=[],
        artifact_bundle=bundle,
        quality_report=QualityReport(job_id="j1", overall_score=0.85, gate_result=QualityGateResult(decision=QualityGateDecision.PASS, score=QualityScore(overall_score=0.85), passed=True, gate_reasoning="Passed")),
        critique_report=CritiqueReport(artifact_id="art1", overall_assessment="Clean", findings=[]),
    )

    comp_res = ImprovementComparator.compare(
        baseline_bundle=bundle,
        baseline_candidate=cand_base,
        new_candidate=cand_new,
    )

    assert comp_res.quality_delta == 0.15
    assert "f1" in comp_res.resolved_finding_ids
    assert len(comp_res.new_regressions) == 0
    assert comp_res.is_meaningful_improvement is True
