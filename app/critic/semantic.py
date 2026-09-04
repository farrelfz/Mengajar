"""
Semantic Critic: Evaluates concept consistency, definition completeness, and semantic dependency integrity.
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


class SemanticCritic(BaseCritic):
    """Analyzes semantic integrity, conceptual definitions, and alignment between goals and content."""

    @property
    def critic_id(self) -> str:
        return "semantic"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.SEMANTIC

    def can_critique(self, context: CritiqueContext) -> bool:
        return context.blueprint is not None

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        findings: list[CritiqueFinding] = []
        bp = context.blueprint
        if not bp or not bp.content:
            return findings

        content = bp.content
        concepts = content.concepts
        objectives = content.objectives

        # 1. Uncovered Objectives / Undefined Target Concepts
        concept_names = {c.name.lower().strip() for c in concepts if c.name}
        uncovered = []
        for obj in objectives:
            if obj.target_concept and obj.target_concept.lower().strip() not in concept_names:
                uncovered.append(obj)

        if uncovered:
            target_names = [o.target_concept for o in uncovered]
            findings.append(
                CritiqueFinding(
                    id="sem_uncovered_objectives",
                    perspective=self.perspective,
                    title="Learning Objectives Target Undefined Concepts",
                    observation=f"Objectives target concepts that lack formal definitions: {target_names}.",
                    diagnosis="A learning objective expects the student to master a concept that is never formally defined in the knowledge blueprint.",
                    why_it_matters="Students will be assessed on concepts that the material never formalizes.",
                    evidence=[
                        CritiqueEvidence(
                            source="blueprint.content.objectives",
                            location="objectives",
                            observation=f"{len(uncovered)} objectives have unmatched target_concept values.",
                            supporting_data={"uncovered_concepts": target_names},
                        )
                    ],
                    severity=CritiqueSeverity.HIGH,
                    confidence=CritiqueConfidence.HIGH,
                    affected_locations=["objectives"],
                    improvement_direction="Define explicit ConceptDefinition entries for every concept referenced in learning objectives.",
                )
            )

        # 2. Trivial or Stub Concept Definitions
        trivial_concepts = [c.name for c in concepts if len(str(c.formal_definition or "").strip()) < 10]
        if trivial_concepts:
            findings.append(
                CritiqueFinding(
                    id="sem_trivial_concept_definitions",
                    perspective=self.perspective,
                    title="Shallow Concept Definitions",
                    observation=f"Concepts have stub or trivially short definitions: {trivial_concepts}.",
                    diagnosis="Concept definitions lack mathematical, physical, or contextual articulation beyond short keywords.",
                    why_it_matters="Trivial definitions fail to impart authentic conceptual understanding or support higher-order inquiry.",
                    evidence=[
                        CritiqueEvidence(
                            source="blueprint.content.concepts",
                            location="concepts",
                            observation=f"{len(trivial_concepts)} concepts have definition length < 10 characters.",
                            supporting_data={"trivial_concepts": trivial_concepts},
                        )
                    ],
                    severity=CritiqueSeverity.MEDIUM,
                    confidence=CritiqueConfidence.HIGH,
                    affected_locations=["concepts"],
                    improvement_direction="Expand concept definitions to include intuitive explanations and formal relationships.",
                )
            )

        return findings
