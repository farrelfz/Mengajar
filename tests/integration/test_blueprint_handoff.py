"""Integration tests for BlueprintProposal readiness for Batch 3 (Design Layer handoff)."""

from app.intelligence.blueprint_proposer import BlueprintProposer
from app.intelligence.schemas import (
    AnalysisResult,
    BlueprintCandidateType,
    ContentType,
    ContentUnit,
    DocumentGenre,
    DocumentMode,
    VisualIntent,
    VisualIntentResult,
)


def test_blueprint_proposal_ready_for_batch3_handoff():
    """Verify that BlueprintProposal contains complete semantic structure ready for Batch 3."""
    proposer = BlueprintProposer()

    u_title = ContentUnit(source_order=0, raw_text="# Judul Riset", normalized_text="# Judul Riset", content_type=ContentType.TITLE, depth=1)
    u_data = ContentUnit(source_order=1, raw_text="Tabel data...", normalized_text="Tabel data...", content_type=ContentType.DATA, research_role=ContentType.DATA_POINT)
    u_conc = ContentUnit(source_order=2, raw_text="Kesimpulan...", normalized_text="Kesimpulan...", content_type=ContentType.CONCLUSION, research_role=ContentType.RESEARCH_CONCLUSION)

    intents = {
        u_data.unit_id: VisualIntentResult(unit_id=u_data.unit_id, primary_intent=VisualIntent.DATA_COMPARISON),
    }

    analysis = AnalysisResult(
        job_id="job-handoff-1",
        source_file="handoff.md",
        content_units=[u_title, u_data, u_conc],
        visual_intents=intents,
        document_genre=DocumentGenre.RESEARCH_REPORT,
        recommended_mode=DocumentMode.A4_TUTORIAL,
    )

    proposal = proposer.propose(analysis)

    # 1. Verify top-level metadata
    assert proposal.source_analysis_id == "job-handoff-1"
    assert proposal.document_title == "# Judul Riset"
    assert proposal.document_genre == DocumentGenre.RESEARCH_REPORT
    assert proposal.recommended_mode == DocumentMode.A4_TUTORIAL

    # 2. Verify candidate types and grouping
    assert len(proposal.content_groups) >= 2
    group_candidates = [g.blueprint_candidate for g in proposal.content_groups]
    assert BlueprintCandidateType.TITLE_BLOCK in group_candidates or BlueprintCandidateType.RESEARCH_RESULT_BLOCK in group_candidates

    # 3. Verify zero rendering pollution
    json_str = proposal.model_dump_json()
    for forbidden in ["<div", "<span", "style=", "font-size", "color:", "#ffffff", "px", "rem", "playwright"]:
        assert forbidden not in json_str.lower()
