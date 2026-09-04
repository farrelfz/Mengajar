"""
Unit tests for Refinement History audit memory.
"""

import pytest
from app.blueprints.content import ContentBlueprint, ContentMetadata
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.blueprints.pedagogical import PedagogicalBlueprint, PedagogicalPattern
from app.blueprints.production import ProductionBlueprint, TargetArtifactType
from app.composition.schemas import DocumentComposition
from app.intelligence.schemas import DocumentMode
from app.refinement.contracts import (
    ImprovementComparison,
    ImprovementDecision,
    RefinedArtifactBundle,
    RefinementCandidate,
    RefinementPlan,
    RefinementTrace,
)
from app.refinement.history import RefinementHistory


def test_refinement_history_tracks_iterations_and_fingerprints():
    bp = SemanticMaterialBlueprint(material_id="m1", content=ContentBlueprint(blueprint_id="b", metadata=ContentMetadata(title="T")), pedagogy=PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="R"), production=ProductionBlueprint(target_artifact=TargetArtifactType.DETAILED_HANDOUT))
    comp = DocumentComposition(document_id="d1", title="T", mode=DocumentMode.A4_PORTRAIT, theme_reference="default", source_blueprint_id="b", pages=[])
    bundle = RefinedArtifactBundle(artifact_id="c1", blueprint=bp, composition=comp)

    history = RefinementHistory(artifact_id="art_hist_test")
    plan = RefinementPlan(plan_id="p1", source_artifact_id="art_hist_test", iteration=1)
    cand = RefinementCandidate(candidate_id="c1", parent_artifact_id="root", iteration=1, artifact_bundle=bundle)
    comp_res = ImprovementComparison(iteration=1, baseline_quality_score=0.70, candidate_quality_score=0.85, quality_delta=0.15, baseline_findings_count=1, candidate_findings_count=0)
    trace = RefinementTrace(iteration=1, candidate_score=0.85, quality_delta=0.15, decision=ImprovementDecision.ACCEPT)

    history.record_iteration(plan, cand, comp_res, "fp_test_1", trace)

    assert history.total_iterations == 1
    assert len(history.fingerprints) == 1
    assert history.fingerprints[0] == "fp_test_1"
    assert len(history.traces) == 1
