"""
Structural Critic: Analyzes document structure, dependency ordering, and completeness.
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


class StructuralCritic(BaseCritic):
    """Examines structural organization, dependency chains, and structural gaps."""

    @property
    def critic_id(self) -> str:
        return "structural"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.STRUCTURAL

    def can_critique(self, context: CritiqueContext) -> bool:
        return context.blueprint is not None or context.composition is not None

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        findings: list[CritiqueFinding] = []

        # 1. Check for empty composition structure
        if context.composition is not None and not context.composition.pages:
            findings.append(
                CritiqueFinding(
                    id="struct_empty_doc",
                    perspective=self.perspective,
                    title="Empty Document Composition Structure",
                    observation="The document composition contains zero allocated pages.",
                    diagnosis="No physical pages or content regions exist to deliver instructional material.",
                    why_it_matters="A document with no pages cannot be rendered or consumed by learners.",
                    evidence=[
                        CritiqueEvidence(
                            source="composition",
                            location="global",
                            observation="DocumentComposition.pages is empty.",
                            supporting_data={"page_count": 0},
                        )
                    ],
                    severity=CritiqueSeverity.CRITICAL,
                    confidence=CritiqueConfidence.CERTAIN,
                    affected_locations=["global"],
                    improvement_direction="Generate valid page layouts with appropriate region templates in the Composition Engine.",
                )
            )
            return findings

        # 2. Check for missing conceptual grounding before procedural steps in blueprint
        if context.blueprint is not None and context.blueprint.content:
            content = context.blueprint.content
            if not content.concepts and content.objectives:
                findings.append(
                    CritiqueFinding(
                        id="struct_missing_concept_grounding",
                        perspective=self.perspective,
                        title="Missing Conceptual Grounding Layer",
                        observation="Learning objectives are declared without any formal concept definitions in Level A blueprint.",
                        diagnosis="The document jumps into instructions or examples without structural anchoring of foundational concepts.",
                        why_it_matters="Learners cannot anchor procedural tasks without explicit conceptual models.",
                        evidence=[
                            CritiqueEvidence(
                                source="blueprint.content",
                                location="Level A",
                                observation=f"Found {len(content.objectives)} objectives but 0 concepts.",
                                supporting_data={"objectives_count": len(content.objectives), "concepts_count": 0},
                            )
                        ],
                        severity=CritiqueSeverity.HIGH,
                        confidence=CritiqueConfidence.HIGH,
                        affected_locations=["blueprint_level_a"],
                        improvement_direction="Extract and formalize foundational concept definitions before constructing learning exercises.",
                    )
                )

        # 3. Check for empty regions inside pages
        if context.composition is not None:
            empty_pages = []
            for p in context.composition.pages:
                if not p.regions or all(not r.blocks for r in p.regions.values()):
                    empty_pages.append(f"Page {p.page_number}")

            if empty_pages:
                findings.append(
                    CritiqueFinding(
                        id="struct_empty_pages_detected",
                        perspective=self.perspective,
                        title="Unpopulated Document Pages",
                        observation=f"Pages contain zero populated content regions: {', '.join(empty_pages)}.",
                        diagnosis="Layout regions were allocated by the composition engine but never populated with content blocks.",
                        why_it_matters="Blank pages disrupt reading rhythm and create a perception of broken formatting.",
                        evidence=[
                            CritiqueEvidence(
                                source="composition.pages",
                                location=", ".join(empty_pages),
                                observation="PageRegion blocks list is empty.",
                                supporting_data={"empty_pages": empty_pages},
                            )
                        ],
                        severity=CritiqueSeverity.HIGH,
                        confidence=CritiqueConfidence.CERTAIN,
                        affected_locations=empty_pages,
                        improvement_direction="Prune unpopulated page allocations or assign fallback visual components.",
                    )
                )

        return findings
