"""
Stage 7 — RelationshipInferencer.

Generates cross-unit typed KnowledgeRelationship edges (PREREQUISITE_OF, SUPPORTED_BY,
MEASURED_BY, DEMONSTRATED_BY, CONTRASTED_WITH) attached with RelationshipEvidence.
DO NOT mutate KnowledgeUnits.
"""

from __future__ import annotations

from typing import List
from app.intelligence.pipeline.claim_evidence_extractor import ClaimEvidenceAssociations
from app.intelligence.schemas import (
    ContentType,
    KnowledgeRelationship,
    KnowledgeUnit,
    RelationshipEvidence,
    RelationshipOrigin,
    RelationshipType,
)


class RelationshipInferencer:
    """Stage 7: Generates graph edges with explicit provenance and confidence."""

    def infer(
        self,
        units: List[KnowledgeUnit],
        claim_evidence: ClaimEvidenceAssociations,
    ) -> List[KnowledgeRelationship]:
        edges: List[KnowledgeRelationship] = []
        edge_set: set[str] = set()

        def _add_edge(src: str, tgt: str, rel: RelationshipType, origin: RelationshipOrigin, conf: float, rule: str):
            key = f"{src}->{tgt}:{rel.value}"
            if key not in edge_set and src != tgt:
                edge_set.add(key)
                edges.append(
                    KnowledgeRelationship(
                        source_unit_id=src,
                        target_unit_id=tgt,
                        relationship=rel,
                        evidence=RelationshipEvidence(
                            origin=origin,
                            confidence=conf,
                            rule_name=rule,
                        ),
                    )
                )

        unit_map = {u.id: u for u in units}

        # 1. Claim <-> Evidence Edges from Stage 6
        for claim_id, ev_id, conf in claim_evidence.associations:
            _add_edge(
                src=claim_id,
                tgt=ev_id,
                rel=RelationshipType.SUPPORTED_BY,
                origin=RelationshipOrigin.DETERMINISTIC_RULE,
                conf=conf,
                rule="claim_evidence_locality_rule",
            )

        # 2. Structural & Prerequisite Edges (Section & Heading Order)
        for i in range(len(units) - 1):
            u_curr = units[i]
            u_next = units[i + 1]

            # Prerequisite of sequential concepts in same section
            if u_curr.provenance.source_section_id == u_next.provenance.source_section_id:
                if u_curr.content_type in (ContentType.DEFINITION, ContentType.CONCEPT, ContentType.THEORY):
                    if u_next.content_type in (ContentType.FORMULA, ContentType.PROCEDURE, ContentType.EXAMPLE, ContentType.QUESTION):
                        _add_edge(
                            src=u_curr.id,
                            tgt=u_next.id,
                            rel=RelationshipType.PREREQUISITE_OF,
                            origin=RelationshipOrigin.DETERMINISTIC_RULE,
                            conf=0.90,
                            rule="sequential_prerequisite_rule",
                        )

            # Formula <-> Concept / Measurement Edges
            if u_curr.content_type == ContentType.CONCEPT and u_next.content_type == ContentType.FORMULA:
                _add_edge(
                    src=u_curr.id,
                    tgt=u_next.id,
                    rel=RelationshipType.MEASURED_BY,
                    origin=RelationshipOrigin.DETERMINISTIC_RULE,
                    conf=0.95,
                    rule="concept_formula_measurement_rule",
                )

            # Concept <-> Procedure / Experiment Demonstration Edges
            if u_curr.content_type in (ContentType.CONCEPT, ContentType.THEORY) and u_next.content_type == ContentType.PROCEDURE:
                _add_edge(
                    src=u_curr.id,
                    tgt=u_next.id,
                    rel=RelationshipType.DEMONSTRATED_BY,
                    origin=RelationshipOrigin.DETERMINISTIC_RULE,
                    conf=0.90,
                    rule="concept_procedure_demonstration_rule",
                )

        return edges
