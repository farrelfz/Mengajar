"""
Visual Communication Critic: Analyzes visual rhythm, visual hierarchy, and component monotony.
"""

from __future__ import annotations

from app.critic.base import BaseCritic
from app.critic.context import CritiqueContext
from app.critic.contracts import (
    CritiqueConfidence,
    CritiqueEvidence,
    CritiqueFinding,
    CritiquePerspective,
    CritiqueSeverity,
)


class VisualCommunicationCritic(BaseCritic):
    """Evaluates visual hierarchy, layout monotony, and visual communication rhythm."""

    @property
    def critic_id(self) -> str:
        return "visual_communication"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.VISUAL_COMMUNICATION

    def can_critique(self, context: CritiqueContext) -> bool:
        return context.composition is not None

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        findings: list[CritiqueFinding] = []
        comp = context.composition
        if not comp or not comp.pages:
            return findings

        # Check for Visual Monotony: Identical composition_type across 4+ consecutive pages
        if len(comp.pages) >= 4:
            comp_types = [p.composition_type for p in comp.pages]
            if len(set(comp_types)) == 1:
                findings.append(
                    CritiqueFinding(
                        id="vis_layout_monotony",
                        perspective=self.perspective,
                        title="Visual Layout Monotony Across Document",
                        observation=f"All {len(comp.pages)} pages utilize the exact same layout topology '{comp_types[0]}'.",
                        diagnosis="A lack of structural variation across consecutive pages creates visual fatigue and fails to adapt layout to content semantics.",
                        why_it_matters="Varying visual rhythm sustains student engagement and visually distinguishes different cognitive phases.",
                        evidence=[
                            CritiqueEvidence(
                                source="composition.pages",
                                location="global",
                                observation=f"100% of pages use composition_type '{comp_types[0]}'.",
                                supporting_data={"page_count": len(comp.pages), "uniform_type": comp_types[0]},
                            )
                        ],
                        severity=CritiqueSeverity.MEDIUM,
                        confidence=CritiqueConfidence.HIGH,
                        affected_locations=["global"],
                        improvement_direction="Introduce complementary region topologies (e.g. side-by-side comparison, callout splits) to punctuate the presentation.",
                    )
                )

        return findings
