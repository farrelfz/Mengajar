"""
Universal Knowledge Core — Artifact Differentiation Validator.

Phase 1C.1 Adversarial Hardening:
Distinguishes Knowledge Unit Overlap from Transformation Divergence.
High KnowledgeUnit overlap is explicitly VALID if semantic structures diverge.

Validates Worksheet inquiry flow (anti-quiz detection) and Presentation anti-handout constraints.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set, Any
from pydantic import BaseModel, Field

from app.intelligence.transformation.blueprints import (
    ArtifactBlueprint,
    HandoutBlueprint,
    LearningActivityType,
    PresentationBlueprint,
    ScientificDocumentBlueprint,
    WorksheetBlueprint,
)
from app.intelligence.transformation.intent import ArtifactType


class DifferentiationValidationResult(BaseModel):
    """Result of semantic cross-blueprint differentiation analysis."""
    is_differentiated: bool
    transformation_divergence_score: float = Field(ge=0.0, le=1.0)
    pairwise_unit_jaccard_scores: Dict[str, float] = Field(default_factory=dict)
    violations: List[str] = Field(default_factory=list)
    structural_metrics: Dict[str, Any] = Field(default_factory=dict)


class ArtifactDifferentiationValidator:
    """Validator measuring semantic structure divergence across the four artifact blueprints."""

    def validate(
        self,
        presentation_bp: PresentationBlueprint,
        handout_bp: HandoutBlueprint,
        worksheet_bp: WorksheetBlueprint,
        scientific_bp: ScientificDocumentBlueprint,
    ) -> DifferentiationValidationResult:
        violations: List[str] = []
        jaccard_scores: Dict[str, float] = {}

        blueprints: Dict[ArtifactType, ArtifactBlueprint] = {
            ArtifactType.PRESENTATION: presentation_bp,
            ArtifactType.HANDOUT: handout_bp,
            ArtifactType.WORKSHEET: worksheet_bp,
            ArtifactType.SCIENTIFIC_DOCUMENT: scientific_bp,
        }

        # 1. Pairwise Unit Selection Overlap (Explicitly valid even if high!)
        types = list(blueprints.keys())
        for i in range(len(types)):
            for j in range(i + 1, len(types)):
                t1, t2 = types[i], types[j]
                u1 = set(blueprints[t1].selected_knowledge_unit_ids)
                u2 = set(blueprints[t2].selected_knowledge_unit_ids)

                union = u1.union(u2)
                inter = u1.intersection(u2)
                jaccard = len(inter) / len(union) if union else 1.0
                jaccard_scores[f"{t1.value}_vs_{t2.value}"] = round(jaccard, 3)

        # 2. Structural Transformation Divergence Score
        # Checks element type, narrative role, cognitive framing, and inquiry presence
        structural_types_set = {
            type(presentation_bp.beats[0]).__name__ if presentation_bp.beats else "Empty",
            type(handout_bp.sections[0]).__name__ if handout_bp.sections else "Empty",
            type(worksheet_bp.activities[0]).__name__ if worksheet_bp.activities else "Empty",
            type(scientific_bp.arguments[0]).__name__ if scientific_bp.arguments else "Empty",
        }
        divergence_score = round(len(structural_types_set) / 4.0, 2)

        # 3. Rule: Presentation unit compression check (beats <= handout sections unless handout is small)
        p_beats = len(presentation_bp.beats)
        h_secs = len(handout_bp.sections)

        # 4. Presentation Anti-Handout Validation:
        # Detect presentation blueprints that collapse into uncompressed prose fragments
        if p_beats > 0:
            high_cog = [beat for beat in presentation_bp.beats if beat.cognitive_load_target > 0.70]
            if len(high_cog) / p_beats > 0.40:
                violations.append(
                    f"Presentation anti-handout violation: Excessive cognitive load density across beats ({len(high_cog)}/{p_beats} > 40%)."
                )

        # 5. Worksheet Inquiry Flow & Anti-Quiz Validation:
        if worksheet_bp.activities:
            # Rule 5A: Activities MUST withhold explanations
            non_withheld = [act for act in worksheet_bp.activities if not act.withhold_explanation]
            if non_withheld:
                violations.append(
                    f"Worksheet contains {len(non_withheld)} activities that spoil/reveal answers upfront."
                )

            # Rule 5B: Pattern-aware Anti-Quiz check
            act_types = set(act.activity_type for act in worksheet_bp.activities)
            if len(worksheet_bp.activities) >= 3 and len(act_types) == 1 and LearningActivityType.QUESTION in act_types:
                violations.append(
                    "Worksheet anti-pattern violation: Worksheet consists purely of a repetitive quiz sequence without inquiry variety."
                )

        # 6. Scientific Document Argument Discipline:
        if scientific_bp.arguments:
            no_role = [arg for arg in scientific_bp.arguments if not arg.argument_role]
            if no_role:
                violations.append(
                    f"Scientific document contains {len(no_role)} argument units lacking explicit argument roles."
                )

        metrics = {
            "presentation_beats": len(presentation_bp.beats),
            "handout_sections": len(handout_bp.sections),
            "worksheet_activities": len(worksheet_bp.activities),
            "scientific_arguments": len(scientific_bp.arguments),
            "structural_types_count": len(structural_types_set),
            "transformation_divergence_score": divergence_score,
            "unit_counts": {t.value: len(blueprints[t].selected_knowledge_unit_ids) for t in types},
        }

        is_differentiated = (len(violations) == 0) and (divergence_score >= 0.75)

        return DifferentiationValidationResult(
            is_differentiated=is_differentiated,
            transformation_divergence_score=divergence_score,
            pairwise_unit_jaccard_scores=jaccard_scores,
            violations=violations,
            structural_metrics=metrics,
        )
