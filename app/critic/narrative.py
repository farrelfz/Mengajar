"""
Narrative Critic: Evaluates rhetorical arc, curiosity hooks, transitions, and narrative closure.
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


class NarrativeCritic(BaseCritic):
    """Examines narrative coherence, rhetorical tension, and closure in instructional materials."""

    @property
    def critic_id(self) -> str:
        return "narrative"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.NARRATIVE

    def can_critique(self, context: CritiqueContext) -> bool:
        return context.composition is not None or context.journey is not None

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        findings: list[CritiqueFinding] = []

        # Check for abrupt document termination / missing closure
        if context.composition is not None and len(context.composition.pages) >= 3:
            last_page = context.composition.pages[-1]
            last_page_types = [str(r.role.value if hasattr(r.role, "value") else r.role) for r in last_page.regions.values()]
            # If the last page contains only raw worked exercise or un-summarized formula without a wrap-up/conclusion
            if last_page.page_type not in ["summary", "conclusion", "reflection"] and len(context.composition.pages) > 4:
                findings.append(
                    CritiqueFinding(
                        id="narrative_abrupt_closure",
                        perspective=self.perspective,
                        title="Abrupt Narrative Termination Without Synthesis",
                        observation=f"Multi-page document terminates abruptly on Page {last_page.page_number} without a consolidation or reflection page.",
                        diagnosis="The instructional journey ends immediately after an exercise or derivation without providing a synthesis of key takeaways.",
                        why_it_matters="A clear narrative payoff and summary consolidates learning and solidifies the overarching message in long-term memory.",
                        evidence=[
                            CritiqueEvidence(
                                source="composition.pages",
                                location=f"Page {last_page.page_number}",
                                observation=f"Final page type is '{last_page.page_type}' rather than summary or conclusion.",
                                supporting_data={"page_count": len(context.composition.pages), "last_page_type": last_page.page_type},
                            )
                        ],
                        severity=CritiqueSeverity.LOW,
                        confidence=CritiqueConfidence.MEDIUM,
                        affected_locations=[f"Page {last_page.page_number}"],
                        improvement_direction="Append a concise synthesis slide or reflection prompt that contextualizes what the learner accomplished.",
                    )
                )

        return findings
