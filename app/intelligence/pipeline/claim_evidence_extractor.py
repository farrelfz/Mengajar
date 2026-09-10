"""
Stage 6 — ClaimEvidenceExtractor.

Identifies claim units and evidence units across atomic KnowledgeUnits and derives candidate
associations. DO NOT modify payloads. DO NOT create graph edges.
"""

from __future__ import annotations

from typing import List, Tuple
from pydantic import BaseModel, Field

from app.intelligence.schemas import ContentType, KnowledgeUnit


class ClaimEvidenceAssociations(BaseModel):
    """Candidate associations between claim units and evidence units."""
    claim_unit_ids: List[str] = Field(default_factory=list)
    evidence_unit_ids: List[str] = Field(default_factory=list)
    # List of (claim_unit_id, evidence_unit_id, confidence) tuples
    associations: List[Tuple[str, str, float]] = Field(default_factory=list)


class ClaimEvidenceExtractor:
    """Stage 6: Identifies claim and evidence associations without modifying units or edges."""

    def extract(self, units: List[KnowledgeUnit]) -> ClaimEvidenceAssociations:
        claim_units: List[KnowledgeUnit] = []
        evidence_units: List[KnowledgeUnit] = []

        for u in units:
            if u.content_type in (ContentType.ARGUMENT, ContentType.HYPOTHESIS, ContentType.CONCLUSION, ContentType.THEORY, ContentType.ANALYSIS):
                claim_units.append(u)
            elif u.content_type in (ContentType.EVIDENCE, ContentType.DATA, ContentType.RESULT, ContentType.FINDING):
                evidence_units.append(u)

        associations: List[Tuple[str, str, float]] = []

        # Locality / Section-based association heuristics
        for claim in claim_units:
            for ev in evidence_units:
                # Same section / heading tag check
                common_tags = set(claim.tags) & set(ev.tags)
                same_section = claim.provenance.source_section_id == ev.provenance.source_section_id

                if same_section or common_tags:
                    confidence = 0.90 if same_section else 0.75
                    associations.append((claim.id, ev.id, confidence))
                elif abs(int(claim.provenance.source_start_line or 0) - int(ev.provenance.source_start_line or 0)) < 30:
                    associations.append((claim.id, ev.id, 0.65))

        return ClaimEvidenceAssociations(
            claim_unit_ids=[c.id for c in claim_units],
            evidence_unit_ids=[e.id for e in evidence_units],
            associations=associations,
        )
