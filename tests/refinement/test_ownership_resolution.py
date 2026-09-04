"""
Unit tests for Refinement Ownership Resolution.
"""

import pytest
from app.critic.contracts import CritiqueConfidence, CritiqueFinding, CritiquePerspective, CritiqueSeverity
from app.quality.contracts import QualityDimension, QualityFinding, QualitySeverity
from app.refinement.contracts import RefinementIntent, RefinementTargetLayer
from app.refinement.ownership import RefinementOwnershipResolver


def test_pedagogical_order_finding_resolves_to_director_not_renderer():
    qf = QualityFinding(
        dimension=QualityDimension.PEDAGOGICAL_ALIGNMENT,
        severity=QualitySeverity.ERROR,
        finding="Worked example appears before concept formalization.",
        recommendation="Reorder stages.",
    )
    layer, intent, scope = RefinementOwnershipResolver.resolve_quality_finding(qf)
    assert layer == RefinementTargetLayer.DIRECTOR
    assert intent == RefinementIntent.REORDER


def test_density_finding_resolves_to_density_layer():
    cf = CritiqueFinding(
        id="cf_dense",
        perspective=CritiquePerspective.COGNITIVE_LOAD,
        title="Excessive Text Volume on Presentation Slide",
        observation="2000 chars on 16:9 slide.",
        diagnosis="Exceeds cognitive load limit.",
        why_it_matters="Working memory overload.",
        severity=CritiqueSeverity.HIGH,
        confidence=CritiqueConfidence.HIGH,
        improvement_direction="Split or rebalance density.",
    )
    layer, intent, scope = RefinementOwnershipResolver.resolve_critic_finding(cf)
    assert layer == RefinementTargetLayer.DENSITY
    assert intent == RefinementIntent.REBALANCE_DENSITY


def test_capability_mismatch_resolves_to_capability_selection_layer():
    cf = CritiqueFinding(
        id="cf_cap",
        perspective=CritiquePerspective.CAPABILITY_SELECTION,
        title="Parallel Component Used for Directional Sequential Process",
        observation="Step 1, Step 2 in comparison block.",
        diagnosis="Topology mismatch.",
        why_it_matters="Loss of sequence.",
        severity=CritiqueSeverity.MEDIUM,
        confidence=CritiqueConfidence.HIGH,
        improvement_direction="Re-resolve component to STEP_BLOCK.",
    )
    layer, intent, scope = RefinementOwnershipResolver.resolve_critic_finding(cf)
    assert layer == RefinementTargetLayer.CAPABILITY_SELECTION
    assert intent == RefinementIntent.REPLACE_CAPABILITY
