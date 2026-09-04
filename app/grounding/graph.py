"""
In-Memory Typed Evidence Graph representation for relational traversal and contradiction analysis.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from app.grounding.contracts import (
    Claim,
    ClaimEvidenceLink,
    Evidence,
    GroundingStatus,
    SupportRelation,
)


class EvidenceGraph(BaseModel):
    """In-memory typed graph of Claims, Evidences, and Logical Links."""
    claims: dict[str, Claim] = Field(default_factory=dict)
    evidences: dict[str, Evidence] = Field(default_factory=dict)
    links: list[ClaimEvidenceLink] = Field(default_factory=list)

    def add_claim(self, claim: Claim) -> None:
        self.claims[claim.claim_id] = claim

    def add_evidence(self, evidence: Evidence) -> None:
        self.evidences[evidence.evidence_id] = evidence

    def add_link(self, link: ClaimEvidenceLink) -> None:
        self.links.append(link)

    def get_claim_evidence(self, claim_id: str) -> list[Evidence]:
        ev_ids = [l.evidence_id for l in self.links if l.claim_id == claim_id and l.relation in [SupportRelation.SUPPORTS, SupportRelation.PARTIALLY_SUPPORTS]]
        return [self.evidences[eid] for eid in ev_ids if eid in self.evidences]

    def find_unsupported_claims(self) -> list[Claim]:
        return [c for c in self.claims.values() if c.requires_grounding and c.grounding_status == GroundingStatus.UNGROUNDED]

    def find_contradictions(self) -> list[tuple[Claim, Evidence, str]]:
        contradictions: list[tuple[Claim, Evidence, str]] = []
        for l in self.links:
            if l.relation == SupportRelation.CONTRADICTS:
                c = self.claims.get(l.claim_id)
                e = self.evidences.get(l.evidence_id)
                if c and e:
                    contradictions.append((c, e, l.explanation))
        return contradictions
