"""Unit tests for BlueprintProposer algorithm."""

from app.intelligence.blueprint_proposer import BlueprintProposer
from app.intelligence.schemas import (
    AnalysisResult,
    ContentType,
    ContentUnit,
    DocumentGenre,
    DocumentMode,
    VisualIntent,
    VisualIntentResult,
)


def test_blueprint_proposer_groups_by_headings_and_semantics():
    """Verify units under separate headings form distinct content groups with dependencies."""
    proposer = BlueprintProposer()

    u1 = ContentUnit(source_order=0, raw_text="# Bab 1", normalized_text="# Bab 1", content_type=ContentType.TITLE, depth=1)
    u2 = ContentUnit(source_order=1, raw_text="Latar belakang.", normalized_text="Latar belakang.", content_type=ContentType.BACKGROUND)
    u3 = ContentUnit(source_order=2, raw_text="# Bab 2", normalized_text="# Bab 2", content_type=ContentType.TITLE, depth=1)
    u4 = ContentUnit(source_order=3, raw_text="Tinjauan teori.", normalized_text="Tinjauan teori.", content_type=ContentType.THEORY)

    analysis = AnalysisResult(
        job_id="test-job-1",
        source_file="test.md",
        content_units=[u1, u2, u3, u4],
        document_genre=DocumentGenre.GENERAL,
        recommended_mode=DocumentMode.A4_TUTORIAL,
    )

    proposal = proposer.propose(analysis)

    assert len(proposal.content_groups) == 2
    assert proposal.content_groups[0].title == "# Bab 1"
    assert proposal.content_groups[1].title == "# Bab 2"
    assert proposal.content_groups[1].previous_group_dependency == proposal.content_groups[0].group_id


def test_blueprint_proposer_promotes_visual_intent():
    """Verify group adopts non-default visual intent if present in its child units."""
    proposer = BlueprintProposer()

    u1 = ContentUnit(source_order=0, raw_text="Langkah 1", normalized_text="Langkah 1", content_type=ContentType.PROCEDURE)
    u2 = ContentUnit(source_order=1, raw_text="Langkah 2", normalized_text="Langkah 2", content_type=ContentType.PROCEDURE)

    intents = {
        u1.unit_id: VisualIntentResult(unit_id=u1.unit_id, primary_intent=VisualIntent.STEP_BY_STEP),
        u2.unit_id: VisualIntentResult(unit_id=u2.unit_id, primary_intent=VisualIntent.STEP_BY_STEP),
    }

    analysis = AnalysisResult(
        job_id="test-job-2",
        source_file="test_proc.md",
        content_units=[u1, u2],
        visual_intents=intents,
        document_genre=DocumentGenre.TUTORIAL,
    )

    proposal = proposer.propose(analysis)
    assert len(proposal.content_groups) == 1
    assert proposal.content_groups[0].primary_visual_intent == VisualIntent.STEP_BY_STEP


def test_blueprint_proposal_design_independence():
    """Verify proposal contains NO HTML tags, CSS styles, colors, or page coordinates."""
    proposer = BlueprintProposer()
    u1 = ContentUnit(source_order=0, raw_text="Judul", normalized_text="Judul", content_type=ContentType.TITLE, depth=1)
    analysis = AnalysisResult(
        job_id="test-job-3",
        source_file="test.md",
        content_units=[u1],
        document_genre=DocumentGenre.GENERAL,
    )
    proposal = proposer.propose(analysis)

    proposal_json = proposal.model_dump_json()

    # Forbidden rendering tokens
    forbidden_tokens = ["<div", "style=", "font-size", "color:", "#ffffff", "px", "rem", "playwright"]
    for token in forbidden_tokens:
        assert token not in proposal_json.lower()
