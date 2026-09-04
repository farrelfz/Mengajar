"""
Refinement Ownership Resolver: Maps quality and critic findings to their canonical architectural layer.
"""

from __future__ import annotations

from typing import Any
from app.critic.contracts import CritiqueFinding, CritiquePerspective
from app.quality.contracts import QualityDimension, QualityFinding
from app.refinement.contracts import RefinementIntent, RefinementScope, RefinementTargetLayer


class RefinementOwnershipResolver:
    """Deterministically resolves findings to target architectural layer, scope, and intent."""

    # Map QualityDimension -> Target Layer & Default Intent
    QUALITY_DIMENSION_MAPPING: dict[QualityDimension, tuple[RefinementTargetLayer, RefinementIntent, RefinementScope]] = {
        QualityDimension.PEDAGOGICAL_ALIGNMENT: (RefinementTargetLayer.DIRECTOR, RefinementIntent.REORDER, RefinementScope.SECTION),
        QualityDimension.SEMANTIC_CORRECTNESS: (RefinementTargetLayer.CONTENT, RefinementIntent.CLARIFY, RefinementScope.BLOCK),
        QualityDimension.STRUCTURAL_COHERENCE: (RefinementTargetLayer.COMPOSITION, RefinementIntent.FIX_STRUCTURE, RefinementScope.PAGE),
        QualityDimension.INFORMATION_DENSITY: (RefinementTargetLayer.DENSITY, RefinementIntent.REBALANCE_DENSITY, RefinementScope.PAGE),
        QualityDimension.REDUNDANCY: (RefinementTargetLayer.COMPOSITION, RefinementIntent.REMOVE_REDUNDANCY, RefinementScope.PAGE),
        QualityDimension.FORMAT_INTEGRITY: (RefinementTargetLayer.FORMAT_METADATA, RefinementIntent.FIX_STRUCTURE, RefinementScope.DOCUMENT),
        QualityDimension.VISUAL_APPROPRIATENESS: (RefinementTargetLayer.VISUAL_STRUCTURE, RefinementIntent.IMPROVE_TRANSITION, RefinementScope.PAGE),
    }

    # Map CritiquePerspective -> Target Layer & Default Intent
    CRITIC_PERSPECTIVE_MAPPING: dict[CritiquePerspective, tuple[RefinementTargetLayer, RefinementIntent, RefinementScope]] = {
        CritiquePerspective.PEDAGOGICAL: (RefinementTargetLayer.DIRECTOR, RefinementIntent.REORDER, RefinementScope.SECTION),
        CritiquePerspective.SEMANTIC: (RefinementTargetLayer.CONTENT, RefinementIntent.EXPAND, RefinementScope.BLOCK),
        CritiquePerspective.STRUCTURAL: (RefinementTargetLayer.BLUEPRINT, RefinementIntent.ADD_SCAFFOLDING, RefinementScope.SECTION),
        CritiquePerspective.COGNITIVE_LOAD: (RefinementTargetLayer.DENSITY, RefinementIntent.REBALANCE_DENSITY, RefinementScope.PAGE),
        CritiquePerspective.NARRATIVE: (RefinementTargetLayer.DIRECTOR, RefinementIntent.IMPROVE_TRANSITION, RefinementScope.DOCUMENT),
        CritiquePerspective.VISUAL_COMMUNICATION: (RefinementTargetLayer.VISUAL_STRUCTURE, RefinementIntent.REPLACE_CAPABILITY, RefinementScope.PAGE),
        CritiquePerspective.SCIENTIFIC_RIGOR: (RefinementTargetLayer.CONTENT, RefinementIntent.STRENGTHEN_EVIDENCE, RefinementScope.BLOCK),
        CritiquePerspective.AUDIENCE: (RefinementTargetLayer.CONTENT, RefinementIntent.SIMPLIFY, RefinementScope.BLOCK),
        CritiquePerspective.CAPABILITY_SELECTION: (RefinementTargetLayer.CAPABILITY_SELECTION, RefinementIntent.REPLACE_CAPABILITY, RefinementScope.BLOCK),
        CritiquePerspective.REDUNDANCY: (RefinementTargetLayer.COMPOSITION, RefinementIntent.REMOVE_REDUNDANCY, RefinementScope.PAGE),
    }

    @classmethod
    def resolve_quality_finding(
        cls, finding: QualityFinding
    ) -> tuple[RefinementTargetLayer, RefinementIntent, RefinementScope]:
        if finding.dimension in cls.QUALITY_DIMENSION_MAPPING:
            return cls.QUALITY_DIMENSION_MAPPING[finding.dimension]
        return (RefinementTargetLayer.COMPOSITION, RefinementIntent.FIX_STRUCTURE, RefinementScope.PAGE)

    @classmethod
    def resolve_critic_finding(
        cls, finding: CritiqueFinding
    ) -> tuple[RefinementTargetLayer, RefinementIntent, RefinementScope]:
        if finding.perspective in cls.CRITIC_PERSPECTIVE_MAPPING:
            return cls.CRITIC_PERSPECTIVE_MAPPING[finding.perspective]
        return (RefinementTargetLayer.COMPOSITION, RefinementIntent.CLARIFY, RefinementScope.PAGE)
