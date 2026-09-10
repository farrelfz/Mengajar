"""
Universal Document Intelligence System V5 — Multi-Layer Mutation Model.

Phase 4: Defines the 5 explicit transformation layers spanning token, component,
page composition, blueprint recomposition, and semantic organization.
"""

from __future__ import annotations
from enum import Enum


class TransformationLayer(str, Enum):
    """Explicit transformation layer representing structural actuation depth."""
    LAYER_0_TOKEN = "LAYER_0_TOKEN"
    LAYER_1_COMPONENT = "LAYER_1_COMPONENT"
    LAYER_2_PAGE_COMPOSITION = "LAYER_2_PAGE_COMPOSITION"
    LAYER_3_BLUEPRINT_RECOMPOSITION = "LAYER_3_BLUEPRINT_RECOMPOSITION"
    LAYER_4_SEMANTIC_ORGANIZATION = "LAYER_4_SEMANTIC_ORGANIZATION"

    @property
    def depth(self) -> int:
        _depths = {
            TransformationLayer.LAYER_0_TOKEN: 0,
            TransformationLayer.LAYER_1_COMPONENT: 1,
            TransformationLayer.LAYER_2_PAGE_COMPOSITION: 2,
            TransformationLayer.LAYER_3_BLUEPRINT_RECOMPOSITION: 3,
            TransformationLayer.LAYER_4_SEMANTIC_ORGANIZATION: 4,
        }
        return _depths[self]

    @property
    def is_structural(self) -> bool:
        return self.depth >= 1

    @property
    def is_blueprint_level(self) -> bool:
        return self.depth >= 3
