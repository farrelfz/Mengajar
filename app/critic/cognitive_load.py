"""
Cognitive Load Critic: Evaluates working memory demands, concurrency, and split-attention risks.
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


class CognitiveLoadCritic(BaseCritic):
    """Analyzes working memory saturation, split attention, and concurrent novelty overload."""

    @property
    def critic_id(self) -> str:
        return "cognitive_load"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.COGNITIVE_LOAD

    def can_critique(self, context: CritiqueContext) -> bool:
        return context.composition is not None or context.blueprint is not None

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        findings: list[CritiqueFinding] = []

        # 1. Simultaneous Concept Novelty Overload
        if context.blueprint is not None and context.blueprint.content:
            concepts = context.blueprint.content.concepts
            if len(concepts) >= 6:
                findings.append(
                    CritiqueFinding(
                        id="cog_excessive_concurrent_concepts",
                        perspective=self.perspective,
                        title="Simultaneous Concept Introduction Overload",
                        observation=f"Blueprint introduces {len(concepts)} distinct core concepts simultaneously.",
                        diagnosis="Introducing more than 4-5 novel concepts within a single short lesson saturates working memory limits.",
                        why_it_matters="Learners cannot form stable schemas when too many unfamiliar elements must be processed concurrently.",
                        evidence=[
                            CritiqueEvidence(
                                source="blueprint.content.concepts",
                                location="global",
                                observation=f"Total concepts count is {len(concepts)}.",
                                supporting_data={"concept_count": len(concepts)},
                            )
                        ],
                        severity=CritiqueSeverity.HIGH,
                        confidence=CritiqueConfidence.HIGH,
                        affected_locations=["global"],
                        improvement_direction="Decompose the lesson into multiple progressive chunks, introducing no more than 3-4 concepts per module.",
                    )
                )

        # 2. Split Attention & Block Density Overload on individual pages
        if context.composition is not None and context.composition.pages:
            overloaded_pages = []
            for p in context.composition.pages:
                total_blocks = sum(len(r.blocks) for r in p.regions.values())
                total_text_len = 0
                for r in p.regions.values():
                    for b in r.blocks:
                        total_text_len += len(str(b.raw_content or ""))

                # If single presentation slide has > 1,500 characters or > 6 concurrent blocks
                is_pres = "presentation" in context.target_format.lower()
                if (is_pres and total_text_len > 1500) or total_blocks > 7:
                    overloaded_pages.append((p.page_number, total_text_len, total_blocks))

            if overloaded_pages:
                pages_str = ", ".join(f"Page {p_num}" for p_num, _, _ in overloaded_pages)
                findings.append(
                    CritiqueFinding(
                        id="cog_split_attention_overload",
                        perspective=self.perspective,
                        title="Split-Attention and Working Memory Pressure",
                        observation=f"Pages exhibit extreme information concurrency: {pages_str}.",
                        diagnosis="Dense textual paragraphs, multiple competing visual blocks, and formulas compete for visual attention simultaneously.",
                        why_it_matters="Excessive visual competition forces constant context-switching, increasing extraneous cognitive load and reducing comprehension.",
                        evidence=[
                            CritiqueEvidence(
                                source="composition.pages",
                                location=pages_str,
                                observation="High concurrent block and character volume on single canvas.",
                                supporting_data={"overloaded_pages": overloaded_pages},
                            )
                        ],
                        severity=CritiqueSeverity.HIGH,
                        confidence=CritiqueConfidence.HIGH,
                        affected_locations=[f"Page {p_num}" for p_num, _, _ in overloaded_pages],
                        improvement_direction="Distribute complex concepts across multiple pages and isolate worked derivations from conceptual summaries.",
                    )
                )

        return findings
