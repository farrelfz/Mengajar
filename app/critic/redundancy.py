"""
Redundancy Critic: Analyzes conceptual repetition, unproductive rephrasing, and unvaried examples.
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


class RedundancyCritic(BaseCritic):
    """Examines conceptual redundancy and unproductive repetition across pages."""

    @property
    def critic_id(self) -> str:
        return "redundancy"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.REDUNDANCY

    def can_critique(self, context: CritiqueContext) -> bool:
        return context.composition is not None

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        findings: list[CritiqueFinding] = []
        comp = context.composition
        if not comp or not comp.pages:
            return findings

        # Check for substantial verbatim or near-verbatim duplicate blocks across distinct pages
        page_texts: dict[int, list[str]] = {}
        for p in comp.pages:
            spans = []
            for r in p.regions.values():
                for b in r.blocks:
                    content = str(b.raw_content or "").strip()
                    if len(content) > 50:
                        spans.append(content)
            page_texts[p.page_number] = spans

        seen_spans: dict[str, int] = {}
        for p_num, spans in page_texts.items():
            for s in spans:
                if s in seen_spans:
                    orig_page = seen_spans[s]
                    findings.append(
                        CritiqueFinding(
                            id=f"red_duplicate_content_p{orig_page}_p{p_num}",
                            perspective=self.perspective,
                            title="Substantial Conceptual Repetition Across Pages",
                            observation=f"Page {p_num} contains identical substantive text previously presented on Page {orig_page}.",
                            diagnosis="The same conceptual paragraph is repeated verbatim on multiple pages without introducing a higher level of abstraction or new representation.",
                            why_it_matters="Redundant content wastes document real estate and causes reader disengagement.",
                            evidence=[
                                CritiqueEvidence(
                                    source="composition.pages",
                                    location=f"Page {p_num}",
                                    observation=f"Identical text span matches Page {orig_page}.",
                                    supporting_data={"source_page": orig_page, "duplicate_page": p_num, "span_preview": s[:60]},
                                )
                            ],
                            severity=CritiqueSeverity.MEDIUM,
                            confidence=CritiqueConfidence.CERTAIN,
                            affected_locations=[f"Page {orig_page}", f"Page {p_num}"],
                            improvement_direction="Condense the subsequent occurrence into a brief recall reference or replace it with a complementary visualization.",
                        )
                    )
                else:
                    seen_spans[s] = p_num

        return findings
