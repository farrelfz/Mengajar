"""
Capability Selection Critic: Evaluates semantic appropriateness of resolved UI component choices.
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
from app.design.schemas import ComponentFamily


class CapabilitySelectionCritic(BaseCritic):
    """Examines whether resolved capability component families match semantic instructional intent."""

    @property
    def critic_id(self) -> str:
        return "capability_selection"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.CAPABILITY_SELECTION

    def can_critique(self, context: CritiqueContext) -> bool:
        return context.composition is not None or context.resolution_trace is not None

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        findings: list[CritiqueFinding] = []

        # Check for Causal Sequence encoded in parallel Comparison or Reference Topology
        if context.composition is not None:
            for p in context.composition.pages:
                for r in p.regions.values():
                    for b in r.blocks:
                        raw_lower = str(b.raw_content or "").lower()
                        # If content describes a linear sequential process (Step 1 -> Step 2 -> Step 3)
                        is_sequential = "step 1" in raw_lower and "step 2" in raw_lower and "step 3" in raw_lower
                        # But component family is a parallel category comparison or reference block
                        if is_sequential and b.component_family in [ComponentFamily.COMPARISON_BLOCK, ComponentFamily.REFERENCE_BLOCK]:
                            findings.append(
                                CritiqueFinding(
                                    id=f"cap_parallel_for_sequential_process_p{p.page_number}",
                                    perspective=self.perspective,
                                    title="Parallel Component Used for Directional Sequential Process",
                                    observation=f"Page {p.page_number} formats a 3-step sequential process inside a parallel '{b.component_family.value}' component.",
                                    diagnosis="A comparison block visually implies independent parallel categories, obscuring the linear causal dependency between steps.",
                                    why_it_matters="Learners may read parallel items out of order, misunderstanding the essential temporal or causal chain.",
                                    evidence=[
                                        CritiqueEvidence(
                                            source="composition.pages",
                                            location=f"Page {p.page_number}",
                                            observation=f"Sequential text steps placed inside ComponentFamily.{b.component_family.name}.",
                                            supporting_data={"component_family": str(b.component_family.value), "page_number": p.page_number},
                                        )
                                    ],
                                    severity=CritiqueSeverity.MEDIUM,
                                    confidence=CritiqueConfidence.HIGH,
                                    affected_locations=[f"Page {p.page_number}"],
                                    improvement_direction="Re-resolve component family to a linear STEP_BLOCK or TIMELINE_ITEM component.",
                                )
                            )

        return findings
