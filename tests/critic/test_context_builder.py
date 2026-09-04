"""
Unit tests for CritiqueContextBuilder and partial context graceful degradation.
"""

import pytest

from app.blueprints.content import ContentBlueprint, ContentMetadata, KnowledgeDomain
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.blueprints.pedagogical import PedagogicalBlueprint, PedagogicalPattern, PedagogicalStep, SemanticStepType
from app.blueprints.production import ProductionBlueprint, ProductionRequirement, TargetArtifactType
from app.critic.context import CritiqueContextBuilder


def test_partial_context_assembly_and_evidence_reporting():
    # 1. Blueprint only context
    content = ContentBlueprint(
        blueprint_id="bp_test",
        metadata=ContentMetadata(title="Test", domain=KnowledgeDomain.PHYSICS),
        objectives=[],
        concepts=[],
        facts=[],
    )
    pedagogy = PedagogicalBlueprint(
        primary_pattern=PedagogicalPattern.CONCRETE_TO_ABSTRACT,
        narrative_rationale="Rationale",
        sequence=[PedagogicalStep(id="s1", semantic_type=SemanticStepType.HOOK, purpose="Hook")],
    )
    prod = ProductionBlueprint(
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        requirements=[ProductionRequirement(step_id="s1", semantic_type="hook")],
    )
    bp = SemanticMaterialBlueprint(material_id="m_test", content=content, pedagogy=pedagogy, production=prod)

    ctx_bp = CritiqueContextBuilder("job_1").with_blueprint(bp).build()
    sources = ctx_bp.available_evidence_sources()

    assert "blueprint" in sources
    assert "composition" not in sources
    assert "quality_report" not in sources
    assert ctx_bp.target_format == "a4_portrait"
