"""
Claim-Evidence Linker: Links extracted claims to best retrieved evidence candidates and assigns logical relations.
"""

from __future__ import annotations

from app.grounding.consistency import ContradictionDetector
from app.grounding.contracts import (
    Claim,
    ClaimEvidenceLink,
    Evidence,
    GroundingStatus,
    SupportRelation,
)
from app.grounding.evidence_ranker import EvidenceRanker


class ClaimEvidenceLinker:
    """Links claims to ranked evidence and updates grounding statuses."""

    @classmethod
    def link_claim(cls, claim: Claim, candidate_evidences: list[Evidence]) -> tuple[list[ClaimEvidenceLink], GroundingStatus]:
        if not claim.requires_grounding:
            return ([], GroundingStatus.NOT_REQUIRED)

        if not candidate_evidences:
            return ([], GroundingStatus.UNGROUNDED)

        ranked = EvidenceRanker.rank_evidence(claim, candidate_evidences)
        links: list[ClaimEvidenceLink] = []
        best_status = GroundingStatus.UNGROUNDED

        for score, ev in ranked[:3]:
            relation, explanation = ContradictionDetector.check_relation(claim, ev)

            link = ClaimEvidenceLink(
                claim_id=claim.claim_id,
                evidence_id=ev.evidence_id,
                relation=relation,
                support_score=score,
                semantic_similarity=score,
                explanation=explanation,
            )
            links.append(link)

            if relation == SupportRelation.CONTRADICTS:
                best_status = GroundingStatus.CONTRADICTED
                break
            elif relation == SupportRelation.SUPPORTS:
                best_status = GroundingStatus.GROUNDED
            elif relation == SupportRelation.PARTIALLY_SUPPORTS and best_status != GroundingStatus.GROUNDED:
                best_status = GroundingStatus.PARTIALLY_GROUNDED

        return (links, best_status)
