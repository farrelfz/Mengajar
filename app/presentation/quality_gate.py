"""
Quality Gate System & Validation Engine (Task 9).

Enforces the comprehensive 25-Gate Presentation Quality Matrix with
explicit state-machine statuses (PASS, WARNING, REPAIR_REQUIRED, CRITICAL_FAILURE, STALE),
robust HTML-stripped duplicate slide analysis, claim grounding diagnostics, and versioned QualityRounds.
"""

from __future__ import annotations

import re
import difflib
import time
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.intelligence.markdown_tree_parser import ContentTree
from app.intelligence.content_manifest import ContentManifest, ContentPriority
from app.presentation.slide_architect import SlidePlan, PlannedSlide
from app.presentation.slide_generator import GeneratedSlide
from app.presentation.narrative_evaluator import PresentationArchitectureEvaluator
from app.presentation.semantic_layout_validator import SemanticLayoutValidator
from app.presentation.claim_grounding_validator import ClaimGroundingValidator
from app.presentation.visual_qa import VisualQualityAnalyzer, LayoutDOMInspector, VisualQualityReport
from app.presentation.rhythm_analyzer import PresentationRhythmAnalyzer


class GateStatus(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    REPAIR_REQUIRED = "REPAIR_REQUIRED"
    CRITICAL_FAILURE = "CRITICAL_FAILURE"
    BLOCKED = "BLOCKED"
    NOT_EVALUATED = "NOT_EVALUATED"
    STALE = "STALE"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class Repairability(str, Enum):
    DETERMINISTIC_REPAIRABLE = "DETERMINISTIC_REPAIRABLE"
    AI_ASSISTED_REPAIRABLE = "AI_ASSISTED_REPAIRABLE"
    MANUAL_REPAIR_REQUIRED = "MANUAL_REPAIR_REQUIRED"
    NON_REPAIRABLE = "NON_REPAIRABLE"


class DuplicateCategory(str, Enum):
    UNIQUE = "UNIQUE"
    EXACT_DUPLICATE = "EXACT_DUPLICATE"
    NEAR_TEXTUAL_DUPLICATE = "NEAR_TEXTUAL_DUPLICATE"
    CONCEPT_PROGRESSION = "CONCEPT_PROGRESSION"
    INTENTIONAL_CONTINUITY = "INTENTIONAL_CONTINUITY"
    VISUAL_TEMPLATE_SIMILARITY = "VISUAL_TEMPLATE_SIMILARITY"
    TRUE_REDUNDANT = "TRUE_REDUNDANT"


class DuplicateSlideAnalyzer:
    """Forensic slide deduplication analyzer.

    Distinguishes raw template HTML similarity from genuine semantic duplication,
    intentional concept continuity, and concept progression.
    """

    @staticmethod
    def strip_html(html_str: str) -> str:
        clean = re.sub(r"<(script|style).*?</\1>", "", html_str, flags=re.DOTALL | re.IGNORECASE)
        clean = re.sub(r"<[^>]+>", " ", clean)
        return re.sub(r"\s+", " ", clean).strip()

    @classmethod
    def analyze(
        cls,
        slides: list[GeneratedSlide],
        planned_slides: list[PlannedSlide] | None = None,
    ) -> tuple[float, list[int], list[dict[str, Any]], str]:
        """Analyzes slides for true duplication versus template similarity or intentional continuity.

        Returns:
            (duplicate_rate, redundant_slide_numbers, matching_pairs, summary_details)
        """
        n_slides = len(slides)
        if n_slides <= 1:
            return 0.0, [], [], "No duplicates (<= 1 slide)"

        plan_map = {s.slide_number: s for s in planned_slides} if planned_slides else {}
        clean_texts = [cls.strip_html(s.rendered_html) for s in slides]

        redundant_slide_numbers: set[int] = set()
        flagged_pairs: list[dict[str, Any]] = []

        for i in range(n_slides):
            t_i = clean_texts[i].lower()
            tokens_i = set(re.findall(r"\b\w{4,}\b", t_i))
            p_i = plan_map.get(slides[i].slide_number)
            claims_i = set(c.text.lower() for c in p_i.claim_units) if p_i else set()
            narrative_a = p_i.narrative_function if p_i else "UNKNOWN"
            concept_a = p_i.primary_concept if p_i else ""

            for j in range(i + 1, n_slides):
                t_j = clean_texts[j].lower()
                tokens_j = set(re.findall(r"\b\w{4,}\b", t_j))
                p_j = plan_map.get(slides[j].slide_number)
                claims_j = set(c.text.lower() for c in p_j.claim_units) if p_j else set()
                narrative_b = p_j.narrative_function if p_j else "UNKNOWN"
                concept_b = p_j.primary_concept if p_j else ""

                text_sim = difflib.SequenceMatcher(None, t_i, t_j).ratio() if (t_i and t_j) else 0.0
                raw_sim = difflib.SequenceMatcher(None, slides[i].rendered_html, slides[j].rendered_html).ratio()

                # Calculate claim and concept overlap
                claim_overlap = len(claims_i & claims_j) / max(len(claims_j), 1) if claims_j else 0.0
                concept_overlap = 1.0 if (concept_a and concept_a == concept_b) else 0.0

                # Calculate information gain of slide j relative to slide i
                info_gain = len(tokens_j - tokens_i) / max(len(tokens_j), 1) if tokens_j else 0.0
                adjacency = abs(slides[i].slide_number - slides[j].slide_number)

                # Explicit continuity markers
                continuity = False
                if p_i and p_j:
                    if (concept_a == concept_b or adjacency == 1) and (
                        "lanjutan" in p_j.title.lower()
                        or "bagian" in p_j.title.lower()
                        or "step" in p_j.title.lower()
                        or "tahap" in p_j.title.lower()
                        or p_j.transition_from_previous
                    ):
                        continuity = True

                category = DuplicateCategory.UNIQUE
                action = "KEEP"

                # Multi-dimensional classification
                if text_sim >= 0.95 and (claim_overlap >= 0.70 or not claims_j) and not continuity:
                    category = DuplicateCategory.EXACT_DUPLICATE
                    action = "REMOVE"
                    redundant_slide_numbers.add(slides[j].slide_number)
                elif text_sim >= 0.82 and not continuity:
                    if narrative_a != narrative_b:
                        category = DuplicateCategory.CONCEPT_PROGRESSION
                        action = "KEEP"
                    elif info_gain >= 0.18:
                        category = DuplicateCategory.CONCEPT_PROGRESSION
                        action = "KEEP"
                    elif adjacency <= 3 and claim_overlap >= 0.50:
                        category = DuplicateCategory.TRUE_REDUNDANT
                        action = "MERGE"
                        redundant_slide_numbers.add(slides[j].slide_number)
                    else:
                        category = DuplicateCategory.INTENTIONAL_CONTINUITY
                        action = "KEEP"
                elif raw_sim >= 0.85 and text_sim < 0.45:
                    category = DuplicateCategory.VISUAL_TEMPLATE_SIMILARITY
                    action = "KEEP"
                elif continuity:
                    category = DuplicateCategory.INTENTIONAL_CONTINUITY
                    action = "KEEP"
                elif narrative_a != narrative_b:
                    category = DuplicateCategory.CONCEPT_PROGRESSION
                    action = "KEEP"

                # Record diagnostic report for any pair with noticeable similarity
                if text_sim >= 0.70 or category in (DuplicateCategory.EXACT_DUPLICATE, DuplicateCategory.TRUE_REDUNDANT):
                    flagged_pairs.append({
                        "slides": [slides[i].slide_number, slides[j].slide_number],
                        "text_similarity": round(text_sim, 3),
                        "claim_overlap": round(claim_overlap, 3),
                        "concept_overlap": round(concept_overlap, 3),
                        "narrative_function_a": narrative_a,
                        "narrative_function_b": narrative_b,
                        "information_gain": round(info_gain, 3),
                        "classification": category.value,
                        "recommended_action": action,
                    })

        dup_rate = len(redundant_slide_numbers) / n_slides
        details = (
            f"Duplicate rate: {dup_rate*100:.1f}% ({len(redundant_slide_numbers)} redundant slides out of {n_slides}). "
            f"Flagged {len(flagged_pairs)} candidate slide pairs."
        )
        return round(dup_rate, 3), sorted(list(redundant_slide_numbers)), flagged_pairs, details


class GateResult(BaseModel):
    gate_id: str
    gate_name: str
    category: str = "Semantic"  # Semantic, Visual, Presentation, Safety
    status: GateStatus = GateStatus.PASS
    passed: bool = True
    score: float = 1.0
    threshold: float = 0.0
    severity: Severity = Severity.CRITICAL
    repairability: Repairability = Repairability.DETERMINISTIC_REPAIRABLE
    root_cause: Optional[str] = None
    affected_slides: list[int] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)
    details: str = ""
    qa_version: int = 1
    is_blocking: bool = True


class QualityRound(BaseModel):
    round_id: int = 1
    artifact_version: int = 1
    total_gates: int = 25
    passed_gates: int = 0
    failed_gates: int = 0
    warning_gates: int = 0
    critical_failures: int = 0
    repairable_failures: int = 0
    gate_results: list[GateResult] = Field(default_factory=list)
    critical_coverage: float = 1.0
    important_coverage: float = 1.0
    duplicate_rate: float = 0.0
    layout_entropy: float = 1.0
    hallucination_count: int = 0
    grounding_score: float = 1.0
    visual_score: float = 1.0
    narrative_score: float = 1.0
    rhythm_score: float = 1.0
    overall_score: float = 1.0
    overall_passed: bool = True
    export_blocked: bool = False
    blocking_reasons: list[str] = Field(default_factory=list)
    warning_reasons: list[str] = Field(default_factory=list)
    repair_plan: Optional[Any] = None
    timestamp: float = Field(default_factory=time.time)

    def has_repairable_failures(self) -> bool:
        return self.repairable_failures > 0 or any(
            g.status == GateStatus.REPAIR_REQUIRED for g in self.gate_results
        )

    def has_critical_failures(self) -> bool:
        return self.critical_failures > 0 or any(
            g.status in (GateStatus.CRITICAL_FAILURE, GateStatus.BLOCKED) for g in self.gate_results
        )


QualityValidationReport = QualityRound


class PresentationQualityGate:
    """Master evaluator for the 25-Gate Presentation Quality Matrix."""

    def __init__(self) -> None:
        self.architecture_evaluator = PresentationArchitectureEvaluator()
        self.semantic_validator = SemanticLayoutValidator()
        self.grounding_validator = ClaimGroundingValidator()
        self.visual_analyzer = VisualQualityAnalyzer()
        self.rhythm_analyzer = PresentationRhythmAnalyzer()
        self.dom_inspector = LayoutDOMInspector()

    def evaluate(
        self,
        tree: ContentTree,
        manifest: ContentManifest,
        plan: SlidePlan,
        slides: list[GeneratedSlide],
        pdf_path: Path | None = None,
        round_id: int = 1,
        artifact_version: int = 1,
    ) -> QualityRound:
        gates: list[GateResult] = []
        blocking_reasons: list[str] = []
        warning_reasons: list[str] = []

        slide_count = len(slides)
        all_covered_refs: set[str] = set()
        for s in slides:
            all_covered_refs.update(s.source_refs)

        # -------------------------------------------------------------
        # GATE 1: Source Parsing Success >= 95% (Critical)
        # -------------------------------------------------------------
        parsing_score = 1.0 if tree.total_sections_count > 0 and tree.total_blocks_count > 0 else 0.0
        g1_pass = parsing_score >= 0.95
        gates.append(
            GateResult(
                gate_id="GATE_1_PARSING",
                gate_name="Source Parsing Integrity",
                category="Semantic",
                status=GateStatus.PASS if g1_pass else GateStatus.CRITICAL_FAILURE,
                passed=g1_pass,
                score=parsing_score,
                threshold=0.95,
                severity=Severity.CRITICAL,
                repairability=Repairability.NON_REPAIRABLE,
                details=f"Parsed {tree.total_sections_count} sections and {tree.total_blocks_count} blocks",
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g1_pass:
            blocking_reasons.append("Gate 1 Failed: Markdown parsing produced empty structural tree")

        # -------------------------------------------------------------
        # GATE 2: Critical Content Coverage >= 95% (Critical)
        # -------------------------------------------------------------
        crit_count = len(manifest.critical_concepts)
        crit_covered = 0
        for c in manifest.critical_concepts:
            if c.source_section_id in all_covered_refs or any(b_id in all_covered_refs for b_id in c.source_block_ids):
                crit_covered += 1

        crit_coverage = (crit_covered / crit_count) if crit_count > 0 else 1.0
        g2_pass = crit_coverage >= 0.95
        gates.append(
            GateResult(
                gate_id="GATE_2_CRITICAL_COVERAGE",
                gate_name="Critical Content Coverage",
                category="Semantic",
                status=GateStatus.PASS if g2_pass else GateStatus.CRITICAL_FAILURE,
                passed=g2_pass,
                score=round(crit_coverage, 3),
                threshold=0.95,
                severity=Severity.CRITICAL,
                repairability=Repairability.AI_ASSISTED_REPAIRABLE,
                root_cause=f"Missing {crit_count - crit_covered} critical concepts in slide plan" if not g2_pass else None,
                details=f"Covered {crit_covered}/{crit_count} critical concepts ({crit_coverage*100:.1f}%)",
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g2_pass:
            blocking_reasons.append(f"Gate 2 Failed: Critical coverage ({crit_coverage*100:.1f}%) < 95%")

        # -------------------------------------------------------------
        # GATE 3: Important Content Coverage >= 85% (Critical)
        # -------------------------------------------------------------
        imp_count = len(manifest.important_concepts)
        imp_covered = 0
        for c in manifest.important_concepts:
            if c.source_section_id in all_covered_refs or any(b_id in all_covered_refs for b_id in c.source_block_ids):
                imp_covered += 1

        imp_coverage = (imp_covered / imp_count) if imp_count > 0 else 1.0
        g3_pass = imp_coverage >= 0.85
        gates.append(
            GateResult(
                gate_id="GATE_3_IMPORTANT_COVERAGE",
                gate_name="Important Content Coverage",
                category="Semantic",
                status=GateStatus.PASS if g3_pass else GateStatus.REPAIR_REQUIRED,
                passed=g3_pass,
                score=round(imp_coverage, 3),
                threshold=0.85,
                severity=Severity.CRITICAL,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                root_cause=f"Missing {imp_count - imp_covered} important concepts" if not g3_pass else None,
                details=f"Covered {imp_covered}/{imp_count} important concepts ({imp_coverage*100:.1f}%)",
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g3_pass:
            blocking_reasons.append(f"Gate 3 Failed: Important coverage ({imp_coverage*100:.1f}%) < 85%")

        # -------------------------------------------------------------
        # GATE 4: Generated Slide Count >= Estimated Minimum (Critical)
        # -------------------------------------------------------------
        g4_pass = slide_count >= manifest.min_slides
        gates.append(
            GateResult(
                gate_id="GATE_4_SLIDE_COUNT",
                gate_name="Minimum Slide Count & Allocation Sanity",
                category="Presentation",
                status=GateStatus.PASS if g4_pass else GateStatus.REPAIR_REQUIRED,
                passed=g4_pass,
                score=float(slide_count),
                threshold=float(manifest.min_slides),
                severity=Severity.CRITICAL,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                details=f"Generated {slide_count} slides (Target: {manifest.min_slides}–{manifest.max_slides})",
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g4_pass:
            blocking_reasons.append(f"Gate 4 Failed: Generated slide count ({slide_count}) < estimated min ({manifest.min_slides})")

        # -------------------------------------------------------------
        # GATE 5: Duplicate Slide Rate < 10% (Critical)
        # -------------------------------------------------------------
        dup_rate, redundant_slides, dup_pairs, dup_details = DuplicateSlideAnalyzer.analyze(slides, plan.slides)
        g5_pass = dup_rate < 0.10
        gates.append(
            GateResult(
                gate_id="GATE_5_DUPLICATES",
                gate_name="Duplicate Slide Rate Limit",
                category="Safety",
                status=GateStatus.PASS if g5_pass else GateStatus.REPAIR_REQUIRED,
                passed=g5_pass,
                score=round(dup_rate, 3),
                threshold=0.10,
                severity=Severity.CRITICAL,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                root_cause="Over-fragmented blocks causing redundant content repetition" if not g5_pass else None,
                affected_slides=redundant_slides,
                evidence={"matching_pairs": dup_pairs, "redundant_slides": redundant_slides},
                details=dup_details,
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g5_pass:
            blocking_reasons.append(f"Gate 5 Failed: Duplicate slide rate ({dup_rate*100:.1f}%) >= 10%")

        # -------------------------------------------------------------
        # GATE 6: No Identical Consecutive Slides (Critical)
        # -------------------------------------------------------------
        consecutive_identical = False
        consecutive_pair: list[int] = []
        for i in range(len(slides) - 1):
            if slides[i].title == slides[i + 1].title and slides[i].layout == slides[i + 1].layout:
                clean_a = DuplicateSlideAnalyzer.strip_html(slides[i].rendered_html)
                clean_b = DuplicateSlideAnalyzer.strip_html(slides[i + 1].rendered_html)
                sim = difflib.SequenceMatcher(None, clean_a, clean_b).ratio()
                if sim > 0.80:
                    consecutive_identical = True
                    consecutive_pair = [slides[i].slide_number, slides[i + 1].slide_number]
                    break

        g6_pass = not consecutive_identical
        gates.append(
            GateResult(
                gate_id="GATE_6_CONSECUTIVE_IDENTICAL",
                gate_name="No Identical Consecutive Slides",
                category="Safety",
                status=GateStatus.PASS if g6_pass else GateStatus.CRITICAL_FAILURE,
                passed=g6_pass,
                score=0.0 if consecutive_identical else 1.0,
                threshold=1.0,
                severity=Severity.CRITICAL,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                root_cause="Duplicate consecutive slide generated with identical content" if consecutive_identical else None,
                affected_slides=consecutive_pair,
                details="No identical consecutive slides detected" if g6_pass else f"Identical consecutive slides: {consecutive_pair}",
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g6_pass:
            blocking_reasons.append("Gate 6 Failed: Identical consecutive slides detected")

        # -------------------------------------------------------------
        # GATE 7: Anti-Hallucination & Blacklist Guard (Critical)
        # -------------------------------------------------------------
        hallucination_warnings = sum(1 for s in slides if s.has_hallucination_warning)
        g7_pass = hallucination_warnings == 0
        gates.append(
            GateResult(
                gate_id="GATE_7_ANTI_HALLUCINATION",
                gate_name="Anti-Hallucination & Blacklist Guard",
                category="Safety",
                status=GateStatus.PASS if g7_pass else GateStatus.CRITICAL_FAILURE,
                passed=g7_pass,
                score=float(hallucination_warnings),
                threshold=0.0,
                severity=Severity.CRITICAL,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                root_cause="Forbidden terms or fabricated statistics detected" if not g7_pass else None,
                details=f"{hallucination_warnings} forbidden blacklist or ungrounded claims detected",
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g7_pass:
            blocking_reasons.append(f"Gate 7 Failed: {hallucination_warnings} hallucinated claims detected")

        # -------------------------------------------------------------
        # GATE 8: Zero System Logs inside Content (Critical)
        # -------------------------------------------------------------
        log_errors = sum(1 for s in slides if s.has_sanitization_error)
        g8_pass = log_errors == 0
        gates.append(
            GateResult(
                gate_id="GATE_8_LOG_SANITIZATION",
                gate_name="System Log Content Sanitization",
                category="Safety",
                status=GateStatus.PASS if g8_pass else GateStatus.CRITICAL_FAILURE,
                passed=g8_pass,
                score=float(log_errors),
                threshold=0.0,
                severity=Severity.CRITICAL,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                details=f"{log_errors} slides contaminated with system log patterns",
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g8_pass:
            blocking_reasons.append(f"Gate 8 Failed: {log_errors} slides contain system log timestamps/errors")

        # -------------------------------------------------------------
        # GATE 9: Layout Diversity Passes (Warning)
        # -------------------------------------------------------------
        layout_counts = plan.layout_distribution
        max_layout_pct = (max(layout_counts.values()) / slide_count) if (slide_count > 0 and layout_counts) else 1.0
        g9_pass = max_layout_pct <= 0.50 and plan.layout_entropy >= 0.50
        gates.append(
            GateResult(
                gate_id="GATE_9_LAYOUT_DIVERSITY",
                gate_name="Presentation Layout Diversity",
                category="Presentation",
                status=GateStatus.PASS if g9_pass else GateStatus.WARNING,
                passed=g9_pass,
                score=round(plan.layout_entropy, 3),
                threshold=0.50,
                severity=Severity.WARNING,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                details=f"Entropy: {plan.layout_entropy}, Dominant layout: {max_layout_pct*100:.1f}%",
                qa_version=artifact_version,
                is_blocking=False,
            )
        )
        if not g9_pass:
            warning_reasons.append(f"Gate 9 Warning: Single layout dominates {max_layout_pct*100:.1f}% > 50%")

        # -------------------------------------------------------------
        # GATE 10: All Slides have source_refs (Critical)
        # -------------------------------------------------------------
        slides_without_refs = sum(1 for s in slides if not s.source_refs)
        g10_pass = slides_without_refs == 0
        gates.append(
            GateResult(
                gate_id="GATE_10_BIDIRECTIONAL_TRACEABILITY",
                gate_name="Bidirectional Source Traceability",
                category="Semantic",
                status=GateStatus.PASS if g10_pass else GateStatus.CRITICAL_FAILURE,
                passed=g10_pass,
                score=1.0 if g10_pass else 0.0,
                threshold=1.0,
                severity=Severity.CRITICAL,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                details="100% of slides contain bidirectional source block references" if g10_pass else f"{slides_without_refs} slides lack source references",
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g10_pass:
            blocking_reasons.append(f"Gate 10 Failed: {slides_without_refs} slides lack source references")

        # -------------------------------------------------------------
        # GATE 11: Claim-Level Source Grounding (Critical)
        # -------------------------------------------------------------
        self.grounding_validator.update_tree(tree)
        grounding_report = self.grounding_validator.evaluate(plan.slides)
        g11_pass = grounding_report.unsupported_count == 0 and grounding_report.grounding_score >= 0.85
        status_11 = GateStatus.PASS if g11_pass else GateStatus.REPAIR_REQUIRED
        affected_11 = [u["slide"] for u in grounding_report.unsupported_claims]
        gates.append(
            GateResult(
                gate_id="GATE_11_CLAIM_GROUNDING",
                gate_name="Claim-Level Source Grounding",
                category="Semantic",
                status=status_11,
                passed=g11_pass,
                score=grounding_report.grounding_score,
                threshold=0.85,
                severity=Severity.CRITICAL,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                root_cause="Unlinked source provenance or ungrounded statement" if not g11_pass else None,
                affected_slides=affected_11,
                evidence={
                    "unsupported_claims": grounding_report.unsupported_claims,
                    "blacklist_hits": grounding_report.secondary_blacklist_hits,
                },
                details=f"{grounding_report.direct_support_count} direct, {grounding_report.paraphrase_support_count} paraphrase, {grounding_report.unsupported_count} unsupported claims",
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g11_pass:
            blocking_reasons.append(f"Gate 11 Failed: {grounding_report.unsupported_count} unsupported claims detected")

        # -------------------------------------------------------------
        # GATE 12: Presentation Narrative Quality (Warning)
        # -------------------------------------------------------------
        arch_scores, _ = self.architecture_evaluator.evaluate(plan)
        g12_pass = arch_scores.narrative_progression >= 0.70
        gates.append(
            GateResult(
                gate_id="GATE_12_NARRATIVE_QUALITY",
                gate_name="Presentation Narrative Progression",
                category="Semantic",
                status=GateStatus.PASS if g12_pass else GateStatus.WARNING,
                passed=g12_pass,
                score=arch_scores.narrative_progression,
                threshold=0.70,
                severity=Severity.WARNING,
                repairability=Repairability.AI_ASSISTED_REPAIRABLE,
                details=f"Narrative score: {arch_scores.narrative_progression*100:.1f}%, purpose diversity: {arch_scores.purpose_diversity*100:.1f}%",
                qa_version=artifact_version,
                is_blocking=False,
            )
        )
        if not g12_pass:
            warning_reasons.append(f"Gate 12 Warning: Narrative progression score is {arch_scores.narrative_progression*100:.1f}% (< 70%)")

        # -------------------------------------------------------------
        # GATE 13: Cognitive Load Balance (Warning)
        # -------------------------------------------------------------
        g13_pass = arch_scores.cognitive_load_balance >= 0.75
        gates.append(
            GateResult(
                gate_id="GATE_13_COGNITIVE_LOAD",
                gate_name="Cognitive Load Distribution",
                category="Semantic",
                status=GateStatus.PASS if g13_pass else GateStatus.WARNING,
                passed=g13_pass,
                score=arch_scores.cognitive_load_balance,
                threshold=0.75,
                severity=Severity.WARNING,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                details=f"Cognitive load balance: {arch_scores.cognitive_load_balance*100:.1f}%",
                qa_version=artifact_version,
                is_blocking=False,
            )
        )
        if not g13_pass:
            warning_reasons.append(f"Gate 13 Warning: Cognitive load balance is {arch_scores.cognitive_load_balance*100:.1f}% (< 75%)")

        # -------------------------------------------------------------
        # GATE 14: Concept Fragmentation Avoidance (Warning)
        # -------------------------------------------------------------
        g14_pass = arch_scores.concept_fragmentation <= 0.35
        gates.append(
            GateResult(
                gate_id="GATE_14_CONCEPT_FRAGMENTATION",
                gate_name="Concept Fragmentation Avoidance",
                category="Semantic",
                status=GateStatus.PASS if g14_pass else GateStatus.WARNING,
                passed=g14_pass,
                score=round(1.0 - arch_scores.concept_fragmentation, 3),
                threshold=0.65,
                severity=Severity.WARNING,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                details=f"Fragmentation index: {arch_scores.concept_fragmentation:.2f} (lower is better)",
                qa_version=artifact_version,
                is_blocking=False,
            )
        )
        if not g14_pass:
            warning_reasons.append(f"Gate 14 Warning: Concept fragmentation index is high ({arch_scores.concept_fragmentation:.2f})")

        # -------------------------------------------------------------
        # GATE 15: Concept Compression Avoidance (Warning)
        # -------------------------------------------------------------
        g15_pass = arch_scores.concept_compression <= 0.35
        gates.append(
            GateResult(
                gate_id="GATE_15_CONCEPT_COMPRESSION",
                gate_name="Concept Compression Avoidance",
                category="Semantic",
                status=GateStatus.PASS if g15_pass else GateStatus.WARNING,
                passed=g15_pass,
                score=round(1.0 - arch_scores.concept_compression, 3),
                threshold=0.65,
                severity=Severity.WARNING,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                details=f"Compression index: {arch_scores.concept_compression:.2f} (lower is better)",
                qa_version=artifact_version,
                is_blocking=False,
            )
        )
        if not g15_pass:
            warning_reasons.append(f"Gate 15 Warning: Concept compression index is high ({arch_scores.concept_compression:.2f})")

        # -------------------------------------------------------------
        # GATE 16: Semantic Layout Alignment (Critical)
        # -------------------------------------------------------------
        semantic_layout_res = self.semantic_validator.evaluate(plan.slides)
        g16_pass = semantic_layout_res.status != "FAIL" and semantic_layout_res.alignment_score >= 0.75
        status_16 = GateStatus.PASS if g16_pass else GateStatus.REPAIR_REQUIRED
        affected_16 = [v["slide_number"] for v in semantic_layout_res.violations]
        gates.append(
            GateResult(
                gate_id="GATE_16_SEMANTIC_LAYOUT_ALIGNMENT",
                gate_name="Semantic Layout Appropriateness",
                category="Semantic",
                status=status_16,
                passed=g16_pass,
                score=semantic_layout_res.alignment_score,
                threshold=0.75,
                severity=Severity.CRITICAL,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                root_cause="Layout assignment mismatched narrative role according to Visual Grammar Matrix" if not g16_pass else None,
                affected_slides=affected_16,
                evidence={"violations": semantic_layout_res.violations},
                details=f"Alignment score: {semantic_layout_res.alignment_score*100:.1f}%, violations: {semantic_layout_res.penalized_slides}",
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g16_pass:
            blocking_reasons.append(f"Gate 16 Failed: Severe semantic layout mismatch ({semantic_layout_res.penalized_slides} slides)")

        # -------------------------------------------------------------
        # VISUAL INSPECTION VIA PYMUPDF OR DOM
        # -------------------------------------------------------------
        if pdf_path and pdf_path.exists():
            visual_rep = self.visual_analyzer.analyze_pdf(pdf_path, slides)
        else:
            dom_issues = []
            for i, s in enumerate(slides):
                iss = self.dom_inspector.inspect_slide_html(i + 1, s.layout, s.rendered_html)
                dom_issues.extend(iss)
            crit_iss = sum(1 for d in dom_issues if d.is_blocking)
            visual_rep = VisualQualityReport(
                passed=crit_iss == 0,
                overall_score=max(0.0, 1.0 - (len(dom_issues) * 0.05)),
                critical_issues=crit_iss,
                warning_issues=len(dom_issues) - crit_iss,
                issues=dom_issues,
            )

        # -------------------------------------------------------------
        # GATE 17: Text Overflow & Viewport Boundary (Critical)
        # -------------------------------------------------------------
        overflow_issues = [iss for iss in visual_rep.issues if iss.issue_type == "TEXT_OVERFLOW"]
        g17_pass = len(overflow_issues) == 0
        gates.append(
            GateResult(
                gate_id="GATE_17_TEXT_OVERFLOW",
                gate_name="Text Overflow & Viewport Boundary",
                category="Visual",
                status=GateStatus.PASS if g17_pass else GateStatus.REPAIR_REQUIRED,
                passed=g17_pass,
                score=1.0 if g17_pass else 0.0,
                threshold=1.0,
                severity=Severity.CRITICAL,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                affected_slides=[iss.slide_number for iss in overflow_issues],
                details="Zero text bounding box overflows" if g17_pass else f"{len(overflow_issues)} text overflow violations",
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g17_pass:
            blocking_reasons.append(f"Gate 17 Failed: Text overflow detected on {len(overflow_issues)} slides")

        # -------------------------------------------------------------
        # GATE 18: Element Collision Guard (Critical)
        # -------------------------------------------------------------
        collision_issues = [iss for iss in visual_rep.issues if iss.issue_type == "ELEMENT_COLLISION"]
        g18_pass = len(collision_issues) == 0
        gates.append(
            GateResult(
                gate_id="GATE_18_ELEMENT_COLLISION",
                gate_name="Element Collision & Layout Overlap",
                category="Visual",
                status=GateStatus.PASS if g18_pass else GateStatus.REPAIR_REQUIRED,
                passed=g18_pass,
                score=1.0 if g18_pass else 0.0,
                threshold=1.0,
                severity=Severity.CRITICAL,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                affected_slides=[iss.slide_number for iss in collision_issues],
                details="Zero bounding box collisions detected" if g18_pass else f"{len(collision_issues)} element overlaps detected",
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g18_pass:
            blocking_reasons.append(f"Gate 18 Failed: Element collision detected on {len(collision_issues)} slides")

        # -------------------------------------------------------------
        # GATE 19: Tiny Text Threshold (Critical)
        # -------------------------------------------------------------
        tiny_issues = [iss for iss in visual_rep.issues if iss.issue_type == "TINY_TEXT"]
        g19_pass = len(tiny_issues) == 0
        gates.append(
            GateResult(
                gate_id="GATE_19_TINY_TEXT",
                gate_name="Minimum Typography Readability",
                category="Visual",
                status=GateStatus.PASS if g19_pass else GateStatus.REPAIR_REQUIRED,
                passed=g19_pass,
                score=1.0 if g19_pass else 0.0,
                threshold=1.0,
                severity=Severity.CRITICAL,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                affected_slides=[iss.slide_number for iss in tiny_issues],
                details="All typography meets 14pt+ readability threshold" if g19_pass else f"{len(tiny_issues)} slides contain tiny illegible font spans",
                qa_version=artifact_version,
                is_blocking=True,
            )
        )
        if not g19_pass:
            blocking_reasons.append(f"Gate 19 Failed: Tiny text readability violation on {len(tiny_issues)} slides")

        # -------------------------------------------------------------
        # GATE 20: Density Balance (Warning)
        # -------------------------------------------------------------
        g20_pass = visual_rep.density_score >= 0.70
        gates.append(
            GateResult(
                gate_id="GATE_20_DENSITY_BALANCE",
                gate_name="Visual Information Density Balance",
                category="Visual",
                status=GateStatus.PASS if g20_pass else GateStatus.WARNING,
                passed=g20_pass,
                score=visual_rep.density_score,
                threshold=0.70,
                severity=Severity.WARNING,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                details=f"Density balance score: {visual_rep.density_score*100:.1f}%",
                qa_version=artifact_version,
                is_blocking=False,
            )
        )
        if not g20_pass:
            warning_reasons.append(f"Gate 20 Warning: Visual density balance score is {visual_rep.density_score*100:.1f}%")

        # -------------------------------------------------------------
        # GATE 21: Intentional Whitespace Quality (Warning)
        # -------------------------------------------------------------
        ws_score = getattr(visual_rep, "composition_score", 1.0)
        g21_pass = ws_score >= 0.70
        gates.append(
            GateResult(
                gate_id="GATE_21_WHITESPACE_QUALITY",
                gate_name="Intentional Whitespace Quality",
                category="Visual",
                status=GateStatus.PASS if g21_pass else GateStatus.WARNING,
                passed=g21_pass,
                score=ws_score,
                threshold=0.70,
                severity=Severity.WARNING,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                details=f"Whitespace score: {ws_score*100:.1f}%",
                qa_version=artifact_version,
                is_blocking=False,
            )
        )
        if not g21_pass:
            warning_reasons.append(f"Gate 21 Warning: Whitespace score is {ws_score*100:.1f}%")

        # -------------------------------------------------------------
        # GATE 22: Visual Typography Hierarchy (Warning)
        # -------------------------------------------------------------
        g22_pass = visual_rep.hierarchy_score >= 0.75
        gates.append(
            GateResult(
                gate_id="GATE_22_VISUAL_HIERARCHY",
                gate_name="Visual Typography Hierarchy",
                category="Visual",
                status=GateStatus.PASS if g22_pass else GateStatus.WARNING,
                passed=g22_pass,
                score=visual_rep.hierarchy_score,
                threshold=0.75,
                severity=Severity.WARNING,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                details=f"Visual hierarchy score: {visual_rep.hierarchy_score*100:.1f}%",
                qa_version=artifact_version,
                is_blocking=False,
            )
        )
        if not g22_pass:
            warning_reasons.append(f"Gate 22 Warning: Visual hierarchy score is {visual_rep.hierarchy_score*100:.1f}%")

        # -------------------------------------------------------------
        # GATE 23: Composition Repetition Streak Guard (Warning)
        # -------------------------------------------------------------
        streak_limit = 3
        max_streak = 1
        curr_streak = 1
        for i in range(len(slides) - 1):
            if slides[i].layout == slides[i + 1].layout:
                curr_streak += 1
                if curr_streak > max_streak:
                    max_streak = curr_streak
            else:
                curr_streak = 1

        g23_pass = max_streak <= streak_limit
        gates.append(
            GateResult(
                gate_id="GATE_23_COMPOSITION_REPETITION",
                gate_name="Composition Layout Streak Guard",
                category="Presentation",
                status=GateStatus.PASS if g23_pass else GateStatus.WARNING,
                passed=g23_pass,
                score=float(max_streak),
                threshold=float(streak_limit),
                severity=Severity.WARNING,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                details=f"Max identical layout streak: {max_streak} (limit <= {streak_limit})",
                qa_version=artifact_version,
                is_blocking=False,
            )
        )
        if not g23_pass:
            warning_reasons.append(f"Gate 23 Warning: {max_streak} consecutive slides share the exact same layout")

        # -------------------------------------------------------------
        # GATE 24: Card Overload Guard (Warning)
        # -------------------------------------------------------------
        card_overload_slides = [
            s.slide_number for s in slides if s.layout == "concept_card" and len(s.source_refs) > 4
        ]
        g24_pass = len(card_overload_slides) == 0
        gates.append(
            GateResult(
                gate_id="GATE_24_CARD_OVERLOAD",
                gate_name="Card Overload Guard",
                category="Visual",
                status=GateStatus.PASS if g24_pass else GateStatus.WARNING,
                passed=g24_pass,
                score=1.0 if g24_pass else 0.0,
                threshold=1.0,
                severity=Severity.WARNING,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                affected_slides=card_overload_slides,
                details="Zero overloaded generic cards" if g24_pass else f"{len(card_overload_slides)} slides overloaded with cards",
                qa_version=artifact_version,
                is_blocking=False,
            )
        )
        if not g24_pass:
            warning_reasons.append(f"Gate 24 Warning: {len(card_overload_slides)} slides contain card overload")

        # -------------------------------------------------------------
        # GATE 25: Slide Cadence & Rhythm (Warning)
        # -------------------------------------------------------------
        rhythm_res = self.rhythm_analyzer.analyze(plan.slides)
        g25_pass = rhythm_res.status != "POOR" and rhythm_res.rhythm_score >= 0.70
        gates.append(
            GateResult(
                gate_id="GATE_25_SLIDE_RHYTHM",
                gate_name="Presentation Cadence & Rhythm",
                category="Presentation",
                status=GateStatus.PASS if g25_pass else GateStatus.WARNING,
                passed=g25_pass,
                score=rhythm_res.rhythm_score,
                threshold=0.70,
                severity=Severity.WARNING,
                repairability=Repairability.DETERMINISTIC_REPAIRABLE,
                details=f"Cadence score: {rhythm_res.rhythm_score*100:.1f}%, {len(rhythm_res.issues)} pacing warnings",
                qa_version=artifact_version,
                is_blocking=False,
            )
        )
        if not g25_pass:
            warning_reasons.append(f"Gate 25 Warning: Presentation rhythm score is {rhythm_res.rhythm_score*100:.1f}%")

        # Summarize authoritative QualityRound
        passed_count = sum(1 for g in gates if g.passed)
        failed_count = len(gates) - passed_count
        warning_count = sum(1 for g in gates if g.status == GateStatus.WARNING)
        critical_count = sum(1 for g in gates if g.status in (GateStatus.CRITICAL_FAILURE, GateStatus.BLOCKED))
        repairable_count = sum(1 for g in gates if g.status == GateStatus.REPAIR_REQUIRED)
        overall_passed = len(blocking_reasons) == 0

        # Mean score across all gates
        overall_score = round(sum(g.score for g in gates) / len(gates), 3) if gates else 1.0

        return QualityRound(
            round_id=round_id,
            artifact_version=artifact_version,
            total_gates=len(gates),
            passed_gates=passed_count,
            failed_gates=failed_count,
            warning_gates=warning_count,
            critical_failures=critical_count,
            repairable_failures=repairable_count,
            gate_results=gates,
            critical_coverage=round(crit_coverage, 3),
            important_coverage=round(imp_coverage, 3),
            duplicate_rate=round(dup_rate, 3),
            layout_entropy=plan.layout_entropy,
            hallucination_count=hallucination_warnings,
            grounding_score=grounding_report.grounding_score,
            visual_score=visual_rep.overall_score,
            narrative_score=arch_scores.narrative_progression,
            rhythm_score=rhythm_res.rhythm_score,
            overall_score=overall_score,
            overall_passed=overall_passed,
            export_blocked=not overall_passed,
            blocking_reasons=blocking_reasons,
            warning_reasons=warning_reasons,
        )
