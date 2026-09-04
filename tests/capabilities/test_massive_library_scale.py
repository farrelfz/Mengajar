"""
Test Suite for Batch 10 Massive Capability Library Expansion.

Verifies:
1. 60+ to 80+ distinct capabilities registered.
2. Valid taxonomy signature on all capabilities.
3. No duplicate IDs.
4. Balanced family distribution.
5. High-performance discovery and resolution.
6. Cross-domain template reuse across domain packs.
7. Machine-readable catalog API functionality.
"""

import time
import pytest

from app.capabilities.contracts import Capability
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.taxonomy import CapabilityFamily, SemanticIntent
from app.libraries import register_all_default_capabilities
from app.libraries.catalog import CapabilityCatalog


@pytest.fixture
def populated_registry() -> CapabilityRegistry:
    reg = CapabilityRegistry()
    register_all_default_capabilities(reg)
    return reg


@pytest.fixture
def catalog(populated_registry: CapabilityRegistry) -> CapabilityCatalog:
    return CapabilityCatalog(registry=populated_registry)


def test_massive_capability_count(catalog: CapabilityCatalog):
    summary = catalog.get_summary()
    total = summary["total_capabilities"]
    # Verify 80+ capabilities registered
    assert total >= 80, f"Expected at least 80 capabilities, got {total}"
    assert summary["domains_count"] >= 5


def test_all_capabilities_have_valid_taxonomy(catalog: CapabilityCatalog):
    all_caps = catalog.list_capabilities()
    for cap in all_caps:
        meta = cap.metadata
        assert meta.capability_id, "Capability ID must not be empty"
        assert meta.taxonomy is not None, f"Taxonomy missing on {meta.capability_id}"
        assert isinstance(meta.taxonomy.family, CapabilityFamily)
        assert isinstance(meta.taxonomy.primary_intent, SemanticIntent)
        assert len(meta.semantic_tags) > 0, f"Semantic tags empty on {meta.capability_id}"
        assert len(meta.supported_artifacts) > 0, f"Supported artifacts empty on {meta.capability_id}"


def test_no_duplicate_capability_ids(catalog: CapabilityCatalog):
    all_caps = catalog.list_capabilities()
    ids = [c.metadata.capability_id for c in all_caps]
    assert len(ids) == len(set(ids)), f"Duplicate capability IDs detected: {len(ids) - len(set(ids))}"


def test_family_distribution_diversity(catalog: CapabilityCatalog):
    summary = catalog.get_summary()
    by_family = summary["capabilities_by_family"]
    # Ensure at least 6 distinct families are utilized in the ecosystem
    assert len(by_family) >= 6, f"Expected broad family diversity, got {len(by_family)} families"
    assert "process_visualization" in by_family
    assert "comparative_reasoning" in by_family
    assert "concept_structure" in by_family


def test_lookup_performance_high_throughput(catalog: CapabilityCatalog):
    # Benchmark 1,000 queries against the registry
    start = time.perf_counter()
    for _ in range(1000):
        res = catalog.find_by_intent(SemanticIntent.SEQUENCE)
        assert len(res) > 0
    duration_ms = (time.perf_counter() - start) * 1000
    # 1,000 lookups should easily finish in under 250ms
    assert duration_ms < 250.0, f"Lookup performance too slow: {duration_ms:.2f}ms for 1000 queries"


def test_cross_domain_reuse_across_six_domains(catalog: CapabilityCatalog):
    # Verify the PROCESS family is reused across multiple diverse domain packs
    process_caps = catalog.find_by_family(CapabilityFamily.PROCESS_VISUALIZATION)
    domains = {c.metadata.domain for c in process_caps}
    assert len(domains) >= 3, f"Expected at least 3 distinct domains using Process family, got {domains}"

    # Check key domain capabilities exist
    cap_ids = {c.metadata.capability_id for c in process_caps}
    assert "diagram.process_flow" in cap_ids or "pedagogy.concept_progression" in cap_ids
    assert "writing.paragraph_anatomy" in cap_ids
    assert "experiment.procedure_flow" in cap_ids
    assert "data.chart_reading_framework" in cap_ids


def test_catalog_api_filters(catalog: CapabilityCatalog):
    domains = catalog.list_domains()
    assert "general" in domains or "research_education" in domains

    comparison_caps = catalog.find_by_intent(SemanticIntent.COMPARE)
    assert len(comparison_caps) >= 5
    for c in comparison_caps:
        assert c.metadata.taxonomy.primary_intent == SemanticIntent.COMPARE
