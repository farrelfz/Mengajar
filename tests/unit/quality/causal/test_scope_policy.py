"""
Universal Document Intelligence System V5 — Scope Policy Tests.

Phase 3A.2 Tests 13–17:
- Test 13: Local scope determination
- Test 14: Cluster scope determination
- Test 15: Systemic scope determination
- Test 16: Artifact-wide scope determination
- Test 17: Multi-format scope policy thresholds
"""

import pytest

from app.quality.causal.scope import FailureScope, ScopePolicy


def test_13_local_scope_determination():
    """Test 13: Single isolated page defect (<= 15% of document) resolves to LOCAL."""
    policy = ScopePolicy(local_threshold=0.15, cluster_consecutive_min=3, systemic_threshold=0.50)
    
    # 1 page out of 10 pages = 10% (<= 15%)
    scope = policy.determine_scope(affected_pages=[2], total_pages=10)
    assert scope == FailureScope.LOCAL

    # Empty pages resolves to LOCAL
    assert policy.determine_scope(affected_pages=[], total_pages=10) == FailureScope.LOCAL


def test_14_cluster_scope_determination():
    """Test 14: Consecutive streak of 3+ pages resolves to CLUSTER."""
    policy = ScopePolicy(local_threshold=0.15, cluster_consecutive_min=3, systemic_threshold=0.50)
    
    # 3 consecutive slides in a 12-slide presentation (25% < 50%, but streak == 3)
    scope = policy.determine_scope(affected_pages=[3, 4, 5], total_pages=12)
    assert scope == FailureScope.CLUSTER


def test_15_systemic_scope_determination():
    """Test 15: Defect affecting > 50% of document resolves to SYSTEMIC."""
    policy = ScopePolicy(local_threshold=0.15, cluster_consecutive_min=3, systemic_threshold=0.50)
    
    # 6 non-consecutive pages out of 10 pages = 60% (> 50%)
    scope = policy.determine_scope(affected_pages=[1, 3, 5, 7, 8, 9], total_pages=10)
    assert scope == FailureScope.SYSTEMIC


def test_16_artifact_wide_scope_determination():
    """Test 16: Document-level structural defects evaluate to ARTIFACT_WIDE."""
    policy = ScopePolicy()
    
    # Explicit document-level flag
    scope = policy.determine_scope(
        affected_pages=[1],
        total_pages=10,
        is_document_level=True,
    )
    assert scope == FailureScope.ARTIFACT_WIDE


def test_17_multiformat_scope_policy_thresholds():
    """Test 17: Format-calibrated policies for Handout, Presentation, Worksheet, Scientific."""
    pres_policy = ScopePolicy.for_artifact("PRESENTATION")
    hand_policy = ScopePolicy.for_artifact("HANDOUT")
    work_policy = ScopePolicy.for_artifact("WORKSHEET")
    sci_policy = ScopePolicy.for_artifact("SCIENTIFIC_DOCUMENT")

    # Presentation requires streak >= 3 for CLUSTER
    assert pres_policy.cluster_consecutive_min == 3
    # Streak of 2 in 10-slide deck is LOCAL
    assert pres_policy.determine_scope([2, 3], total_pages=10) == FailureScope.LOCAL

    # Handout with 2 consecutive pages in 8-page document forms a section streak (CLUSTER)
    assert hand_policy.cluster_consecutive_min == 2
    assert hand_policy.determine_scope([2, 3], total_pages=8) == FailureScope.CLUSTER

    # Scientific document 2 consecutive pages forms a section streak (CLUSTER)
    assert sci_policy.cluster_consecutive_min == 2
    assert sci_policy.determine_scope([4, 5], total_pages=12) == FailureScope.CLUSTER

    # Worksheet accommodates localized activity blocks
    assert work_policy.local_threshold == 0.20
