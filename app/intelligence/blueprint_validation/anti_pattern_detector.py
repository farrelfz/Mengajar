"""
Universal Document Intelligence System V5 — Blueprint Anti-Pattern Detector.

Phase 4.1: Cross-artifact structural homogenization and collapse detection.
"""

from __future__ import annotations
from typing import Any


class BlueprintAntiPatternDetector:
    """Detects structural anti-patterns in artifact blueprints."""

    def detect_presentation_collapse(self, blueprint_dict: dict) -> list[str]:
        """Detects signals that a Presentation blueprint has collapsed into Handout structure."""
        signals = []
        slides = blueprint_dict.get("slides", [])
        if not slides:
            return ["No slides found — blueprint is empty."]

        # Signal 1: Missing visual grammar across most slides
        no_grammar = [i for i, s in enumerate(slides) if not s.get("VISUAL_GRAMMAR")]
        if len(no_grammar) > len(slides) * 0.5:
            signals.append(
                f"PRESENTATION→HANDOUT: {len(no_grammar)}/{len(slides)} slides missing VISUAL_GRAMMAR "
                "(prose-first structure detected)."
            )

        # Signal 2: Missing progressive disclosure
        no_disclosure = [i for i, s in enumerate(slides) if not s.get("PROGRESSIVE_DISCLOSURE_PLAN")]
        if len(no_disclosure) > len(slides) * 0.6:
            signals.append(
                f"PRESENTATION→HANDOUT: {len(no_disclosure)}/{len(slides)} slides missing "
                "PROGRESSIVE_DISCLOSURE_PLAN — no cognitive reveal strategy."
            )

        # Signal 3: No narrative transitions
        no_transitions = [i for i, s in enumerate(slides) if not s.get("NARRATIVE_TRANSITION_OUT")]
        if len(no_transitions) > len(slides) * 0.7:
            signals.append(
                f"PRESENTATION→HANDOUT: {len(no_transitions)}/{len(slides)} slides missing "
                "NARRATIVE_TRANSITION_OUT — no story flow."
            )
        return signals

    def detect_quiz_collapse(self, blueprint_dict: dict) -> list[str]:
        """Detects signals that a Worksheet blueprint has collapsed into a quiz sheet."""
        signals = []
        activities = blueprint_dict.get("activities", [])
        if not activities:
            return []

        # Signal 1: All activities are QUESTION type
        stages = [str(a.get("INQUIRY_STAGE", "")).upper() for a in activities]
        question_only = all(s == "QUESTION" for s in stages if s)
        if question_only and len(activities) >= 3:
            signals.append(
                f"WORKSHEET→QUIZ: All {len(activities)} activities are QUESTION stage — "
                "no investigation or observation."
            )

        # Signal 2: No investigation or data collection stages
        inquiry_stages = {"INVESTIGATION", "DATA_COLLECTION", "OBSERVATION", "PHENOMENON"}
        has_inquiry = any(s in inquiry_stages for s in stages)
        if not has_inquiry and len(activities) >= 3:
            signals.append(
                "WORKSHEET→QUIZ: No investigation/observation stages present — "
                "quiz collapse risk is high."
            )

        return signals

    def detect_answer_leak(self, blueprint_dict: dict) -> list[str]:
        """Detects answer leakage signals in Worksheet blueprints."""
        signals = []
        activities = blueprint_dict.get("activities", [])

        for i, act in enumerate(activities):
            # Direct leak: WITHHOLD_EXPLANATION is False on investigation activity
            stage = str(act.get("INQUIRY_STAGE", "")).upper()
            if stage in {"INVESTIGATION", "OBSERVATION", "PREDICTION", "HYPOTHESIS"}:
                if act.get("WITHHOLD_EXPLANATION") is False:
                    signals.append(
                        f"ANSWER_LEAK: activity[{i}] (stage={stage}) has WITHHOLD_EXPLANATION=False."
                    )
                if act.get("ANSWER_LEAK_RISK") is True:
                    signals.append(
                        f"ANSWER_LEAK: activity[{i}] (stage={stage}) is flagged ANSWER_LEAK_RISK=True."
                    )
        return signals

    def detect_scientific_essay_collapse(self, blueprint_dict: dict) -> list[str]:
        """Detects signals that a Scientific Document has collapsed into a narrative essay."""
        signals = []
        arguments = blueprint_dict.get("arguments", [])
        if not arguments:
            return ["No arguments found — scientific document is empty."]

        # Signal 1: Missing evidence types
        no_evidence_type = [i for i, a in enumerate(arguments) if not a.get("EVIDENCE_TYPE")]
        if len(no_evidence_type) > len(arguments) * 0.5:
            signals.append(
                f"SCIENTIFIC→ESSAY: {len(no_evidence_type)}/{len(arguments)} arguments missing "
                "EVIDENCE_TYPE — argument discipline absent."
            )

        # Signal 2: Missing uncertainty states
        no_uncertainty = [i for i, a in enumerate(arguments) if not a.get("UNCERTAINTY_STATE")]
        if len(no_uncertainty) > len(arguments) * 0.5:
            signals.append(
                f"SCIENTIFIC→ESSAY: {len(no_uncertainty)}/{len(arguments)} arguments missing "
                "UNCERTAINTY_STATE — epistemic honesty absent."
            )

        # Signal 3: Missing limitations
        no_limitation = [i for i, a in enumerate(arguments) if not a.get("LIMITATION")]
        if len(no_limitation) == len(arguments):
            signals.append(
                "SCIENTIFIC→ESSAY: No arguments have LIMITATION — "
                "scientific scope boundary absent."
            )
        return signals

    def detect_cross_artifact_homogenization(self, blueprints: dict[str, dict]) -> list[str]:
        """
        Detects structural convergence across the four artifact blueprints.
        blueprints: {"PRESENTATION": {...}, "HANDOUT": {...}, "WORKSHEET": {...}, "SCIENTIFIC_DOCUMENT": {...}}
        """
        signals = []

        # Check if top-level keys are suspiciously identical across artifacts
        key_sets = {art: set(bp.keys()) for art, bp in blueprints.items()}
        art_types = list(key_sets.keys())

        for i in range(len(art_types)):
            for j in range(i + 1, len(art_types)):
                a1, a2 = art_types[i], art_types[j]
                shared = key_sets[a1].intersection(key_sets[a2])
                total = key_sets[a1].union(key_sets[a2])
                if total:
                    similarity = len(shared) / len(total)
                    if similarity > 0.8:
                        signals.append(
                            f"HOMOGENIZATION: {a1} and {a2} share {similarity:.0%} structural keys — "
                            "possible cross-artifact collapse."
                        )
        return signals
