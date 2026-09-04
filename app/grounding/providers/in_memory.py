"""
Deterministic In-Memory Knowledge Provider for offline testing and fast local retrieval.
"""

from __future__ import annotations

import re
from typing import Any
from app.grounding.contracts import (
    Evidence,
    EvidenceType,
    FreshnessStatus,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeSource,
    KnowledgeSourceType,
    SourceAuthority,
)
from app.grounding.providers.base import KnowledgeProvider
from app.grounding.providers.contracts import KnowledgeQuery


class InMemoryKnowledgeProvider(KnowledgeProvider):
    """Stores knowledge documents and chunks in-memory and provides lexical search."""

    def __init__(self, provider_id: str = "in_memory_provider") -> None:
        self._provider_id = provider_id
        self.sources: dict[str, KnowledgeSource] = {}
        self.documents: dict[str, KnowledgeDocument] = {}
        self.chunks: dict[str, KnowledgeChunk] = {}

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def add_source(self, source: KnowledgeSource) -> None:
        self.sources[source.source_id] = source

    def add_document(self, doc: KnowledgeDocument, chunks: list[KnowledgeChunk] | None = None) -> None:
        self.documents[doc.document_id] = doc
        if chunks:
            for ch in chunks:
                self.chunks[ch.chunk_id] = ch
        else:
            # Auto-split by paragraph/sentence
            paras = [p.strip() for p in doc.content.split("\n") if p.strip()]
            for idx, p in enumerate(paras):
                cid = f"chk_{doc.document_id}_{idx}"
                self.chunks[cid] = KnowledgeChunk(
                    chunk_id=cid,
                    document_id=doc.document_id,
                    source_id=doc.source_id,
                    content=p,
                    position=idx,
                    section="body",
                )

    def search(self, query: KnowledgeQuery) -> list[Evidence]:
        q_tokens = set(re.findall(r"\w+", query.query.lower()))
        results: list[tuple[float, Evidence]] = []

        for cid, chk in self.chunks.items():
            doc = self.documents.get(chk.document_id)
            src = self.sources.get(chk.source_id)
            if not doc or not src:
                continue

            # Domain filtering
            if query.domain and query.domain != "general" and doc.domain != "general" and doc.domain != query.domain:
                continue

            c_tokens = set(re.findall(r"\w+", chk.content.lower()))
            if not c_tokens:
                continue

            # Jaccard / token overlap scoring
            overlap = len(q_tokens.intersection(c_tokens))
            if overlap == 0:
                continue

            score = round(overlap / (len(q_tokens) + 1e-6), 3)
            ev_type = EvidenceType.DEFINITION if "is defined" in chk.content.lower() or "means" in chk.content.lower() else EvidenceType.DIRECT_STATEMENT

            ev = Evidence(
                evidence_id=f"ev_{cid}",
                source_id=src.source_id,
                chunk_id=cid,
                evidence_type=ev_type,
                content=chk.content,
                authority=src.authority,
                relevance_score=score,
                freshness=FreshnessStatus.TIME_INSENSITIVE,
                domain=doc.domain,
            )
            results.append((score, ev))

        results.sort(key=lambda x: x[0], reverse=True)
        return [ev for _, ev in results[: query.top_k]]

    def get_document(self, document_id: str) -> KnowledgeDocument | None:
        return self.documents.get(document_id)

    def get_source(self, source_id: str) -> KnowledgeSource | None:
        return self.sources.get(source_id)
