"""
Scientific Rigor Critic: Evaluates claim-evidence alignment, correlation vs causation, and variable ambiguity.
"""

from __future__ import annotations

from app.blueprints.content import KnowledgeDomain
from app.critic.base import BaseCritic
from app.critic.context import CritiqueContext
from app.critic.contracts import (
    CritiqueConfidence,
    CritiqueEvidence,
    CritiqueFinding,
    CritiquePerspective,
    CritiqueSeverity,
)


class ScientificRigorCritic(BaseCritic):
    """Examines scientific rigor, claim-evidence alignment, and causal reasoning validity."""

    @property
    def critic_id(self) -> str:
        return "scientific_rigor"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.SCIENTIFIC_RIGOR

    def can_critique(self, context: CritiqueContext) -> bool:
        # Check domain relevance (physics, science, research, mathematics)
        if context.blueprint and context.blueprint.content and context.blueprint.content.metadata:
            dom = context.blueprint.content.metadata.domain
            if dom in [
                KnowledgeDomain.PHYSICS,
                KnowledgeDomain.GENERAL_SCIENCE,
                KnowledgeDomain.RESEARCH_METHODOLOGY,
                KnowledgeDomain.MATHEMATICS,
                KnowledgeDomain.DATA_LITERACY if hasattr(KnowledgeDomain, "DATA_LITERACY") else KnowledgeDomain.MATHEMATICS,
            ]:
                return True
        return context.document_genre in ["scientific", "research", "experiment"]

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        findings: list[CritiqueFinding] = []
        bp = context.blueprint
        if not bp or not bp.content:
            return findings

        # Check facts and text for unsupported causal claims or correlation-causation leap
        facts = bp.content.facts
        for idx, fact in enumerate(facts):
            fact_text = str(fact.statement if hasattr(fact, "statement") else fact).lower()
            if ("correlated" in fact_text or "associated with" in fact_text) and ("proves that" in fact_text or "causes" in fact_text):
                findings.append(
                    CritiqueFinding(
                        id=f"sci_correlation_as_causation_{idx}",
                        perspective=self.perspective,
                        title="Correlation Inappropriately Stated as Direct Causation",
                        observation=f"Fact statement merges correlation with causal certainty: '{fact_text[:80]}...'",
                        diagnosis="The explanation claims definitive causation based solely on correlational or observational association.",
                        why_it_matters="Conflating correlation with causation is a foundational scientific reasoning error that misleads students.",
                        evidence=[
                            CritiqueEvidence(
                                source="blueprint.content.facts",
                                location=f"Fact {idx + 1}",
                                observation="Claim contains both associative terminology and definitive causal conclusion.",
                                supporting_data={"statement": fact_text},
                            )
                        ],
                        severity=CritiqueSeverity.HIGH,
                        confidence=CritiqueConfidence.HIGH,
                        affected_locations=[f"Fact {idx + 1}"],
                        improvement_direction="Clarify that statistical correlation indicates an association and requires controlled experimentation to establish causation.",
                    )
                )

        return findings
