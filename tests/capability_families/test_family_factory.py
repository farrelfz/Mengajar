"""
Tests for FamilyTemplateRegistry and Capability Family Factory.
"""

import pytest

from app.capabilities.contracts import CapabilityMetadata, RenderTarget
from app.capabilities.families.contracts import ProcessSpec, ProcessStage
from app.capabilities.families.factory import (
    create_family_capability,
    register_family_capability,
)
from app.capabilities.families.registry import (
    FamilyTemplateRegistry,
    get_default_family_registry,
)
from app.capabilities.families.templates import LinearProcessTemplate
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)


def test_family_template_registry():
    reg = FamilyTemplateRegistry()
    template = LinearProcessTemplate()
    reg.register(template)

    # Retrieval
    retrieved = reg.get("process.linear")
    assert retrieved is not None
    assert retrieved.family == CapabilityFamily.PROCESS_VISUALIZATION

    # Duplicate prevention
    with pytest.raises(ValueError, match="already registered"):
        reg.register(template, overwrite=False)

    # List by family
    process_templates = reg.list_by_family(CapabilityFamily.PROCESS_VISUALIZATION)
    assert len(process_templates) == 1


def test_default_family_registry_contains_canonical_templates():
    reg = get_default_family_registry()
    templates = reg.list_all()
    assert len(templates) >= 7

    assert reg.get("process.linear") is not None
    assert reg.get("comparison.matrix") is not None
    assert reg.get("hierarchy.tree") is not None
    assert reg.get("reasoning.evidence_chain") is not None
    assert reg.get("progression.ladder") is not None
    assert reg.get("quantitative.derivation") is not None
    assert reg.get("relationship.network") is not None


def test_family_factory_creates_renderable_capability():
    cap_meta = CapabilityMetadata(
        capability_id="test.pedagogy.learning_pipeline",
        category="pedagogy",
        display_name="Learning Pipeline",
        description="Structured 3-step learning progression",
        semantic_tags=["learning", "pipeline", "pedagogy"],
        supported_artifacts=["presentation", "document"],
        domain="general",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.PROCESS_VISUALIZATION,
            primary_intent=SemanticIntent.SEQUENCE,
            structure=InformationStructure.LINEAR_SEQUENCE,
            pedagogical_role=PedagogicalRole.SCAFFOLD,
            visual_grammar=VisualGrammar.PROCESS_FLOW,
            density=DensityProfile.FOCUSED,
        ),
    )

    cap = create_family_capability(
        capability_id="test.pedagogy.learning_pipeline",
        template_id="process.linear",
        metadata=cap_meta,
    )

    assert cap.metadata.capability_id == "test.pedagogy.learning_pipeline"
    assert cap.renderer is not None

    # Test rendering through adapter
    spec = ProcessSpec(
        title="Learning Steps",
        stages=[
            ProcessStage(id="1", label="Understand Core Principles"),
            ProcessStage(id="2", label="Apply to Worked Examples"),
            ProcessStage(id="3", label="Synthesize Knowledge"),
        ],
    )
    output = cap.renderer.render(spec)
    assert output.output_format == "html"
    assert "Understand Core Principles" in output.rendered_content
    assert "family-process" in output.rendered_content


def test_family_factory_incompatible_family_rejection():
    # Attempt to pair COMPARATIVE_REASONING metadata with process.linear template
    bad_meta = CapabilityMetadata(
        capability_id="bad.cap",
        category="test",
        display_name="Bad Capability",
        description="Incompatible",
        semantic_tags=["bad"],
        supported_artifacts=["presentation"],
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.COMPARATIVE_REASONING,
            primary_intent=SemanticIntent.COMPARE,
            structure=InformationStructure.MATRIX,
            pedagogical_role=PedagogicalRole.ANALYSIS,
            visual_grammar=VisualGrammar.COMPARISON,
            density=DensityProfile.FOCUSED,
        ),
    )

    with pytest.raises(ValueError, match="incompatible with template"):
        create_family_capability(
            capability_id="bad.cap",
            template_id="process.linear",
            metadata=bad_meta,
        )
