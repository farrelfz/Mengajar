"""
Pedagogical Alignment & Sequence Evaluator.

Checks stage transitions, prerequisite-to-formalization ordering,
worked-example placement, practice alignment, and cognitive scaffolding.
"""

from __future__ import annotations

from app.blueprints.contracts import SemanticMaterialBlueprint
from app.director.contracts import LearningJourney, LearningStageType
from app.quality.contracts import (
    QualityDimension,
    QualityFinding,
    QualityMetric,
    QualitySeverity,
)


class PedagogicalEvaluator:
    """Evaluates the cognitive structure and sequencing of the learning journey."""

    @staticmethod
    def evaluate(
        journey: LearningJourney | None,
        blueprint: SemanticMaterialBlueprint | None = None,
    ) -> tuple[list[QualityMetric], list[QualityFinding]]:
        metrics: list[QualityMetric] = []
        findings: list[QualityFinding] = []

        if not journey or not journey.stages:
            return metrics, findings

        stage_types = [s.stage_type for s in journey.stages]
        score = 1.0

        # Invariant 1: Worked example should not precede concept definition / formalization
        if LearningStageType.WORKED_EXAMPLE in stage_types and LearningStageType.CONCEPT_FORMALIZATION in stage_types:
            first_worked_ex = stage_types.index(LearningStageType.WORKED_EXAMPLE)
            first_concept = stage_types.index(LearningStageType.CONCEPT_FORMALIZATION)
            if first_worked_ex < first_concept:
                score -= 0.4
                findings.append(
                    QualityFinding(
                        dimension=QualityDimension.PEDAGOGICAL_ALIGNMENT,
                        severity=QualitySeverity.ERROR,
                        finding="Worked example appears before concept formalization.",
                        evidence={"worked_example_index": first_worked_ex, "formalization_index": first_concept},
                        affected_section=f"Stage {first_worked_ex + 1}",
                        score_impact=-0.4,
                        recommendation="Reorder stages so that concept formalization precedes procedural application.",
                    )
                )

        # Invariant 2: Independent Practice should not precede concept definition
        practice_types = [LearningStageType.INDEPENDENT_PRACTICE, LearningStageType.GUIDED_PRACTICE]
        has_practice = any(pt in stage_types for pt in practice_types)
        if has_practice and LearningStageType.CONCEPT_FORMALIZATION in stage_types:
            first_practice = min(stage_types.index(pt) for pt in practice_types if pt in stage_types)
            first_concept = stage_types.index(LearningStageType.CONCEPT_FORMALIZATION)
            if first_practice < first_concept:
                score -= 0.35
                findings.append(
                    QualityFinding(
                        dimension=QualityDimension.PEDAGOGICAL_ALIGNMENT,
                        severity=QualitySeverity.ERROR,
                        finding="Practice stage appears before concept formalization.",
                        evidence={"practice_index": first_practice, "formalization_index": first_concept},
                        affected_section=f"Stage {first_practice + 1}",
                        score_impact=-0.35,
                        recommendation="Ensure foundational concepts are formalized before student practice.",
                    )
                )

        # Invariant 3: Advanced Challenge should not precede concept formalization
        if LearningStageType.CHALLENGE in stage_types and LearningStageType.CONCEPT_FORMALIZATION in stage_types:
            first_challenge = stage_types.index(LearningStageType.CHALLENGE)
            first_concept = stage_types.index(LearningStageType.CONCEPT_FORMALIZATION)
            if first_challenge < first_concept:
                score -= 0.3
                findings.append(
                    QualityFinding(
                        dimension=QualityDimension.PEDAGOGICAL_ALIGNMENT,
                        severity=QualitySeverity.WARNING,
                        finding="Advanced challenge stage appears before foundational concept formalization.",
                        evidence={"challenge_index": first_challenge, "formalization_index": first_concept},
                        affected_section=f"Stage {first_challenge + 1}",
                        score_impact=-0.3,
                        recommendation="Place advanced challenges after concept introduction and worked examples.",
                    )
                )

        # Invariant 4: Hook or intuition should ideally initiate introductory materials
        if len(stage_types) >= 3 and stage_types[0] not in [
            LearningStageType.HOOK,
            LearningStageType.PHENOMENON if hasattr(LearningStageType, "PHENOMENON") else LearningStageType.HOOK,
            LearningStageType.SURFACE_INTUITION,
            LearningStageType.CONTEXT_SETTING if hasattr(LearningStageType, "CONTEXT_SETTING") else LearningStageType.ACTIVATE_PRIOR_KNOWLEDGE,
            LearningStageType.CONTEXT,
            LearningStageType.PROBLEM_STATEMENT,
        ]:
            score -= 0.15
            findings.append(
                QualityFinding(
                    dimension=QualityDimension.PEDAGOGICAL_ALIGNMENT,
                    severity=QualitySeverity.WARNING,
                    finding=f"Learning journey begins abruptly with '{stage_types[0].value}' without prior cognitive hook.",
                    evidence={"first_stage": stage_types[0].value},
                    affected_section="Stage 1",
                    score_impact=-0.15,
                    recommendation="Prepend a phenomenon or cognitive hook to build learner interest.",
                )
            )

        metrics.append(
            QualityMetric(
                name="pedagogical_sequencing_integrity",
                dimension=QualityDimension.PEDAGOGICAL_ALIGNMENT,
                score=max(0.0, round(score, 3)),
                weight=1.5,
                raw_value=[s.value for s in stage_types],
                details={"total_stages": len(stage_types)},
            )
        )

        return metrics, findings
