"""
Universal Document Intelligence System V5 — Progression-Aware Repetition Analyzer.

Phase 3A.1: Disentangles intentional progressive sequence continuity from layout monotony.
Protects conceptual build-ups and step-by-step derivations from false-positive repetition penalties.
"""

from __future__ import annotations

import difflib
import re
from typing import Dict, List, Tuple
from pydantic import BaseModel, ConfigDict


class RepetitionEvaluationResult(BaseModel):
    """Result of analyzing visual and semantic continuity between two pages/slides."""
    model_config = ConfigDict(frozen=True)

    page_pair: Tuple[int, int]
    visual_similarity: float
    semantic_information_gain: float
    is_progressive_reveal: bool
    is_intentional_continuity: bool
    is_layout_monotony: bool
    penalty_score: float
    rationale: str


class ProgressionAwareRepetitionAnalyzer:
    """Analyzes visual similarity in combination with semantic information gain."""

    @classmethod
    def evaluate_pair(
        cls,
        page_a: int,
        page_b: int,
        text_a: str,
        text_b: str,
        visual_similarity: float,
        is_marked_progressive: bool = False,
    ) -> RepetitionEvaluationResult:
        # 1. Clean and tokenize texts
        words_a = set(re.findall(r"\b\w{3,}\b", text_a.lower()))
        words_b = set(re.findall(r"\b\w{3,}\b", text_b.lower()))

        # New words introduced in page B
        new_words = words_b - words_a
        info_gain = len(new_words) / max(1, len(words_b))

        # Check for superset / progressive inclusion (text B includes majority of text A)
        matcher = difflib.SequenceMatcher(None, text_a.lower(), text_b.lower())
        char_sim = matcher.ratio()
        
        # Progressive reveal heuristics:
        # High visual similarity + new substantive content added + text B is longer or marked
        is_prog = is_marked_progressive or (
            visual_similarity >= 0.85
            and (len(text_b) >= len(text_a))
            and (info_gain >= 0.20 or (len(new_words) >= 4 and char_sim >= 0.60))
        )

        is_intentional = False
        is_monotony = False
        penalty = 0.0
        rationale = ""

        if visual_similarity >= 0.88:
            if is_prog or info_gain >= 0.30:
                is_intentional = True
                is_monotony = False
                penalty = 0.0
                rationale = (
                    f"Pages {page_a}->{page_b}: Intentional progressive continuity. "
                    f"Visual similarity ({visual_similarity:.2f}) supported by information gain ({info_gain:.2f})."
                )
            else:
                is_intentional = False
                is_monotony = True
                penalty = round(visual_similarity * (1.0 - info_gain) * 0.5, 2)
                rationale = (
                    f"Pages {page_a}->{page_b}: Unjustified layout monotony. "
                    f"High visual similarity ({visual_similarity:.2f}) with low information gain ({info_gain:.2f})."
                )
        else:
            rationale = f"Pages {page_a}->{page_b}: Distinct layouts (similarity {visual_similarity:.2f})."

        return RepetitionEvaluationResult(
            page_pair=(page_a, page_b),
            visual_similarity=round(visual_similarity, 3),
            semantic_information_gain=round(info_gain, 3),
            is_progressive_reveal=is_prog,
            is_intentional_continuity=is_intentional,
            is_layout_monotony=is_monotony,
            penalty_score=penalty,
            rationale=rationale,
        )
