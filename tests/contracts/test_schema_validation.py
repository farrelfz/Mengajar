"""Unit tests for Intelligence Domain Schemas."""

import pytest
from pydantic import ValidationError

from app.intelligence.schemas import (
    BlueprintCandidateType,
    BlueprintProposal,
    ContentDensity,
    ContentGroup,
    ContentType,
    ContentUnit,
    DocumentGenre,
    DocumentMode,
    ResearchTraceability,
    TraceabilityWarning,
    VisualIntent,
)


def test_content_unit_creation_and_word_count():
    """Verify ContentUnit validates non-empty text and calculates word count."""
    unit = ContentUnit(
        source_order=0,
        raw_text="Ini adalah contoh teks unit semantik.",
        normalized_text="Ini adalah contoh teks unit semantik.",
        content_type=ContentType.EXPLANATION,
    )
    assert unit.word_count == 6
    assert unit.unit_id is not None
    assert unit.content_type == ContentType.EXPLANATION


def test_content_unit_empty_text_raises():
    """Verify ContentUnit rejects empty or whitespace-only raw text."""
    with pytest.raises(ValidationError):
        ContentUnit(
            source_order=0,
            raw_text="   \n  ",
            normalized_text="",
        )


def test_research_traceability_bab_coverage_validator():
    """Verify ResearchTraceability flags MISSING_BAB_COVERAGE if results exist without conclusion."""
    traceability = ResearchTraceability(
        has_research_problem=True,
        has_results=True,
        has_conclusion=False,
    )
    assert TraceabilityWarning.MISSING_BAB_COVERAGE in traceability.traceability_warnings


def test_blueprint_proposal_schema_defaults():
    """Verify BlueprintProposal can be created with valid semantic groups."""
    group = ContentGroup(
        title="Pengantar",
        unit_ids=["u1", "u2"],
        blueprint_candidate=BlueprintCandidateType.SECTION_INTRODUCTION,
        primary_visual_intent=VisualIntent.TEXT_FOCUSED,
        density=ContentDensity.LOW,
    )
    proposal = BlueprintProposal(
        source_analysis_id="job-123",
        document_title="Laporan Penelitian",
        document_genre=DocumentGenre.RESEARCH_REPORT,
        recommended_mode=DocumentMode.A4_TUTORIAL,
        content_groups=[group],
    )
    assert proposal.document_title == "Laporan Penelitian"
    assert len(proposal.content_groups) == 1
    assert proposal.content_groups[0].blueprint_candidate == BlueprintCandidateType.SECTION_INTRODUCTION


def test_content_type_enum_membership():
    """Verify essential research roles exist in ContentType enum."""
    assert ContentType.RESEARCH_PROBLEM == "research_problem"
    assert ContentType.RESEARCH_FINDING == "research_finding"
    assert ContentType.RESEARCH_INTERPRETATION == "research_interpretation"
    assert ContentType.RESEARCH_CONCLUSION == "research_conclusion"
    assert ContentType.RESEARCH_RECOMMENDATION == "research_recommendation"
