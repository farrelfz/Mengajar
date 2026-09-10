"""
Presentation Narrative & Architecture Evaluator.

Evaluates narrative progression, pedagogical flow, cognitive load distribution,
concept fragmentation, concept compression, and slide purpose redundancy.
"""

from __future__ import annotations

import difflib
import re
from typing import Any
from pydantic import BaseModel, Field

from app.presentation.slide_architect import PlannedSlide, SlidePlan


class NarrativeTransitionGraph:
    """Directed heuristic graph of natural, pedagogically sound narrative transitions."""

    COMPATIBILITY: dict[str, list[str]] = {
        "HOOK": ["QUESTION", "CONTEXT", "PROBLEM", "CONCEPT_INTRODUCTION"],
        "QUESTION": ["CONCEPT_INTRODUCTION", "INVESTIGATION", "MECHANISM", "EXPERIMENT", "CONTEXT"],
        "CONTEXT": ["QUESTION", "CONCEPT_INTRODUCTION", "PROBLEM", "MECHANISM"],
        "PROBLEM": ["QUESTION", "CONCEPT_INTRODUCTION", "INVESTIGATION", "MECHANISM"],
        "CONCEPT_INTRODUCTION": ["CONCEPT_DEEPENING", "MECHANISM", "COMPARISON", "PROCESS", "EXPERIMENT", "QUESTION"],
        "CONCEPT_DEEPENING": ["MECHANISM", "COMPARISON", "APPLICATION", "QUESTION"],
        "MECHANISM": ["APPLICATION", "EXPERIMENT", "COMPARISON", "CAUSE_EFFECT", "OBSERVATION", "CONCEPT_INTRODUCTION"],
        "CAUSE_EFFECT": ["MECHANISM", "APPLICATION", "OBSERVATION", "REFLECTION"],
        "COMPARISON": ["MECHANISM", "APPLICATION", "SYNTHESIS", "ANALYSIS", "CONCEPT_INTRODUCTION"],
        "PROCESS": ["EXPERIMENT", "OBSERVATION", "APPLICATION", "STEP_FLOW"],
        "EXPERIMENT": ["OBSERVATION", "ANALYSIS", "MECHANISM", "PROCESS"],
        "OBSERVATION": ["ANALYSIS", "REFLECTION", "SYNTHESIS", "DATA"],
        "ANALYSIS": ["REFLECTION", "SYNTHESIS", "CONCLUSION", "OBSERVATION"],
        "REFLECTION": ["SYNTHESIS", "CONCLUSION", "QUESTION", "CALL_TO_ACTION"],
        "MISCONCEPTION": ["CONCEPT_INTRODUCTION", "MECHANISM", "REFLECTION"],
        "SYNTHESIS": ["CONCLUSION", "CALL_TO_ACTION", "REFLECTION"],
        "CONCLUSION": ["CALL_TO_ACTION", "SYNTHESIS"],
        "CALL_TO_ACTION": ["CONCLUSION"],
    }

    def evaluate_transition(self, from_func: str, to_func: str) -> tuple[float, str]:
        """Score compatibility between consecutive narrative functions (0.0 to 1.0)."""
        f_from = from_func.upper()
        f_to = to_func.upper()

        if f_from == f_to:
            return 0.75, f"Repetitive narrative state: {f_from} -> {f_to}"

        allowed = self.COMPATIBILITY.get(f_from, [])
        if f_to in allowed:
            return 1.0, f"High narrative compatibility: {f_from} -> {f_to}"

        # Incoherent jump: CONCLUSION -> CONCEPT_INTRODUCTION
        if f_from == "CONCLUSION" and f_to in ("CONCEPT_INTRODUCTION", "MECHANISM", "PROBLEM"):
            return 0.20, f"Incoherent regression: {f_from} -> {f_to} (reintroducing core concepts after conclusion)"

        # Partial compatibility for related states
        return 0.60, f"Moderate narrative compatibility: {f_from} -> {f_to}"

    def detect_monotonous_sequences(self, slides: list[PlannedSlide], max_streak: int = 4) -> list[dict[str, Any]]:
        """Detect long monotonous streaks of the identical narrative function (>= 5 slides)."""
        issues: list[dict[str, Any]] = []
        if not slides:
            return issues

        current_func = slides[0].narrative_function
        streak_indices = [slides[0].slide_number]

        for s in slides[1:]:
            if s.narrative_function == current_func:
                streak_indices.append(s.slide_number)
            else:
                if len(streak_indices) > max_streak:
                    issues.append({
                        "narrative_function": current_func,
                        "streak_length": len(streak_indices),
                        "slide_numbers": list(streak_indices),
                        "message": f"Monotonous sequence: {len(streak_indices)} consecutive '{current_func}' slides",
                    })
                current_func = s.narrative_function
                streak_indices = [s.slide_number]

        if len(streak_indices) > max_streak:
            issues.append({
                "narrative_function": current_func,
                "streak_length": len(streak_indices),
                "slide_numbers": list(streak_indices),
                "message": f"Monotonous sequence: {len(streak_indices)} consecutive '{current_func}' slides",
            })

        return issues


class CognitiveLoadValidator:
    """Validates cognitive load distribution across the presentation deck."""

    def __init__(self, max_high_streak: int = 2) -> None:
        self.max_high_streak = max_high_streak

    def evaluate(self, slides: list[PlannedSlide]) -> tuple[float, list[dict[str, Any]]]:
        """Returns (cognitive_load_balance_score, issues)."""
        if not slides:
            return 1.0, []

        issues: list[dict[str, Any]] = []
        high_streak = 0
        streak_slides = []
        penalties = 0

        for s in slides:
            level = (s.cognitive_load.level if hasattr(s.cognitive_load, "level") else "medium").lower()
            if level == "high":
                high_streak += 1
                streak_slides.append(s.slide_number)
            else:
                if high_streak > self.max_high_streak:
                    penalties += (high_streak - self.max_high_streak)
                    issues.append({
                        "type": "HIGH_COGNITIVE_LOAD_STREAK",
                        "streak_length": high_streak,
                        "slide_numbers": list(streak_slides),
                        "message": f"High cognitive load streak of {high_streak} slides ({streak_slides}) exceeds recommended max {self.max_high_streak}",
                    })
                high_streak = 0
                streak_slides = []

        if high_streak > self.max_high_streak:
            penalties += (high_streak - self.max_high_streak)
            issues.append({
                "type": "HIGH_COGNITIVE_LOAD_STREAK",
                "streak_length": high_streak,
                "slide_numbers": list(streak_slides),
                "message": f"High cognitive load streak of {high_streak} slides ({streak_slides}) exceeds recommended max {self.max_high_streak}",
            })

        score = max(0.0, min(1.0, 1.0 - (penalties * 0.15)))
        return round(score, 3), issues


class ConceptFragmentationAnalyzer:
    """Detects unnecessary splitting of a single simple concept across consecutive slides."""

    def analyze(self, slides: list[PlannedSlide]) -> tuple[float, list[dict[str, Any]]]:
        """Returns (fragmentation_score, issues). Lower score is better (0.0 = no fragmentation)."""
        if len(slides) < 3:
            return 0.0, []

        issues: list[dict[str, Any]] = []
        fragmentation_count = 0

        # Group runs of slides with identical primary concept
        i = 0
        while i < len(slides) - 2:
            s1, s2, s3 = slides[i], slides[i+1], slides[i+2]
            c1 = s1.primary_concept.strip().lower()
            c2 = s2.primary_concept.strip().lower()
            c3 = s3.primary_concept.strip().lower()

            if c1 and c1 == c2 == c3:
                # Check text content overlap / thinness
                t1 = " ".join(b.content for b in s1.key_blocks)
                t2 = " ".join(b.content for b in s2.key_blocks)
                t3 = " ".join(b.content for b in s3.key_blocks)
                
                # If all three slides are very short (< 40 words each), it's likely over-fragmented
                w1, w2, w3 = len(t1.split()), len(t2.split()), len(t3.split())
                if w1 < 35 and w2 < 35 and w3 < 35:
                    fragmentation_count += 1
                    issues.append({
                        "type": "CONCEPT_FRAGMENTATION",
                        "concept": s1.primary_concept,
                        "slides": [s1.slide_number, s2.slide_number, s3.slide_number],
                        "recommendation": f"Merge thin slides {[s1.slide_number, s2.slide_number, s3.slide_number]} for '{s1.primary_concept}'",
                    })
                    i += 2
            i += 1

        score = min(1.0, fragmentation_count * 0.15)
        return round(score, 3), issues


class ConceptCompressionAnalyzer:
    """Detects excessive cramming of multiple independent concepts/formulas onto a single slide."""

    def analyze(self, slides: list[PlannedSlide]) -> tuple[float, list[dict[str, Any]]]:
        """Returns (compression_score, issues). Lower score is better (0.0 = balanced)."""
        issues: list[dict[str, Any]] = []
        compressed_slides = 0

        for s in slides:
            num_blocks = len(s.key_blocks)
            total_words = sum(len(b.content.split()) for b in s.key_blocks)
            formulas = sum(1 for b in s.key_blocks if b.type.value == "formula")
            
            # Severe compression: >= 4 formulas or >= 3 formulas with high word count or > 240 words on non-table slide
            is_overcrowded = (formulas >= 4) or (formulas >= 3 and total_words > 80) or (total_words > 240 and s.layout != "data_table") or (num_blocks >= 7)
            if is_overcrowded:
                compressed_slides += 1
                issues.append({
                    "slide_number": s.slide_number,
                    "title": s.title,
                    "total_words": total_words,
                    "formula_count": formulas,
                    "recommendation": f"Split dense slide {s.slide_number} ('{s.title}') into concept and mechanism slides",
                })

        score = min(1.0, (compressed_slides / max(1, len(slides))) * 2.0)
        return round(score, 3), issues


class SlidePurposeRedundancyAnalyzer:
    """Detects consecutive slides that duplicate the exact same instructional purpose."""

    def analyze(self, slides: list[PlannedSlide]) -> tuple[float, list[dict[str, Any]]]:
        """Returns (redundancy_score, issues). Lower score is better."""
        if len(slides) < 2:
            return 0.0, []

        issues: list[dict[str, Any]] = []
        redundant_pairs = 0

        for i in range(len(slides) - 1):
            s1, s2 = slides[i], slides[i+1]
            same_concept = (s1.primary_concept and s1.primary_concept.lower() == s2.primary_concept.lower())
            same_narrative = (s1.narrative_function == s2.narrative_function)
            same_pedagogy = (s1.pedagogical_function == s2.pedagogical_function)

            # Measure textual similarity of purpose & titles
            p1 = f"{s1.title} {s1.purpose}"
            p2 = f"{s2.title} {s2.purpose}"
            sim = difflib.SequenceMatcher(None, p1, p2).ratio()

            if same_concept and same_narrative and same_pedagogy and sim > 0.70:
                redundant_pairs += 1
                issues.append({
                    "slide_pair": [s1.slide_number, s2.slide_number],
                    "concept": s1.primary_concept,
                    "similarity": round(sim, 2),
                    "reason": f"Slides {s1.slide_number} & {s2.slide_number} share identical purpose, function, and {sim*100:.0f}% lexical similarity",
                })

        score = min(1.0, redundant_pairs / max(1, len(slides)))
        return round(score, 3), issues


class InformationGainAnalyzer:
    """Measures new concept and relationship delta between consecutive slides."""

    def analyze(self, slides: list[PlannedSlide]) -> tuple[float, list[dict[str, Any]]]:
        """Returns (mean_information_gain_score, issues). Score 0.0 to 1.0 (higher is better)."""
        if len(slides) < 2:
            return 1.0, []

        gains: list[float] = []
        issues: list[dict[str, Any]] = []

        for i in range(len(slides) - 1):
            s1, s2 = slides[i], slides[i+1]
            
            # Token sets
            tokens1 = set(re.findall(r"\w+", " ".join(b.content for b in s1.key_blocks).lower()))
            tokens2 = set(re.findall(r"\w+", " ".join(b.content for b in s2.key_blocks).lower()))

            if not tokens2:
                # Transition / synthesis slide
                gain = 0.5
            else:
                new_tokens = tokens2 - tokens1
                gain = len(new_tokens) / max(1, len(tokens2))

            gains.append(gain)
            if gain < 0.12 and s2.narrative_function not in ("SYNTHESIS", "CONCLUSION"):
                issues.append({
                    "slide_number": s2.slide_number,
                    "previous_slide": s1.slide_number,
                    "information_gain": round(gain, 3),
                    "message": f"Slide {s2.slide_number} contributes low new information gain ({gain*100:.1f}%) relative to Slide {s1.slide_number}",
                })

        mean_gain = sum(gains) / len(gains) if gains else 1.0
        return round(mean_gain, 3), issues


class PresentationQualityScores(BaseModel):
    narrative_progression: float = 1.0
    purpose_diversity: float = 1.0
    transition_quality: float = 1.0
    cognitive_load_balance: float = 1.0
    concept_fragmentation: float = 0.0
    concept_compression: float = 0.0
    pedagogical_progression: float = 1.0
    redundancy: float = 0.0


class PresentationArchitectureEvaluator:
    """Master evaluator for Task 5 Presentation Architecture quality signals."""

    def __init__(self) -> None:
        self.transition_graph = NarrativeTransitionGraph()
        self.load_validator = CognitiveLoadValidator()
        self.fragmentation_analyzer = ConceptFragmentationAnalyzer()
        self.compression_analyzer = ConceptCompressionAnalyzer()
        self.redundancy_analyzer = SlidePurposeRedundancyAnalyzer()
        self.info_gain_analyzer = InformationGainAnalyzer()

    def evaluate(self, plan: SlidePlan) -> tuple[PresentationQualityScores, list[dict[str, Any]]]:
        """Complete evaluation of presentation architecture signals."""
        slides = plan.slides
        all_issues: list[dict[str, Any]] = []

        if not slides:
            return PresentationQualityScores(), []

        # 1. Narrative transitions
        trans_scores = []
        for i in range(len(slides) - 1):
            s_from = slides[i].narrative_function
            s_to = slides[i+1].narrative_function
            score, msg = self.transition_graph.evaluate_transition(s_from, s_to)
            trans_scores.append(score)
            if score < 0.50:
                all_issues.append({"type": "NARRATIVE_TRANSITION", "slides": [slides[i].slide_number, slides[i+1].slide_number], "detail": msg})

        # Check monotonous streaks
        monotonous = self.transition_graph.detect_monotonous_sequences(slides, max_streak=4)
        for m in monotonous:
            all_issues.append({"type": "MONOTONOUS_NARRATIVE", **m})
            trans_scores.append(0.60)

        narrative_score = round(sum(trans_scores) / len(trans_scores), 3) if trans_scores else 1.0

        # 2. Cognitive load
        load_score, load_issues = self.load_validator.evaluate(slides)
        all_issues.extend(load_issues)

        # 3. Fragmentation
        frag_score, frag_issues = self.fragmentation_analyzer.analyze(slides)
        all_issues.extend(frag_issues)

        # 4. Compression
        comp_score, comp_issues = self.compression_analyzer.analyze(slides)
        all_issues.extend(comp_issues)

        # 5. Redundancy
        red_score, red_issues = self.redundancy_analyzer.analyze(slides)
        all_issues.extend(red_issues)

        # 6. Purpose diversity
        unique_purposes = len({s.narrative_function for s in slides})
        purpose_diversity = round(min(1.0, unique_purposes / 6.0), 3)

        # 7. Pedagogical flow
        unique_pedagogy = len({s.pedagogical_function for s in slides})
        pedagogical_flow = round(min(1.0, unique_pedagogy / 5.0), 3)

        # 8. Information gain
        info_gain, info_issues = self.info_gain_analyzer.analyze(slides)
        all_issues.extend(info_issues)

        scores = PresentationQualityScores(
            narrative_progression=narrative_score,
            purpose_diversity=purpose_diversity,
            transition_quality=narrative_score,
            cognitive_load_balance=load_score,
            concept_fragmentation=frag_score,
            concept_compression=comp_score,
            pedagogical_progression=pedagogical_flow,
            redundancy=red_score,
        )

        return scores, all_issues
