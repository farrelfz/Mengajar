"""
Semantic Layout Appropriateness Validator.

Enforces the Visual Grammar Matrix: ensures layouts are pedagogically and
semantically aligned with what the slide is communicating, penalizing
semantically inappropriate pairings (e.g. PROCESS rendered as generic cards).
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from app.presentation.slide_architect import PlannedSlide
from app.presentation.visual_grammar_registry import VISUAL_GRAMMAR_MATRIX


class LayoutAlignmentResult(BaseModel):
    alignment_score: float
    status: str  # "PASS", "WARNING", "FAIL"
    total_slides: int
    matched_slides: int
    penalized_slides: int
    violations: list[dict[str, Any]] = Field(default_factory=list)


class SemanticLayoutValidator:
    """Evaluates Semantic-Layout appropriateness across planned slides."""

    GRAMMAR_MATRIX = VISUAL_GRAMMAR_MATRIX

    def evaluate_slide(self, slide: PlannedSlide) -> tuple[float, str | None]:
        """Evaluates a single slide against the Visual Grammar Matrix.
        Returns (score, violation_reason_if_any).
        """
        # Determine category
        role = slide.narrative_function.upper()
        if slide.visual_type in ("risk_matrix", "hazard_warning"):
            role = "SAFETY"
        elif slide.visual_type == "formula_visual":
            role = "FORMULA"
        elif slide.visual_type == "data_table":
            role = "OBSERVATION"
        elif slide.visual_type in ("step_process", "timeline_horizontal"):
            role = "PROCESS"

        rule = self.GRAMMAR_MATRIX.get(role)
        if not rule:
            return 1.0, None

        current_layout = slide.layout

        # Check if explicitly avoided
        if current_layout in rule["avoid"]:
            penalty = 0.40  # severe mismatch
            reason = f"Semantic mismatch on Slide {slide.slide_number} ('{slide.title}'): {role} communicates poorly using '{current_layout}'. {rule['reason']}"
            return penalty, reason

        # Check if preferred
        if current_layout in rule["preferred"]:
            return 1.0, None

        # Neutral fallback
        return 0.85, None

    def evaluate(self, slides: list[PlannedSlide]) -> LayoutAlignmentResult:
        """Evaluates all planned slides and produces an alignment report."""
        if not slides:
            return LayoutAlignmentResult(
                alignment_score=1.0,
                status="PASS",
                total_slides=0,
                matched_slides=0,
                penalized_slides=0,
                violations=[],
            )

        scores: list[float] = []
        violations: list[dict[str, Any]] = []

        for s in slides:
            score, reason = self.evaluate_slide(s)
            scores.append(score)
            if reason:
                violations.append({
                    "slide_number": s.slide_number,
                    "title": s.title,
                    "narrative_function": s.narrative_function,
                    "layout": s.layout,
                    "score": score,
                    "reason": reason,
                })

        mean_score = sum(scores) / len(scores)
        penalized_count = len(violations)
        matched_count = len(slides) - penalized_count

        status = "PASS"
        if mean_score < 0.80 or penalized_count > 3:
            status = "FAIL"
        elif penalized_count > 0:
            status = "WARNING"

        return LayoutAlignmentResult(
            alignment_score=round(mean_score, 3),
            status=status,
            total_slides=len(slides),
            matched_slides=matched_count,
            penalized_slides=penalized_count,
            violations=violations,
        )
