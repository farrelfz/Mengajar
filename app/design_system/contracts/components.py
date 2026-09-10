"""
Universal Design System — Component Contracts.

Phase 3B.0: Canonical component specifications, slot definitions,
artifact compatibility invariants, and token bindings.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field


class ComponentCategory(str, Enum):
    """Semantic component categories across document artifacts."""
    HEADER = "HEADER"
    FOOTER = "FOOTER"
    CARD = "CARD"
    STAT_CALLOUT = "STAT_CALLOUT"
    TIMELINE_ITEM = "TIMELINE_ITEM"
    PROCESS_STEP = "PROCESS_STEP"
    COMPARISON_COLUMN = "COMPARISON_COLUMN"
    CALLOUT_BOX = "CALLOUT_BOX"
    RESPONSE_WORKSPACE = "RESPONSE_WORKSPACE"
    FORMULA_BLOCK = "FORMULA_BLOCK"
    EVIDENCE_CARD = "EVIDENCE_CARD"
    TABLE = "TABLE"
    KEY_TAKEAWAY = "KEY_TAKEAWAY"


class SlotSpec(BaseModel):
    """Typed slot within a component layout."""
    model_config = ConfigDict(frozen=True)

    name: str
    is_required: bool = True
    allowed_content_types: Tuple[str, ...] = ("text",)
    min_chars: int = 0
    max_chars: Optional[int] = None
    default_semantic_token: Optional[str] = None


class ComponentSpec(BaseModel):
    """Specification of an architectural document component."""
    model_config = ConfigDict(frozen=True)

    component_id: str
    category: ComponentCategory
    allowed_artifacts: Tuple[str, ...] = (
        "PRESENTATION",
        "HANDOUT",
        "WORKSHEET",
        "SCIENTIFIC_DOCUMENT",
    )
    slots: Tuple[SlotSpec, ...] = ()
    min_width_pt: float = 0.0
    min_height_pt: float = 0.0
    token_bindings: Dict[str, str] = Field(default_factory=dict)
    density_weight: float = 1.0
    is_anti_spoiling_sensitive: bool = False
    description: str = ""

    def is_allowed_for(self, artifact_type: str) -> bool:
        """Enforces INV-DESIGN-010: artifact-specific component whitelist."""
        return artifact_type.upper() in [a.upper() for a in self.allowed_artifacts]

    def get_slot(self, name: str) -> Optional[SlotSpec]:
        """Retrieves a slot specification by name."""
        for slot in self.slots:
            if slot.name == name:
                return slot
        return None
