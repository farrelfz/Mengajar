"""
Master Knowledge Grounding Engine: Coordinates the entire claim extraction, retrieval, evidence ranking, linking, scoring, and report generation loop.
"""

from __future__ import annotations

import uuid
from typing import Any
from app.blueprints.content import ContentBlueprint
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.grounding.claims import HeuristicClaimExtractor
from app.grounding.contracts import (
    Claim,
    ClaimEvidenceLink,
    Evidence,
    GroundedMaterialContext,
    GroundingFinding,
    GroundingReport,
    GroundingScore,
    GroundingStatus,
    GroundingTrace,
)
from app.grounding.graph import EvidenceGraph
from app.grounding.linker import ClaimEvidenceLinker
from app.grounding.policies import DomainGroundingPolicyRegistry
from app.grounding.provenance import ProvenanceTracer
from app.grounding.providers.base import KnowledgeProvider
from app.grounding.providers.contracts import KnowledgeQuery
from app.grounding.retrieval import RetrievalEngine
from app.grounding.scoring import GroundingScoreCalculator
from app.grounding.unsupported import UnsupportedClaimDetector


class KnowledgeGroundingEngine:
    """Master engine performing deterministic, explainable knowledge grounding."""

    def __init__(self, providers: list[KnowledgeProvider] | None = None) -> None:
        self.extractor = HeuristicClaimExtractor()
        self.retrieval_engine = RetrievalEngine(providers=providers)

    def ground_material(
        self,
        material: SemanticMaterialBlueprint | ContentBlueprint | str,
        domain: str = "general",
        sources: list[Any] | None = None,
    ) -> GroundedMaterialContext:
        trace_id = f"trc_grd_{uuid.uuid4().hex[:8]}"
        trace_decisions: list[str] = []

        # 1. Extract Claims
        claims = self.extractor.extract_claims(material, domain=domain)
        trace_decisions.append(f"Extracted {len(claims)} atomic claims.")

        policy = DomainGroundingPolicyRegistry.get_policy(domain)
        trace_decisions.append(f"Applied DomainGroundingPolicy for '{domain}'.")

        # 2. Retrieve Candidate Evidences & Link
        all_evidences_dict: dict[str, Evidence] = {}
        all_links: list[ClaimEvidenceLink] = []

        for c in claims:
            if not c.requires_grounding:
                continue

            query = KnowledgeQuery(query=c.content, domain=domain, top_k=3)
            retrieved = self.retrieval_engine.retrieve(query)
            ev_list = [r.evidence for r in retrieved]
            for ev in ev_list:
                all_evidences_dict[ev.evidence_id] = ev

            links, status = ClaimEvidenceLinker.link_claim(c, ev_list)
            c.grounding_status = status
            all_links.extend(links)

        # 3. Detect Unsupported Claims & Contradictions
        findings = UnsupportedClaimDetector.detect_findings(claims)
        trace_decisions.append(f"Generated {len(findings)} diagnostic findings.")

        # 4. Compute Grounding Score
        score = GroundingScoreCalculator.calculate_score(
            claims=claims,
            evidence=list(all_evidences_dict.values()),
            links=all_links,
        )

        # 5. Build Evidence Graph & Provenance
        graph = EvidenceGraph()
        for c in claims:
            graph.add_claim(c)
        for ev in all_evidences_dict.values():
            graph.add_evidence(ev)
        for l in all_links:
            graph.add_link(l)

        provenances = ProvenanceTracer.trace_provenance(
            claims=claims,
            links=all_links,
            evidence_dict=all_evidences_dict,
        )

        trace = GroundingTrace(
            trace_id=trace_id,
            query="batch_grounding",
            evidence_candidates_count=len(all_evidences_dict),
            evidence_selected_count=len(all_evidences_dict),
            claims_analyzed=len(claims),
            links_created=len(all_links),
            decisions=trace_decisions,
        )

        report = GroundingReport(
            claims_total=len(claims),
            claims_grounded=sum(1 for c in claims if c.grounding_status == GroundingStatus.GROUNDED),
            claims_partial=sum(1 for c in claims if c.grounding_status == GroundingStatus.PARTIALLY_GROUNDED),
            claims_unsupported=sum(1 for c in claims if c.grounding_status == GroundingStatus.UNGROUNDED and c.requires_grounding),
            claims_contradicted=sum(1 for c in claims if c.grounding_status == GroundingStatus.CONTRADICTED),
            score=score,
            findings=findings,
            trace=trace,
        )

        mat_id = getattr(material, "material_id", getattr(material, "blueprint_id", "material_text"))

        return GroundedMaterialContext(
            material_id=str(mat_id),
            claims=claims,
            evidence=list(all_evidences_dict.values()),
            links=all_links,
            citations=provenances,
            report=report,
        )
