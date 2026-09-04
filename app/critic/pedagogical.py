"""
Pedagogical Critic: Evaluates educational sequencing, prerequisite flow, worked-example placement, and cognitive scaffolding.
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
from app.director.contracts import LearningStageType


class PedagogicalCritic(BaseCritic):
    """Examines pedagogical effectiveness and explains why structural sequence flaws hinder student learning."""

    @property
    def critic_id(self) -> str:
        return "pedagogical"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.PEDAGOGICAL

    def can_critique(self, context: CritiqueContext) -> bool:
        return context.journey is not None or context.blueprint is not None

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        findings: list[CritiqueFinding] = []

        # Analyze LearningJourney if present
        if context.journey is not None and context.journey.stages:
            stages = context.journey.stages
            stage_types = [s.stage_type for s in stages]

            # Invariant 1: Worked example before concept formalization
            if LearningStageType.WORKED_EXAMPLE in stage_types and LearningStageType.CONCEPT_FORMALIZATION in stage_types:
                ex_idx = stage_types.index(LearningStageType.WORKED_EXAMPLE)
                concept_idx = stage_types.index(LearningStageType.CONCEPT_FORMALIZATION)
                if ex_idx < concept_idx:
                    findings.append(
                        CritiqueFinding(
                            id="ped_worked_example_precedes_concept",
                            perspective=self.perspective,
                            title="Worked Example Precedes Conceptual Formalization",
                            observation=f"Worked example at Stage {ex_idx + 1} appears before concept formalization at Stage {concept_idx + 1}.",
                            diagnosis="Learners are presented with mathematical or procedural problem-solving steps before establishing the underlying qualitative mental model.",
                            why_it_matters="Cognitive science shows that manipulating symbols without conceptual grounding causes rote memorization and high error rates.",
                            evidence=[
                                CritiqueEvidence(
                                    source="director_journey.stages",
                                    location=f"Stage {ex_idx + 1}",
                                    observation="Worked example is positioned before concept formalization.",
                                    supporting_data={"worked_example_index": ex_idx, "concept_index": concept_idx},
                                )
                            ],
                            severity=CritiqueSeverity.HIGH,
                            confidence=CritiqueConfidence.CERTAIN,
                            affected_locations=[f"Stage {ex_idx + 1}", f"Stage {concept_idx + 1}"],
                            improvement_direction="Reorder the learning journey so that concept formalization and intuition precede worked applications.",
                        )
                    )

            # Invariant 2: Independent practice before concept introduction
            practice_types = [LearningStageType.INDEPENDENT_PRACTICE, LearningStageType.GUIDED_PRACTICE]
            for p_type in practice_types:
                if p_type in stage_types and LearningStageType.CONCEPT_FORMALIZATION in stage_types:
                    p_idx = stage_types.index(p_type)
                    concept_idx = stage_types.index(LearningStageType.CONCEPT_FORMALIZATION)
                    if p_idx < concept_idx:
                        findings.append(
                            CritiqueFinding(
                                id="ped_practice_precedes_concept",
                                perspective=self.perspective,
                                title="Practice Exercise Precedes Instruction",
                                observation=f"Practice stage '{p_type.value}' at Stage {p_idx + 1} precedes concept introduction at Stage {concept_idx + 1}.",
                                diagnosis="Students are expected to apply knowledge independently without receiving foundational instruction.",
                                why_it_matters="Premature testing without instruction leads to frustration, high failure rates, and misconceptions.",
                                evidence=[
                                    CritiqueEvidence(
                                        source="director_journey.stages",
                                        location=f"Stage {p_idx + 1}",
                                        observation="Practice stage appears prior to foundational theory.",
                                        supporting_data={"practice_index": p_idx, "concept_index": concept_idx},
                                    )
                                ],
                                severity=CritiqueSeverity.HIGH,
                                confidence=CritiqueConfidence.CERTAIN,
                                affected_locations=[f"Stage {p_idx + 1}"],
                                improvement_direction="Ensure structured concept explanation and worked examples precede independent student practice.",
                            )
                        )

            # Invariant 3: Missing prior-knowledge activation or hook
            if len(stage_types) >= 3 and stage_types[0] in [LearningStageType.CONCEPT_FORMALIZATION, LearningStageType.INDEPENDENT_PRACTICE]:
                findings.append(
                    CritiqueFinding(
                        id="ped_abrupt_opening",
                        perspective=self.perspective,
                        title="Abrupt Instructional Opening Without Cognitive Hook",
                        observation=f"Instruction begins immediately with abstract '{stage_types[0].value}' without an introductory phenomenon or hook.",
                        diagnosis="The material skips motivation and prior-knowledge activation, demanding immediate abstract cognitive commitment.",
                        why_it_matters="Engaging initial hooks anchor new material into existing learner schemata and boost retention.",
                        evidence=[
                            CritiqueEvidence(
                                source="director_journey.stages",
                                location="Stage 1",
                                observation=f"First stage is '{stage_types[0].value}'.",
                                supporting_data={"first_stage": stage_types[0].value},
                            )
                        ],
                        severity=CritiqueSeverity.MEDIUM,
                        confidence=CritiqueConfidence.HIGH,
                        affected_locations=["Stage 1"],
                        improvement_direction="Prepend an introductory phenomenon, real-world context, or motivating question to activate curiosity.",
                    )
                )

        return findings
