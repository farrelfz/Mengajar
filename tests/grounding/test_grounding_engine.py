"""
Unit tests for Knowledge Grounding Engine master pipeline.
"""

from pathlib import Path
import pytest
from app.blueprints.content import (
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    KnowledgeDomain,
)
from app.grounding.engine import KnowledgeGroundingEngine
from app.grounding.providers.local_doc import LocalDocumentKnowledgeProvider


def test_grounding_engine_grounds_physics_blueprint():
    provider = LocalDocumentKnowledgeProvider("local_phys")
    provider.load_markdown_file(Path("tests/fixtures/grounding/physics_sources.md"), domain="physics")

    engine = KnowledgeGroundingEngine(providers=[provider])

    content = ContentBlueprint(
        blueprint_id="bp_phys",
        metadata=ContentMetadata(title="Torque Mechanics", domain=KnowledgeDomain.PHYSICS),
        concepts=[
            ConceptDefinition(id="c1", name="Torque", formal_definition="Rotational force analog tau = r * F sin(theta).", formula="tau = r * F sin(theta)"),
        ],
    )

    grounded_context = engine.ground_material(content, domain="physics")
    rep = grounded_context.report

    assert rep.claims_total >= 1
    assert rep.claims_grounded >= 1
    assert rep.score.overall_score >= 0.70
    assert len(grounded_context.citations) >= 1
