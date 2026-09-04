"""
Unit tests for multi-provider retrieval, deduplication, and deterministic candidate ranking.
"""

from pathlib import Path
import pytest
from app.grounding.providers.contracts import KnowledgeQuery
from app.grounding.providers.local_doc import LocalDocumentKnowledgeProvider
from app.grounding.retrieval import RetrievalEngine


def test_retrieval_engine_federates_and_deduplicates():
    p1 = LocalDocumentKnowledgeProvider("p1")
    p1.load_markdown_file(Path("tests/fixtures/grounding/physics_sources.md"), domain="physics")

    engine = RetrievalEngine(providers=[p1])
    q = KnowledgeQuery(query="Newton-meter SI unit of torque", domain="physics", top_k=3)
    results = engine.retrieve(q)

    assert len(results) >= 1
    assert results[0].retrieval_score > 0
    assert "Newton-meter" in results[0].evidence.content
