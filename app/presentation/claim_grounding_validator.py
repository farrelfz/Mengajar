"""
Claim-Level Source Grounding Validator.

Evaluates claim-level source traceability and verifies that slide claims
are supported by source evidence (direct, paraphrase, or valid inference)
while blocking unsupported exaggerations, fabricated numbers, or ungrounded statistics.
"""

from __future__ import annotations

import re
import difflib
from typing import Any
from pydantic import BaseModel, Field

from app.intelligence.markdown_tree_parser import ContentTree, ContentBlock
from app.presentation.slide_architect import PlannedSlide, ClaimUnit


EXAGGERATION_PATTERNS = [
    (re.compile(r"\bcompletely\s+prevents\b", re.I), "completely prevents"),
    (re.compile(r"\b100%\s+aman\b", re.I), "100% aman"),
    (re.compile(r"\btanpa\s+risiko\s+sama\s+sekali\b", re.I), "tanpa risiko sama sekali"),
    (re.compile(r"\bmustahil\s+terbakar\b", re.I), "mustahil terbakar"),
    (re.compile(r"\bzero\s+risk\b", re.I), "zero risk"),
    (re.compile(r"\bcompletely\s+eliminates\b", re.I), "completely eliminates"),
]

SPECIFIC_FABRICATION_PATTERNS = [
    (re.compile(r"\btepat\s+\d+\s+(detik|menit|persen)\b", re.I), "fabricated precise quantity"),
    (re.compile(r"\bexactly\s+\d+\s+(seconds|minutes|percent)\b", re.I), "fabricated exact constant"),
]

SECONDARY_BLACKLIST_TERMS = [
    "p < 0.05",
    "p < 0.01",
    "Primary Factor / Treatment",
    "Target Metric / Measured Response",
    "Statistically significant correlation",
    "Hypothesis Test Protocol",
]


class GroundingResult(BaseModel):
    grounding_score: float
    status: str  # "PASS", "WARNING", "FAIL"
    total_claims: int
    direct_support_count: int
    paraphrase_support_count: int
    inferred_support_count: int
    unsupported_count: int
    unsupported_claims: list[dict[str, Any]] = Field(default_factory=list)
    secondary_blacklist_hits: list[str] = Field(default_factory=list)


class ClaimGroundingValidator:
    """Validates factual claims on slides against referenced source blocks."""

    def __init__(self, tree: ContentTree | None = None) -> None:
        self.tree = tree
        self.source_block_map: dict[str, str] = {}
        if tree:
            for blk in tree.all_blocks_flat():
                self.source_block_map[blk.id] = blk.content
            for sec in tree.all_sections_flat():
                sec_text = " ".join(b.content for b in sec.blocks)
                self.source_block_map[sec.id] = f"{sec.title}. {sec_text}"

    def update_tree(self, tree: ContentTree) -> None:
        self.tree = tree
        self.source_block_map.clear()
        for blk in tree.all_blocks_flat():
            self.source_block_map[blk.id] = blk.content
        for sec in tree.all_sections_flat():
            sec_text = " ".join(b.content for b in sec.blocks)
            self.source_block_map[sec.id] = f"{sec.title}. {sec_text}"

    def evaluate_claim(self, claim: ClaimUnit, source_corpus: str) -> tuple[str, float, str]:
        """Evaluates support level of a claim against source text.
        Returns (support_level, confidence, detail).
        Levels: DIRECT_SUPPORT, PARAPHRASE_SUPPORT, INFERRED_SUPPORT, UNSUPPORTED.
        """
        claim_text = claim.text.strip()
        if not claim_text:
            return "INFERRED_SUPPORT", 1.0, "Empty or structural statement"

        claim_lower = claim_text.lower()
        source_lower = source_corpus.lower()

        # Pedagogical synthesis and concluding integration statements
        if any(k in claim_lower for k in ["sintesis", "peta konsep", "kesimpulan", "integrate", "conclude", "rangkuman", "refleksi", "penutup"]):
            return "INFERRED_SUPPORT", 0.95, "Pedagogical synthesis and concluding integration statement"

        # 1. Check for Unsupported Exaggerations
        for pat, desc in EXAGGERATION_PATTERNS:
            if pat.search(claim_lower) and not pat.search(source_lower):
                return "UNSUPPORTED", 0.0, f"Unsupported exaggeration: '{desc}' not found or qualified in source evidence"

        # 2. Check for Unsupported Specific Numerical Fabrications
        for pat, desc in SPECIFIC_FABRICATION_PATTERNS:
            if pat.search(claim_lower) and not pat.search(source_lower):
                return "UNSUPPORTED", 0.1, f"Unsupported specific claim: '{desc}' not present in source text"

        # 3. Direct Support (high lexical overlap or substring containment)
        if claim_lower in source_lower:
            return "DIRECT_SUPPORT", 1.0, "Exact lexical substring match in source evidence"

        # Extract meaningful tokens (length >= 4)
        c_tokens = set(re.findall(r"\b[a-z0-9_-]{4,}\b", claim_lower))
        s_tokens = set(re.findall(r"\b[a-z0-9_-]{4,}\b", source_lower))

        if not c_tokens:
            return "INFERRED_SUPPORT", 0.8, "Short generic phrase"

        overlap = len(c_tokens.intersection(s_tokens)) / len(c_tokens)

        if overlap >= 0.70:
            return "DIRECT_SUPPORT", round(overlap, 2), f"Strong lexical overlap ({overlap*100:.0f}%)"
        elif overlap >= 0.35:
            return "PARAPHRASE_SUPPORT", round(overlap, 2), f"Valid semantic paraphrase ({overlap*100:.0f}% key terms grounded)"
        elif overlap >= 0.15:
            return "INFERRED_SUPPORT", round(overlap, 2), f"Contextual pedagogical inference ({overlap*100:.0f}% term alignment)"
        else:
            return "UNSUPPORTED", round(overlap, 2), f"Unsupported claim: only {overlap*100:.0f}% term alignment with source evidence"

    def evaluate(self, slides: list[PlannedSlide]) -> GroundingResult:
        """Evaluates all claims across all slides against the source tree."""
        all_claims = [c for s in slides for c in s.claim_units]
        
        # Build total source corpus
        full_source = " ".join(self.source_block_map.values())

        direct_cnt = 0
        para_cnt = 0
        infer_cnt = 0
        unsupported_cnt = 0
        unsupported_list: list[dict[str, Any]] = []
        blacklist_hits: list[str] = []

        # Secondary blacklist check across all slides
        for s in slides:
            claims_corpus = " ".join(c.text for c in s.claim_units)
            slide_corpus = f"{s.title} {s.purpose} {claims_corpus} " + " ".join(b.content for b in s.key_blocks)
            for term in SECONDARY_BLACKLIST_TERMS:
                if term.lower() in slide_corpus.lower() and term.lower() not in full_source.lower():
                    blacklist_hits.append(f"Slide {s.slide_number}: Blacklisted term '{term}'")

        for s in slides:
            # Build slide-specific referenced source corpus
            ref_texts = [self.source_block_map.get(ref, "") for ref in s.source_refs if ref in self.source_block_map]
            ref_corpus = " ".join(ref_texts) if ref_texts else full_source

            for c in s.claim_units:
                level, conf, detail = self.evaluate_claim(c, ref_corpus)
                c.support_level = level

                if level == "DIRECT_SUPPORT":
                    direct_cnt += 1
                elif level == "PARAPHRASE_SUPPORT":
                    para_cnt += 1
                elif level == "INFERRED_SUPPORT":
                    infer_cnt += 1
                else:
                    # Find independent best source match across entire document
                    best_match_id = None
                    best_sim = 0.0
                    c_lower = c.text.lower()
                    c_tokens = set(re.findall(r"\b[a-z0-9_-]{4,}\b", c_lower))
                    for b_id, b_text in self.source_block_map.items():
                        b_lower = b_text.lower()
                        if not b_lower or not c_tokens:
                            continue
                        b_tokens = set(re.findall(r"\b[a-z0-9_-]{4,}\b", b_lower))
                        sim = len(c_tokens & b_tokens) / len(c_tokens) if c_tokens else 0.0
                        if sim > best_sim:
                            best_sim = sim
                            best_match_id = b_id

                    # Determine root cause and repair action
                    if best_sim >= 0.35 and best_match_id:
                        failure_reason = f"Source evidence exists in block '{best_match_id}' ({best_sim*100:.0f}% term match), but was not declared in slide provenance"
                        severity = "WARNING"
                        repair_action = "update_provenance"
                    elif any(pat.search(c_lower) for pat, _ in EXAGGERATION_PATTERNS):
                        failure_reason = detail
                        severity = "WARNING"
                        repair_action = "soften_exaggeration"
                    else:
                        failure_reason = detail
                        severity = "CRITICAL"
                        repair_action = "remove_claim" if best_sim < 0.20 else "update_provenance"

                    unsupported_cnt += 1
                    unsupported_list.append({
                        "claim_id": c.claim_id,
                        "slide": s.slide_number,
                        "claim_text": c.text,
                        "declared_source_refs": s.source_refs,
                        "independent_best_source_match": [best_match_id] if best_match_id else [],
                        "similarity": round(best_sim, 3),
                        "failure_reason": failure_reason,
                        "severity": severity,
                        "repair_action": repair_action,
                        "detail": detail,
                    })

        total = len(all_claims)
        supported = direct_cnt + para_cnt + (infer_cnt * 0.9)
        score = (supported / total) if total > 0 else 1.0

        # Export is blocked if there are critical unsupported claims or blacklist hits
        status = "PASS"
        if unsupported_cnt > 0 or len(blacklist_hits) > 0:
            status = "FAIL"
        elif infer_cnt > (total * 0.4):
            status = "WARNING"

        return GroundingResult(
            grounding_score=round(score, 3),
            status=status,
            total_claims=total,
            direct_support_count=direct_cnt,
            paraphrase_support_count=para_cnt,
            inferred_support_count=infer_cnt,
            unsupported_count=unsupported_cnt,
            unsupported_claims=unsupported_list,
            secondary_blacklist_hits=blacklist_hits,
        )
