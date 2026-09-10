"""
Universal Document Intelligence System V5 — Canonical Failure Taxonomy Tests.

Phase 3A.2 Tests 9–12:
- Test 9: 10 Canonical Failure Domains completeness
- Test 10: Canonical Severity levels hierarchy and ordering
- Test 11: Detection Confidence vs Causal Confidence separation
- Test 12: Extensible failure code registry with domain association
"""

import pytest

from app.quality.causal.taxonomy import (
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalSeverity,
    CausalConfidence,
    DetectionConfidence,
    get_codes_for_domain,
    get_domain_for_code,
    register_canonical_code,
)


def test_09_canonical_failure_domains_completeness():
    """Test 9: CanonicalFailureDomain contains exactly the 10 specified domains."""
    expected_domains = {
        "PHYSICAL_RENDER",
        "BLUEPRINT_INTEGRITY",
        "SEMANTIC_TRACEABILITY",
        "PEDAGOGICAL_STRUCTURE",
        "COGNITIVE_LOAD",
        "STYLE_DESIGN",
        "SCIENTIFIC_RIGOR",
        "ACCESSIBILITY",
        "EXECUTION_CONTRACT",
        "EXPORT_PACKAGING",
    }
    actual_domains = {d.value for d in CanonicalFailureDomain}
    assert actual_domains == expected_domains
    assert len(CanonicalFailureDomain) == 10


def test_10_canonical_severity_hierarchy_and_ordering():
    """Test 10: Severity ranking strictly obeys INFO < WARNING < MINOR < MAJOR < CRITICAL < BLOCKING."""
    severities = [
        CanonicalSeverity.INFO,
        CanonicalSeverity.WARNING,
        CanonicalSeverity.MINOR,
        CanonicalSeverity.MAJOR,
        CanonicalSeverity.CRITICAL,
        CanonicalSeverity.BLOCKING,
    ]

    for i in range(len(severities) - 1):
        assert severities[i] < severities[i + 1]
        assert severities[i] <= severities[i + 1]
        assert severities[i + 1] > severities[i]
        assert severities[i + 1] >= severities[i]

    # Transitive checks
    assert CanonicalSeverity.INFO < CanonicalSeverity.BLOCKING
    assert CanonicalSeverity.WARNING < CanonicalSeverity.CRITICAL
    assert CanonicalSeverity.CRITICAL < CanonicalSeverity.BLOCKING


def test_11_detection_vs_causal_confidence_separation():
    """Test 11: Detection confidence is strictly separated from causal confidence."""
    # DetectionConfidence is for physical/structural observation
    det_values = {c.value for c in DetectionConfidence}
    assert det_values == {"HIGH", "MEDIUM", "LOW"}

    # CausalConfidence is for root cause hypothesis attribution
    causal_values = {c.value for c in CausalConfidence}
    assert "UNKNOWN" in causal_values
    assert "HIGH" in causal_values

    # Distinct enum types with different semantic scopes
    assert DetectionConfidence is not CausalConfidence
    assert type(DetectionConfidence.HIGH) is not type(CausalConfidence.HIGH)
    assert isinstance(DetectionConfidence.HIGH, DetectionConfidence)
    assert not isinstance(DetectionConfidence.HIGH, CausalConfidence)
    assert "UNKNOWN" not in det_values
    assert "UNKNOWN" in causal_values


def test_12_failure_code_registry_and_domain_association():
    """Test 12: Every canonical failure code associates with a domain and supports registry lookup."""
    # Check standard codes mapped to domains
    assert CanonicalFailureCode.TEXT_CLIPPING.domain == CanonicalFailureDomain.PHYSICAL_RENDER
    assert CanonicalFailureCode.UNSUPPORTED_CLAIM.domain == CanonicalFailureDomain.SEMANTIC_TRACEABILITY
    assert CanonicalFailureCode.INQUIRY_FLOW_BREAK.domain == CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE
    assert CanonicalFailureCode.LAYOUT_MONOTONY.domain == CanonicalFailureDomain.STYLE_DESIGN
    assert CanonicalFailureCode.CONTRAST_DEFICIT.domain == CanonicalFailureDomain.ACCESSIBILITY
    assert CanonicalFailureCode.EXECUTION_TIMEOUT.domain == CanonicalFailureDomain.EXECUTION_CONTRACT
    assert CanonicalFailureCode.METADATA_CORRUPTION.domain == CanonicalFailureDomain.EXPORT_PACKAGING

    # Query codes by domain
    render_codes = get_codes_for_domain(CanonicalFailureDomain.PHYSICAL_RENDER)
    assert CanonicalFailureCode.TEXT_CLIPPING in render_codes
    assert CanonicalFailureCode.ELEMENT_COLLISION in render_codes

    # Dynamic registry extension
    new_code = register_canonical_code("CUSTOM_COLOR_ACCESSIBILITY_FLAW", CanonicalFailureDomain.ACCESSIBILITY)
    assert get_domain_for_code(new_code) == CanonicalFailureDomain.ACCESSIBILITY
