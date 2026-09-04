"""
Audience Suitability Critic: Evaluates alignment between target learner level and content complexity.
"""

from __future__ import annotations

from app.blueprints.content import AudienceLevel
from app.critic.base import BaseCritic
from app.critic.context import CritiqueContext
from app.critic.contracts import (
    CritiqueConfidence,
    CritiqueEvidence,
    CritiqueFinding,
    CritiquePerspective,
    CritiqueSeverity,
)


class AudienceCritic(BaseCritic):
    """Analyzes prerequisite assumptions, terminology difficulty, and audience suitability."""

    @property
    def critic_id(self) -> str:
        return "audience"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.AUDIENCE

    def can_critique(self, context: CritiqueContext) -> bool:
        return context.blueprint is not None

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        findings: list[CritiqueFinding] = []
        bp = context.blueprint
        if not bp or not bp.content or not bp.content.metadata:
            return findings

        audience = bp.content.metadata.audience
        is_high_school_or_lower = audience in [
            AudienceLevel.MIDDLE_SCHOOL,
            AudienceLevel.HIGH_SCHOOL,
            AudienceLevel.ELEMENTARY if hasattr(AudienceLevel, "ELEMENTARY") else AudienceLevel.MIDDLE_SCHOOL,
        ]

        if is_high_school_or_lower:
            # Check for overly dense advanced university jargon without scaffolding
            advanced_terms = ["lagrangian", "hamiltonian", "tensor", "eigenvalue", "homology", "stochastic differential"]
            matched_terms = []
            for c in bp.content.concepts:
                name_lower = c.name.lower()
                defn_lower = str(c.formal_definition or "").lower()
                for t in advanced_terms:
                    if t in name_lower or t in defn_lower:
                        matched_terms.append(t)

            if matched_terms:
                findings.append(
                    CritiqueFinding(
                        id="aud_advanced_prerequisite_gap",
                        perspective=self.perspective,
                        title="Advanced Prerequisite Gap for High School Audience",
                        observation=f"Material targets high school learners but assumes advanced tertiary concepts: {matched_terms}.",
                        diagnosis="Advanced graduate or university mathematics/physics concepts are introduced without preparatory scaffolding for high school students.",
                        why_it_matters="Premature exposure to highly abstract formalisms causes cognitive overload and alienation from the subject.",
                        evidence=[
                            CritiqueEvidence(
                                source="blueprint.content.concepts",
                                location="concepts",
                                observation=f"Found advanced terms {matched_terms} in high school material.",
                                supporting_data={"matched_terms": matched_terms, "target_audience": str(audience)},
                            )
                        ],
                        severity=CritiqueSeverity.HIGH,
                        confidence=CritiqueConfidence.HIGH,
                        affected_locations=["concepts"],
                        improvement_direction="Reframe the explanation using intuitive high school physical analogies or provide explicit foundational definitions.",
                    )
                )

        return findings
