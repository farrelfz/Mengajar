"""
Knowledge Retrieval Engine: Multi-provider query federation, deduplication, and deterministic candidate aggregation.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from app.grounding.contracts import Evidence
from app.grounding.providers.base import KnowledgeProvider
from app.grounding.providers.contracts import KnowledgeQuery
from app.grounding.providers.registry import KnowledgeProviderRegistry


class RetrievedEvidence(BaseModel):
    evidence: Evidence
    retrieval_score: float
    provider_id: str
    rank: int


class RetrievalEngine:
    """Federates queries across registered knowledge providers deterministically."""

    def __init__(self, providers: list[KnowledgeProvider] | None = None) -> None:
        self.providers = providers or KnowledgeProviderRegistry.list_all()

    def retrieve(self, query: KnowledgeQuery) -> list[RetrievedEvidence]:
        all_candidates: dict[str, tuple[float, Evidence, str]] = {}

        for provider in self.providers:
            evidences = provider.search(query)
            for ev in evidences:
                key = f"{ev.source_id}_{ev.content.strip().lower()}"
                score = ev.relevance_score
                if key not in all_candidates or score > all_candidates[key][0]:
                    all_candidates[key] = (score, ev, provider.provider_id)

        # Sort deterministically
        sorted_ev = sorted(all_candidates.values(), key=lambda x: (x[0], x[1].evidence_id), reverse=True)

        results: list[RetrievedEvidence] = []
        for rank, (score, ev, p_id) in enumerate(sorted_ev[: query.top_k], start=1):
            results.append(
                RetrievedEvidence(
                    evidence=ev,
                    retrieval_score=score,
                    provider_id=p_id,
                    rank=rank,
                )
            )
        return results
