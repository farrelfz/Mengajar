"""
Citation Provenance: Machine-readable traceability chain linking Claim -> Evidence -> Document -> Source.
"""

from __future__ import annotations

from app.grounding.contracts import CitationProvenance, Claim, ClaimEvidenceLink, Evidence


class ProvenanceTracer:
    """Constructs machine-readable citation provenance chains."""

    @classmethod
    def trace_provenance(
        cls,
        claims: list[Claim],
        links: list[ClaimEvidenceLink],
        evidence_dict: dict[str, Evidence],
    ) -> list[CitationProvenance]:
        provenances: list[CitationProvenance] = []

        for c in claims:
            c_links = [l for l in links if l.claim_id == c.claim_id]
            if not c_links:
                continue

            ev_ids = [l.evidence_id for l in c_links]
            src_ids = list({evidence_dict[eid].source_id for eid in ev_ids if eid in evidence_dict})

            trace_str = " -> ".join([c.claim_id] + ev_ids + src_ids)

            provenances.append(
                CitationProvenance(
                    citation_id=f"cit_{c.claim_id}",
                    claim_id=c.claim_id,
                    evidence_ids=ev_ids,
                    source_ids=src_ids,
                    trace_path=trace_str,
                )
            )

        return provenances
