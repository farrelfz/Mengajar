"""
Unit tests for Refinement Planner mapping findings to prioritized actions.
"""

import pytest
from app.blueprints.content import ContentBlueprint, ContentMetadata
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.blueprints.pedagogical import PedagogicalBlueprint, PedagogicalPattern
from app.blueprints.production import ProductionBlueprint, TargetArtifactType
from app.composition.schemas import DocumentComposition
from app.critic.contracts import CritiqueConfidence, CritiqueFinding, CritiquePerspective, CritiqueReport, CritiqueSeverity
from app.intelligence.schemas import DocumentMode
from app.quality.contracts import (
    QualityDimension,
    QualityFinding,
    QualityGateDecision,
    QualityGateResult,
    QualityReport,
    QualityScore,
    QualitySeverity,
)
from app.refinement.contracts import RefinedArtifactBundle, RefinementTargetLayer
from app.refinement.planner import RefinementPlanner


def test_planner_creates_ordered_plan_from_reports():
    content = ContentBlueprint(blueprint_id="bp", metadata=ContentMetadata(title="Test"))
    pedagogy = PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="Rationale")
    prod = ProductionBlueprint(target_artifact=TargetArtifactType.TEACHING_PRESENTATION)
    bp = SemanticMaterialBlueprint(material_id="m1", content=content, pedagogy=pedagogy, production=prod)
    comp = DocumentComposition(document_id="d1", title="Test", mode=DocumentMode.PRESENTATION_16_9, theme_reference="default", source_blueprint_id="bp", pages=[])
    bundle = RefinedArtifactBundle(artifact_id="art_1", blueprint=bp, composition=comp)

    q_score = QualityScore(overall_score=0.72)
    q_rep = QualityReport(
        job_id="job_1",
        overall_score=0.72,
        gate_result=QualityGateResult(decision=QualityGateDecision.NEEDS_REFINEMENT, score=q_score, passed=False, gate_reasoning="Needs density refinement"),
        findings=[
            QualityFinding(
                dimension=QualityDimension.INFORMATION_DENSITY,
                severity=QualitySeverity.WARNING,
                finding="Overcrowded slide",
                recommendation="Split block",
            )
        ],
    )
    c_rep = CritiqueReport(
        artifact_id="art_1",
        overall_assessment="Needs pedagogical reordering",
        findings=[
            CritiqueFinding(
                id="cf_ped",
                perspective=CritiquePerspective.PEDAGOGICAL,
                title="Worked Example Precedes Formalization",
                observation="Wrong order",
                diagnosis="Missing definition",
                why_it_matters="Pedagogical integrity",
                severity=CritiqueSeverity.HIGH,
                confidence=CritiqueConfidence.HIGH,
                improvement_direction="Reorder concept formalization before worked example.",
            )
        ],
    )

    plan = RefinementPlanner.create_plan(bundle, q_rep, c_rep, iteration=1)

    assert len(plan.actions) == 2
    assert plan.iteration == 1
    layers = {a.target_layer for a in plan.actions}
    assert RefinementTargetLayer.DIRECTOR in layers
    assert RefinementTargetLayer.DENSITY in layers
