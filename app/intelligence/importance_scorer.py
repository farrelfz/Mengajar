"""
KIR AI Document Intelligence — Importance Scorer.

Calculates the presentation importance of a ContentUnit based on
structural, semantic, and relationship weights.
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.intelligence.schemas import (
    ConfidenceLevel,
    ContentRelationship,
    ContentType,
    ContentUnit,
    ImportanceScore,
)

log = get_logger(__name__)

# Base semantic weights
_SEMANTIC_WEIGHTS: dict[ContentType, float] = {
    # High importance KTI roles
    ContentType.RESEARCH_PROBLEM: 1.0,
    ContentType.RESEARCH_QUESTION: 1.0,
    ContentType.RESEARCH_OBJECTIVE: 1.0,
    ContentType.HYPOTHESIS: 0.9,
    ContentType.RESEARCH_METHOD: 0.9,
    ContentType.RESEARCH_FINDING: 1.0,
    ContentType.RESEARCH_CONCLUSION: 1.0,
    ContentType.RESEARCH_RECOMMENDATION: 0.9,
    
    # General high importance
    ContentType.TITLE: 1.0,
    ContentType.SUMMARY: 0.9,
    ContentType.CONCLUSION: 1.0,
    ContentType.FINDING: 1.0,
    
    # Medium
    ContentType.DATA: 0.7,
    ContentType.RESULT: 0.8,
    ContentType.EXPLANATION: 0.6,
    ContentType.THEORY: 0.7,
    
    # Default
    ContentType.OTHER: 0.3,
}

class ImportanceScorer:
    """Calculates the importance score for ContentUnits."""

    def score_unit(
        self,
        unit: ContentUnit,
        all_relationships: list[ContentRelationship],
    ) -> ImportanceScore:
        """Calculate importance score deterministically.
        
        This relies on heuristics rather than the LLM to save tokens and time,
        as importance is a derived metric of structure and semantics.
        """
        reasons = []
        
        # 1. Structural score (headings are important, deep nesting less so)
        if unit.content_type == ContentType.TITLE:
            structural_score = 1.0
            reasons.append("Unit is a structural heading")
        else:
            # depth 0 = 0.8, depth 1 = 0.7, depth 2 = 0.6...
            structural_score = max(0.2, 0.8 - (unit.depth * 0.1))
            reasons.append(f"Structural depth {unit.depth}")

        # 2. Semantic score
        semantic_type = unit.research_role or unit.content_type
        semantic_score = _SEMANTIC_WEIGHTS.get(semantic_type, 0.5)
        reasons.append(f"Semantic type is {semantic_type.value}")

        # 3. Relationship score (centrality)
        # How many other units point to this one?
        incoming = sum(1 for r in all_relationships if r.target_unit_id == unit.unit_id)
        outgoing = sum(1 for r in all_relationships if r.source_unit_id == unit.unit_id)
        
        relationship_score = min(1.0, (incoming * 0.2) + (outgoing * 0.1))
        if relationship_score > 0:
            reasons.append(f"Centrality: {incoming} incoming, {outgoing} outgoing edges")

        # 4. Evidence/Emphasis (heuristic based on text)
        evidence_score = 0.0
        emphasis_score = 0.0
        
        text = unit.normalized_text.lower()
        if any(w in text for w in ["penting", "utama", "kritis", "signifikan"]):
            emphasis_score = 0.5
            reasons.append("Contains emphasis keywords")
            
        if any(c.isdigit() for c in text):
            evidence_score = 0.3
            
        # Calculate final weighted average
        # Semantic carries the most weight, then structural
        final = (
            (structural_score * 0.3) +
            (semantic_score * 0.5) +
            (relationship_score * 0.1) +
            (max(evidence_score, emphasis_score) * 0.1)
        )
        
        final_score = min(1.0, max(0.0, final))

        return ImportanceScore(
            structural_score=structural_score,
            semantic_score=semantic_score,
            relationship_score=relationship_score,
            evidence_score=evidence_score,
            emphasis_score=emphasis_score,
            final_score=final_score,
            confidence=ConfidenceLevel.HIGH,
            reasons=reasons,
        )
