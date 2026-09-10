"""
Universal Knowledge Core — UniversalKnowledgeManifest Schema.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.intelligence.schemas.intent_constraints import AudienceProfile
from app.intelligence.schemas.knowledge_unit import IntrinsicImportance, KnowledgeUnit
from app.intelligence.schemas.relationships import KnowledgeRelationship


class UniversalKnowledgeManifest(BaseModel):
    """Authoritative, artifact-neutral manifest of source knowledge.
    
    Strictly immutable post-compilation. Does NOT contain min_slides, max_slides,
    target_slides, page_count, layout, visual_intent, font_size, column_count,
    IMRAD headings, answer_space, or CSS.
    """
    model_config = ConfigDict(frozen=True)

    manifest_id: str
    document_title: str
    domain: str
    audience_profile: AudienceProfile = Field(default_factory=AudienceProfile)
    created_at: float = Field(default_factory=time.time)

    # Core Source of Truth: Atomic Units & Graph Edges
    units: Dict[str, KnowledgeUnit] = Field(default_factory=dict)
    relationships: Tuple[KnowledgeRelationship, ...] = Field(default_factory=tuple)

    # Source Statistics
    total_sections: int = 0
    total_raw_blocks: int = 0
    ambiguity_ratio: float = 0.0

    def get_unit(self, unit_id: str) -> Optional[KnowledgeUnit]:
        return self.units.get(unit_id)

    def get_units_by_importance(self, importance: IntrinsicImportance) -> List[KnowledgeUnit]:
        return [u for u in self.units.values() if u.intrinsic_importance == importance]

    def get_units_by_category(self, category: str) -> List[KnowledgeUnit]:
        return [u for u in self.units.values() if u.category.value == category or u.category == category]
