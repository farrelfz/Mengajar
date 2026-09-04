"""
Contradiction and Consistency Detector: Conservative deterministic detection of numeric clashes and direct negations.
"""

from __future__ import annotations

import re
from app.grounding.contracts import Claim, Evidence, SupportRelation


class ContradictionDetector:
    """Detects explicit numeric collisions, direct negations, or logical contradictions between claim and evidence."""

    @classmethod
    def _extract_primary_numbers(cls, text: str) -> set[str]:
        # Ignore isolated exponents like ^2
        cleaned = re.sub(r"\^\d+", "", text)
        return set(re.findall(r"\b\d+(?:\.\d+)?\b", cleaned))

    @classmethod
    def check_relation(cls, claim: Claim, evidence: Evidence) -> tuple[SupportRelation, str]:
        c_text = claim.content.lower()
        e_text = evidence.content.lower()

        # 1. Numeric Clash Check (e.g. 9.8 vs 12 for gravity / constants)
        c_nums = cls._extract_primary_numbers(c_text)
        e_nums = cls._extract_primary_numbers(e_text)

        # Check if same entity or variable has incompatible primary numbers
        if ("gravit" in c_text and "gravit" in e_text) or ("torque" in c_text and "torque" in e_text and c_nums and e_nums):
            if c_nums and e_nums and not c_nums.intersection(e_nums):
                return (SupportRelation.CONTRADICTS, f"Numeric contradiction: value mismatch ({c_nums} vs {e_nums}).")

        # 2. Direct Negation Clash (e.g. "causes" vs "does not cause", "depends on" vs "does not depend on")
        if "does not" in e_text and ("causes" in c_text or "increases when" in c_text or "depends on" in c_text):
            return (SupportRelation.CONTRADICTS, "Negation contradiction: evidence explicitly denies causal claim.")

        if "does not" in c_text and ("causes" in e_text or "increases when" in e_text or "depends on" in e_text):
            return (SupportRelation.CONTRADICTS, "Negation contradiction: claim explicitly denies documented causal relationship.")

        # 3. Keyword / Formula semantic alignment
        c_tokens = set(re.findall(r"\w+", c_text))
        e_tokens = set(re.findall(r"\w+", e_text))
        overlap = len(c_tokens.intersection(e_tokens))
        ratio = overlap / (len(c_tokens) + 1e-6)

        if ratio >= 0.5:
            return (SupportRelation.SUPPORTS, f"Strong token overlap ({ratio:.2f}) and aligned context.")
        elif ratio >= 0.25:
            return (SupportRelation.PARTIALLY_SUPPORTS, f"Moderate token overlap ({ratio:.2f}) with partial alignment.")
        elif ratio > 0:
            return (SupportRelation.RELATED, f"Weak semantic relatedness ({ratio:.2f}).")
        else:
            return (SupportRelation.INSUFFICIENT, "No substantial evidence overlap found.")
