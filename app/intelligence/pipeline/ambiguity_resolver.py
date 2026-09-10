"""
Stage 4 — AmbiguityResolver & SemanticResolutionProvider Interface.

Selective AI Gateway stage that resolves classification ambiguities ONLY for candidate units
whose rule confidence falls below AI_ESCALATION_THRESHOLD (0.70). Operates offline by default.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field

from app.intelligence.pipeline.local_classifier import RuleClassifiedUnit
from app.intelligence.schemas import ContentType
from app.intelligence.schemas.knowledge_unit import KnowledgeCategory, ResolutionStatus


class ResolvedUnit(BaseModel):
    classified_unit: RuleClassifiedUnit
    final_content_type: ContentType
    final_category: KnowledgeCategory
    final_confidence: float
    resolution_status: ResolutionStatus = ResolutionStatus.LOCAL_CONFIDENT
    ai_resolved: bool = False
    ai_reasoning: Optional[str] = None


class SemanticResolutionProvider(ABC):
    """Injectable interface for selective AI resolution."""

    @abstractmethod
    async def resolve_ambiguities(
        self,
        ambiguous_units: List[RuleClassifiedUnit],
    ) -> List[ResolvedUnit]:
        """Resolves ambiguous units via AI or mock offline resolution."""
        pass

    async def resolve_unit(self, unit: RuleClassifiedUnit) -> ResolvedUnit:
        """Convenience method to resolve a single unit."""
        results = await self.resolve_ambiguities([unit])
        return results[0]


class OfflineMockResolutionProvider(SemanticResolutionProvider):
    """Default 100% offline resolution provider for tests and local execution."""

    async def resolve_ambiguities(
        self,
        ambiguous_units: List[RuleClassifiedUnit],
    ) -> List[ResolvedUnit]:
        resolved: List[ResolvedUnit] = []
        for u in ambiguous_units:
            # Epistemic honesty: DO NOT artificially inflate confidence to 0.85 offline.
            # Mark explicitly as UNRESOLVED_OFFLINE while preserving local rule confidence.
            resolved.append(
                ResolvedUnit(
                    classified_unit=u,
                    final_content_type=u.content_type,
                    final_category=u.category,
                    final_confidence=u.confidence,
                    resolution_status=ResolutionStatus.UNRESOLVED_OFFLINE,
                    ai_resolved=False,
                    ai_reasoning="Compiled in offline mode; unresolved ambiguity retained using local classification fallback.",
                )
            )
        return resolved

    async def resolve_unit(self, unit: RuleClassifiedUnit) -> ResolvedUnit:
        """Directly resolve a single classified unit offline."""
        return ResolvedUnit(
            classified_unit=unit,
            final_content_type=unit.content_type,
            final_category=unit.category,
            final_confidence=unit.confidence,
            resolution_status=ResolutionStatus.UNRESOLVED_OFFLINE,
            ai_resolved=False,
            ai_reasoning="Compiled in offline mode; unresolved ambiguity retained using local classification fallback.",
        )


class AmbiguityResolver:
    """Stage 4: Selective AI reasoning stage with batching and offline fallback."""

    def __init__(
        self,
        provider: SemanticResolutionProvider | None = None,
        confidence_threshold: float = 0.70,
    ) -> None:
        self.provider = provider or OfflineMockResolutionProvider()
        self.confidence_threshold = confidence_threshold

    async def resolve(
        self,
        classified_units: List[RuleClassifiedUnit],
    ) -> List[ResolvedUnit]:
        clear_units: List[RuleClassifiedUnit] = []
        ambiguous_units: List[RuleClassifiedUnit] = []

        for u in classified_units:
            if u.is_ambiguous or u.confidence < self.confidence_threshold:
                ambiguous_units.append(u)
            else:
                clear_units.append(u)

        resolved_map: dict[str, ResolvedUnit] = {}

        # 1. Clear units bypass AI completely
        for u in clear_units:
            resolved_map[u.candidate.candidate_id] = ResolvedUnit(
                classified_unit=u,
                final_content_type=u.content_type,
                final_category=u.category,
                final_confidence=u.confidence,
                resolution_status=ResolutionStatus.LOCAL_CONFIDENT,
                ai_resolved=False,
            )

        # 2. Ambiguous units sent to AI provider in batch
        if ambiguous_units:
            try:
                ai_results = await self.provider.resolve_ambiguities(ambiguous_units)
                for res in ai_results:
                    resolved_map[res.classified_unit.candidate.candidate_id] = res
            except Exception as exc:
                # Fallback to local rule assignment with DEFERRED status on AI exception
                for u in ambiguous_units:
                    resolved_map[u.candidate.candidate_id] = ResolvedUnit(
                        classified_unit=u,
                        final_content_type=u.content_type,
                        final_category=u.category,
                        final_confidence=u.confidence,
                        resolution_status=ResolutionStatus.DEFERRED,
                        ai_resolved=False,
                        ai_reasoning=f"AI resolution exception, deferred fallback: {exc}",
                    )

        # Maintain original sequence order
        return [resolved_map[u.candidate.candidate_id] for u in classified_units]
