"""
Unit tests for Capability Grammar & Taxonomy Schema.
"""

from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)
from app.capabilities.registry import CapabilityRegistry
from app.libraries import register_all_default_capabilities


def test_taxonomy_enums_integrity():
    """Verify that all taxonomy enums have distinct, non-empty members."""
    for enum_cls in (SemanticIntent, InformationStructure, PedagogicalRole, VisualGrammar, DensityProfile, CapabilityFamily):
        members = list(enum_cls)
        assert len(members) >= 4
        values = [m.value for m in members]
        assert len(values) == len(set(values)), f"Duplicate enum value in {enum_cls.__name__}"


def test_taxonomy_signature_matching():
    """Verify multi-axis intersection matching logic."""
    sig = TaxonomySignature(
        family=CapabilityFamily.PROCESS_VISUALIZATION,
        primary_intent=SemanticIntent.SEQUENCE,
        supported_intents=[SemanticIntent.EXPLAIN],
        structure=InformationStructure.LINEAR_SEQUENCE,
        pedagogical_role=PedagogicalRole.SCAFFOLD,
        visual_grammar=VisualGrammar.PROCESS_FLOW,
        density=DensityProfile.FOCUSED,
        preferred_formats=["presentation_16_9", "a4_landscape"],
    )

    # Exact intent
    assert sig.matches_query(intent="sequence") is True
    # Supported intent
    assert sig.matches_query(intent="explain") is True
    # Non-supported intent
    assert sig.matches_query(intent="compare") is False

    # Multi-axis intersection
    assert sig.matches_query(intent="sequence", family="process_visualization", structure="linear_sequence") is True
    assert sig.matches_query(intent="sequence", family="spatial_systems") is False


def test_all_default_capabilities_have_taxonomy_signatures():
    """Verify that every built-in capability is properly classified under the taxonomy."""
    reg = CapabilityRegistry()
    register_all_default_capabilities(reg)

    caps = reg.list_all()
    assert len(caps) >= 19, f"Expected at least 19 registered capabilities, got {len(caps)}"

    for cap in caps:
        meta = cap.metadata
        assert meta.taxonomy is not None, f"Capability '{meta.capability_id}' lacks TaxonomySignature"
        assert meta.family is not None
        assert meta.primary_intent is not None
        assert meta.structure is not None
        assert meta.pedagogical_role is not None
        assert meta.visual_grammar is not None
        assert meta.density is not None
        assert len(meta.taxonomy.preferred_formats) > 0
