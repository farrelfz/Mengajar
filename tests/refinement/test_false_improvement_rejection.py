"""
Unit tests for rejecting False Improvements where score improves but critical content was lost.
"""

import copy
import pytest
from app.blueprints.content import (
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    KnowledgeDomain,
    LearningObjective,
)
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.blueprints.pedagogical import PedagogicalBlueprint, PedagogicalPattern
from app.blueprints.production import ProductionBlueprint, TargetArtifactType
from app.composition.schemas import DocumentComposition, PageComposition
from app.critic.contracts import CritiqueReport
from app.intelligence.schemas import DocumentMode
from app.quality.contracts import (
    QualityGateDecision,
    QualityGateResult,
    QualityReport,
    QualityScore,
)
from app.refinement.contracts import (
    ImprovementDecision,
    RefinedArtifactBundle,
    RefinementCandidate,
)
from app.refinement.decision import ImprovementJudge
from app.refinement.evaluator import ImprovementComparator


def test_false_improvement_rejected_when_objective_lost_despite_score_increase():
    content_base = ContentBlueprint(
        blueprint_id="bp_base",
        metadata=ContentMetadata(title="Kinematics", domain=KnowledgeDomain.PHYSICS),
        objectives=[
            LearningObjective(id="o1", objective="Understand constant acceleration"),
            LearningObjective(id="o2", objective="Derive velocity-time equation"),
        ],
        concepts=[ConceptDefinition(id="c1", name="Acceleration", formal_definition="Rate of change of velocity.")],
    )
    bp_base = SemanticMaterialBlueprint(material_id="m_base", content=content_base, pedagogy=PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="R"), production=ProductionBlueprint(target_artifact=TargetArtifactType.DETAILED_HANDOUT))
    comp_base = DocumentComposition(document_id="d_base", title="Kinematics", mode=DocumentMode.A4_PORTRAIT, theme_reference="default", source_blueprint_id="bp_base", pages=[PageComposition(page_number=1, page_type="content", composition_type="single_region", regions={})])
    bundle_base = RefinedArtifactBundle(artifact_id="art_base", blueprint=bp_base, composition=comp_base)

    cand_base = RefinementCandidate(
        candidate_id="c_base",
        parent_artifact_id="root",
        iteration=0,
        patches=[],
        artifact_bundle=bundle_base,
        quality_report=QualityReport(job_id="j_base", overall_score=0.82, gate_result=QualityGateResult(decision=QualityGateDecision.PASS, score=QualityScore(overall_score=0.82), passed=True, gate_reasoning="Passed")),
        critique_report=CritiqueReport(artifact_id="art_base", overall_assessment="Needs derivation", findings=[]),
    )

    # Candidate has higher score (0.91) BUT stripped objective o2 to simplify
    content_cand = copy.deepcopy(content_base)
    content_cand.objectives = [content_cand.objectives[0]]
    bp_cand = SemanticMaterialBlueprint(material_id="m_cand", content=content_cand, pedagogy=PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="R"), production=ProductionBlueprint(target_artifact=TargetArtifactType.DETAILED_HANDOUT))
    bundle_cand = RefinedArtifactBundle(artifact_id="art_cand", blueprint=bp_cand, composition=comp_base)

    cand_new = RefinementCandidate(
        candidate_id="c_cand",
        parent_artifact_id="c_base",
        iteration=1,
        patches=[],
        artifact_bundle=bundle_cand,
        quality_report=QualityReport(job_id="j_cand", overall_score=0.91, gate_result=QualityGateResult(decision=QualityGateDecision.PASS, score=QualityScore(overall_score=0.91), passed=True, gate_reasoning="Passed")),  # Higher score
        critique_report=CritiqueReport(artifact_id="art_cand", overall_assessment="Clean", findings=[]),
    )

    comparison = ImprovementComparator.compare(
        baseline_bundle=bundle_base,
        baseline_candidate=cand_base,
        new_candidate=cand_new,
    )
    decision = ImprovementJudge.judge(comparison)

    assert len(comparison.invariant_violations) >= 1
    assert decision == ImprovementDecision.REJECT
