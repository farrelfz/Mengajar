"""
Universal Document Intelligence System V5 — Causal Reach Model.

Phase 3D.1: Hierarchy of causal reach comparing root cause depth against
strategy reach to prevent under-powered local mutations from treating structural root causes.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Optional, Tuple

from app.quality.repair.root_cause import RootCauseType


class CausalReach(str, Enum):
    """Hierarchical reach of a repair strategy."""
    LOCAL_RENDER_GEOMETRY = "LOCAL_RENDER_GEOMETRY"               # Depth 1: R0, CSS/tokens, padding, font scale
    COMPONENT_SPATIAL_STRUCTURE = "COMPONENT_SPATIAL_STRUCTURE"   # Depth 2: R1, card grid, column layout remap
    PAGE_COMPOSITION = "PAGE_COMPOSITION"                         # Depth 3: R2, pagination, slide split, section reflow
    PEDAGOGICAL_STRUCTURE = "PEDAGOGICAL_STRUCTURE"               # Depth 4: R3, activity resequencing, anti-spoiling
    SEMANTIC_INTEGRITY = "SEMANTIC_INTEGRITY"                     # Depth 4: R3, citation linking, claim evidence mapping

    @property
    def depth(self) -> int:
        if self == CausalReach.LOCAL_RENDER_GEOMETRY:
            return 1
        elif self == CausalReach.COMPONENT_SPATIAL_STRUCTURE:
            return 2
        elif self == CausalReach.PAGE_COMPOSITION:
            return 3
        elif self in (CausalReach.PEDAGOGICAL_STRUCTURE, CausalReach.SEMANTIC_INTEGRITY):
            return 4
        return 1


class CausalReachModel:
    """Enforces causal reach sufficiency between root causes and repair strategies."""

    _ROOT_CAUSE_DEPTH_MAP: Dict[RootCauseType, CausalReach] = {
        RootCauseType.PADDING_SPACING: CausalReach.LOCAL_RENDER_GEOMETRY,
        RootCauseType.TYPOGRAPHY: CausalReach.LOCAL_RENDER_GEOMETRY,
        RootCauseType.GRID_GEOMETRY: CausalReach.COMPONENT_SPATIAL_STRUCTURE,
        RootCauseType.SEMANTIC_LAYOUT_MAPPING: CausalReach.COMPONENT_SPATIAL_STRUCTURE,
        RootCauseType.CONTENT_DENSITY: CausalReach.PAGE_COMPOSITION,
        RootCauseType.PAGE_BREAK: CausalReach.PAGE_COMPOSITION,
        RootCauseType.INQUIRY_STRUCTURE: CausalReach.PEDAGOGICAL_STRUCTURE,
        RootCauseType.NARRATIVE_ORDER: CausalReach.PEDAGOGICAL_STRUCTURE,
        RootCauseType.EVIDENCE_MAPPING: CausalReach.SEMANTIC_INTEGRITY,
        RootCauseType.SOURCE_INSUFFICIENCY: CausalReach.SEMANTIC_INTEGRITY,
        RootCauseType.UNKNOWN: CausalReach.SEMANTIC_INTEGRITY,
    }

    @classmethod
    def get_required_reach(cls, root_cause: RootCauseType) -> CausalReach:
        """Returns the minimum causal reach required to resolve the given root cause."""
        return cls._ROOT_CAUSE_DEPTH_MAP.get(root_cause, CausalReach.LOCAL_RENDER_GEOMETRY)

    @classmethod
    def is_reach_sufficient(
        cls,
        strategy_reach: CausalReach,
        root_cause: RootCauseType,
    ) -> bool:
        """
        Validates whether strategy reach has enough causal depth to address the root cause.
        Prevents Depth 1 local padding strategies from attempting Depth 2+ structural collisions.
        """
        required = cls.get_required_reach(root_cause)
        return strategy_reach.depth >= required.depth
