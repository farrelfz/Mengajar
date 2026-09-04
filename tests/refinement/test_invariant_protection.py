"""
Unit tests for Invariant Protection rejecting accidental regressions.
"""

import copy
import pytest
from app.blueprints.content import (
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    LearningObjective,
)
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.blueprints.pedagogical import PedagogicalBlueprint, PedagogicalPattern
from app.blueprints.production import ProductionBlueprint, TargetArtifactType
from app.composition.schemas import DocumentComposition, PageComposition
from app.intelligence.schemas import DocumentMode
from app.refinement.contracts import InvariantCategory, RefinedArtifactBundle
from app.refinement.invariants import InvariantChecker


def test_invariant_checker_catches_deleted_learning_objectives():
    content_base = ContentBlueprint(
        blueprint_id="bp1",
        metadata=ContentMetadata(title="Mechanics"),
        objectives=[
            LearningObjective(id="o1", objective="Master Newton's Second Law"),
            LearningObjective(id="o2", objective="Calculate acceleration from net force"),
        ],
        concepts=[ConceptDefinition(id="c1", name="Force", formal_definition="Push or pull interaction.")],
    )
    pedagogy = PedagogicalBlueprint(primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT, narrative_rationale="Rationale")
    prod = ProductionBlueprint(target_artifact=TargetArtifactType.DETAILED_HANDOUT)
    bp_base = SemanticMaterialBlueprint(material_id="m_base", content=content_base, pedagogy=pedagogy, production=prod)
    comp_base = DocumentComposition(document_id="d_base", title="Mechanics", mode=DocumentMode.A4_PORTRAIT, theme_reference="default", source_blueprint_id="bp1", pages=[PageComposition(page_number=1, page_type="content", composition_type="single_region", regions={})])
    bundle_base = RefinedArtifactBundle(artifact_id="art_base", blueprint=bp_base, composition=comp_base)

    # Candidate accidentally removed objective o2
    content_cand = copy.deepcopy(content_base)
    content_cand.objectives = [content_cand.objectives[0]]  # o2 removed
    bp_cand = SemanticMaterialBlueprint(material_id="m_cand", content=content_cand, pedagogy=pedagogy, production=prod)
    bundle_cand = RefinedArtifactBundle(artifact_id="art_cand", blueprint=bp_cand, composition=comp_base)

    violations = InvariantChecker.check_invariants(bundle_base, bundle_cand)

    assert len(violations) >= 1
    assert violations[0].category == InvariantCategory.SEMANTIC_INVARIANT
    assert violations[0].invariant_name == "learning_objectives_preserved"
