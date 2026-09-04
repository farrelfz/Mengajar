"""
Unit tests for InMemory and LocalDocument Knowledge Providers.
"""

from pathlib import Path
import pytest
from app.grounding.contracts import KnowledgeSource, KnowledgeSourceType, SourceAuthority
from app.grounding.providers.contracts import KnowledgeQuery
from app.grounding.providers.in_memory import InMemoryKnowledgeProvider
from app.grounding.providers.local_doc import LocalDocumentKnowledgeProvider


def test_in_memory_provider_search():
    provider = InMemoryKnowledgeProvider("test_prov")
    src = KnowledgeSource(source_id="s1", title="Mechanics", authority=SourceAuthority.PRIMARY, domain="physics")
    provider.add_source(src)

    from app.grounding.contracts import KnowledgeDocument
    doc = KnowledgeDocument(document_id="d1", source_id="s1", title="Mechanics", content="Torque is defined as rotational force tau = r * F sin(theta).", domain="physics")
    provider.add_document(doc)

    q = KnowledgeQuery(query="torque equation", domain="physics", top_k=2)
    results = provider.search(q)

    assert len(results) >= 1
    assert "Torque is defined" in results[0].content


def test_local_document_provider_loads_fixture():
    fixture_path = Path("tests/fixtures/grounding/physics_sources.md")
    provider = LocalDocumentKnowledgeProvider("local_fixture")
    provider.load_markdown_file(fixture_path, domain="physics", authority=SourceAuthority.PRIMARY)

    assert len(provider.documents) >= 1
    q = KnowledgeQuery(query="gravitational acceleration", domain="physics", top_k=1)
    results = provider.search(q)
    assert len(results) >= 1
    assert "9.8" in results[0].content
