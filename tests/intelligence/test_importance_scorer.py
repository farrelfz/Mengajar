"""Unit tests for ImportanceScorer."""

from app.intelligence.importance_scorer import ImportanceScorer
from app.intelligence.schemas import (
    ConfidenceLevel,
    ContentRelationship,
    ContentType,
    ContentUnit,
    RelationshipType,
)


def test_importance_scorer_headings_receive_high_score():
    """Verify structural headings receive maximum structural weight."""
    scorer = ImportanceScorer()
    unit = ContentUnit(
        source_order=0,
        raw_text="BAB 1 PENDAHULUAN",
        normalized_text="BAB 1 PENDAHULUAN",
        content_type=ContentType.TITLE,
        depth=1,
    )
    score = scorer.score_unit(unit, [])
    assert score.structural_score == 1.0
    assert score.final_score >= 0.7
    assert len(score.reasons) > 0
    assert score.confidence == ConfidenceLevel.HIGH


def test_importance_scorer_centrality_increases_score():
    """Verify units with multiple incoming dependency edges receive higher relationship scores."""
    scorer = ImportanceScorer()
    central_unit = ContentUnit(
        unit_id="u_problem",
        source_order=1,
        raw_text="Rumusan masalah utama...",
        normalized_text="Rumusan masalah utama...",
        content_type=ContentType.RESEARCH_PROBLEM,
        research_role=ContentType.RESEARCH_PROBLEM,
        depth=0,
    )

    relationships = [
        ContentRelationship(source_unit_id="u_q1", target_unit_id="u_problem", relationship_type=RelationshipType.ADDRESSES),
        ContentRelationship(source_unit_id="u_q2", target_unit_id="u_problem", relationship_type=RelationshipType.ADDRESSES),
        ContentRelationship(source_unit_id="u_obj", target_unit_id="u_problem", relationship_type=RelationshipType.ADDRESSES),
    ]

    score_without_rel = scorer.score_unit(central_unit, [])
    score_with_rel = scorer.score_unit(central_unit, relationships)

    assert score_with_rel.relationship_score > score_without_rel.relationship_score
    assert score_with_rel.final_score >= score_without_rel.final_score


def test_importance_scorer_explainability():
    """Verify score contains detailed human-readable reasons, not just arbitrary numbers."""
    scorer = ImportanceScorer()
    unit = ContentUnit(
        source_order=2,
        raw_text="Hasil ini sangat penting dan signifikan.",
        normalized_text="Hasil ini sangat penting dan signifikan.",
        content_type=ContentType.RESEARCH_FINDING,
        research_role=ContentType.RESEARCH_FINDING,
    )
    score = scorer.score_unit(unit, [])
    reasons_str = " ".join(score.reasons)
    assert "Semantic type" in reasons_str
    assert "emphasis" in reasons_str or "Structural" in reasons_str
