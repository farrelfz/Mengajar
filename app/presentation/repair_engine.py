"""
Deterministic Repair & Refinement Engine (Task 10).

Executes deterministic local repairs with:
- Root Cause Classification
- Slide Deduplication & Coverage-Preserving Merging (Gate 5)
- Claim Provenance & Text Softening Repair (Gate 11)
- Canonical Semantic Layout Remapping via Visual Grammar Matrix (Gate 16)
- Typography, Density, and Grid Reflow (Gates 17, 18, 19, 24)
- Convergence Analysis (Attempted vs Successful, Stagnation, Rollback on Divergence)
"""

from __future__ import annotations

import re
import copy
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.presentation.slide_architect import PlannedSlide, SlidePlan
from app.presentation.semantic_layout_validator import LayoutAlignmentResult
from app.presentation.visual_qa import VisualQualityReport, VisualIssue
from app.presentation.visual_grammar_registry import VISUAL_GRAMMAR_MATRIX
from app.intelligence.content_manifest import ContentManifest


class RepairAction(BaseModel):
    slide_number: int
    issue_type: str
    repair_class: str  # "CLASS_A", "CLASS_B", "CLASS_C", "CLASS_D"
    action: str
    before: dict[str, Any]
    after: dict[str, Any]
    notes: str


class RepairResult(BaseModel):
    success: bool
    iterations: int
    max_iterations: int = 2
    attempted: int = 0
    successful: int = 0
    failed: int = 0
    actions_performed: list[RepairAction] = Field(default_factory=list)
    repaired_slide_ids: list[str] = Field(default_factory=list)
    remaining_critical_issues: list[str] = Field(default_factory=list)
    mutated_artifacts: list[str] = Field(default_factory=list)


class RepairConvergenceReport(BaseModel):
    round_before: int
    round_after: int
    failures_before: int
    failures_after: int
    critical_before: int
    critical_after: int
    resolved_failures: list[str] = Field(default_factory=list)
    unresolved_failures: list[str] = Field(default_factory=list)
    newly_introduced_failures: list[str] = Field(default_factory=list)
    score_delta: float = 0.0
    converged: bool = False
    stagnated: bool = False
    diverged: bool = False
    should_rollback: bool = False


class RepairConvergenceAnalyzer:
    """Calculates improvement delta across QualityRounds and detects non-convergence."""

    @classmethod
    def analyze_convergence(
        cls,
        round_before: Any,
        round_after: Any,
    ) -> RepairConvergenceReport:
        b_gates = {g.gate_id: g for g in getattr(round_before, "gate_results", [])}
        a_gates = {g.gate_id: g for g in getattr(round_after, "gate_results", [])}

        b_failed = {g_id for g_id, g in b_gates.items() if not g.passed}
        a_failed = {g_id for g_id, g in a_gates.items() if not g.passed}

        resolved = list(b_failed - a_failed)
        unresolved = list(b_failed & a_failed)
        newly_introduced = list(a_failed - b_failed)

        crit_before = getattr(round_before, "critical_failures", 0)
        crit_after = getattr(round_after, "critical_failures", 0)

        score_b = getattr(round_before, "overall_score", 0.0)
        score_a = getattr(round_after, "overall_score", 0.0)
        score_delta = round(score_a - score_b, 3)

        # Divergence check: repair introduced more critical failures
        diverged = crit_after > crit_before or len(newly_introduced) > len(resolved)
        stagnated = (crit_before == crit_after) and (len(resolved) == 0)
        converged = (crit_after == 0) and (getattr(round_after, "overall_passed", False))

        return RepairConvergenceReport(
            round_before=getattr(round_before, "round_id", 1),
            round_after=getattr(round_after, "round_id", 2),
            failures_before=len(b_failed),
            failures_after=len(a_failed),
            critical_before=crit_before,
            critical_after=crit_after,
            resolved_failures=resolved,
            unresolved_failures=unresolved,
            newly_introduced_failures=newly_introduced,
            score_delta=score_delta,
            converged=converged,
            stagnated=stagnated,
            diverged=diverged,
            should_rollback=diverged,
        )


class SlideDeduplicationPlanner:
    """Plans and executes deduplication and coverage-preserving merging of redundant slides."""

    @classmethod
    def deduplicate(
        cls,
        plan: SlidePlan,
        redundant_slide_numbers: list[int],
        manifest: Optional[ContentManifest] = None,
    ) -> list[RepairAction]:
        if not redundant_slide_numbers:
            return []

        actions: list[RepairAction] = []
        redundant_set = set(redundant_slide_numbers)
        remaining_slides: list[PlannedSlide] = []
        slide_map = {s.slide_number: s for s in plan.slides}

        for s in plan.slides:
            if s.slide_number in redundant_set:
                # Identify predecessor candidate to receive any unmerged source references
                predecessors = [
                    p for p in remaining_slides
                    if p.primary_concept == s.primary_concept or p.act_name == s.act_name
                ]
                target_slide = predecessors[-1] if predecessors else (remaining_slides[-1] if remaining_slides else None)

                merged_refs = []
                if target_slide:
                    for ref in s.source_refs:
                        if ref not in target_slide.source_refs:
                            target_slide.source_refs.append(ref)
                            merged_refs.append(ref)
                    # Merge unique key blocks
                    existing_bids = {b.id for b in target_slide.key_blocks}
                    for b in s.key_blocks:
                        if b.id not in existing_bids:
                            target_slide.key_blocks.append(b)

                actions.append(
                    RepairAction(
                        slide_number=s.slide_number,
                        issue_type="DUPLICATE_SLIDE",
                        repair_class="CLASS_C",
                        action="deduplicate_and_merge",
                        before={"title": s.title, "layout": s.layout, "source_refs": s.source_refs},
                        after={"merged_into": target_slide.slide_number if target_slide else None, "merged_refs": merged_refs},
                        notes=f"Deduplicated redundant Slide {s.slide_number} ('{s.title}'), safely merging source coverage into Slide {target_slide.slide_number if target_slide else 'None'}",
                    )
                )
            else:
                remaining_slides.append(s)

        # Re-index remaining slides to maintain strictly contiguous slide numbering
        for idx, s in enumerate(remaining_slides, start=1):
            s.slide_number = idx

        plan.slides = remaining_slides
        return actions


class ClaimProvenanceRepairer:
    """Repairs unsupported claims via provenance updates, softening exaggerations, or removals."""

    EXAGGERATION_REPLACEMENTS = [
        (re.compile(r"\b100%\s+aman\b", re.I), "aman dalam pengawasan ketat"),
        (re.compile(r"\btanpa\s+risiko\s+sama\s+sekali\b", re.I), "dengan mitigasi risiko yang ketat"),
        (re.compile(r"\bmustahil\s+terbakar\b", re.I), "sangat tahan panas dalam kondisi wajar"),
        (re.compile(r"\bcompletely\s+prevents\b", re.I), "effectively reduces"),
        (re.compile(r"\bcompletely\s+eliminates\b", re.I), "significantly minimizes"),
    ]

    @classmethod
    def repair(
        cls,
        plan: SlidePlan,
        unsupported_claims: list[dict[str, Any]],
    ) -> list[RepairAction]:
        actions: list[RepairAction] = []
        slide_map = {s.slide_number: s for s in plan.slides}

        for u in unsupported_claims:
            s_num_val = u.get("slide")
            if s_num_val is None:
                continue
            s_num = int(s_num_val)
            slide = slide_map.get(s_num)
            if not slide:
                continue

            claim_id = str(u.get("claim_id", ""))
            repair_action = u.get("repair_action", "update_provenance")
            best_match = u.get("independent_best_source_match", [])

            matching_claim = next((c for c in slide.claim_units if c.claim_id == claim_id), None)

            if repair_action == "update_provenance" and best_match:
                # Add missing source blocks to slide provenance
                for ref in best_match:
                    if ref not in slide.source_refs:
                        slide.source_refs.append(ref)
                if matching_claim:
                    for ref in best_match:
                        if ref not in matching_claim.source_refs:
                            matching_claim.source_refs.append(ref)
                    matching_claim.support_level = "DIRECT_SUPPORT"

                actions.append(
                    RepairAction(
                        slide_number=s_num,
                        issue_type="UNSUPPORTED_CLAIM_PROVENANCE",
                        repair_class="CLASS_B",
                        action="update_source_provenance",
                        before={"claim_id": claim_id, "source_refs": u.get("declared_source_refs", [])},
                        after={"linked_blocks": best_match, "new_source_refs": slide.source_refs},
                        notes=f"Linked ground truth evidence {best_match} to claim {claim_id} on Slide {s_num}",
                    )
                )

            elif repair_action == "soften_exaggeration" and matching_claim:
                old_text = matching_claim.text
                new_text = old_text
                for pat, repl in cls.EXAGGERATION_REPLACEMENTS:
                    new_text = pat.sub(repl, new_text)

                if new_text != old_text:
                    matching_claim.text = new_text
                    matching_claim.support_level = "PARAPHRASE_SUPPORT"
                    actions.append(
                        RepairAction(
                            slide_number=s_num,
                            issue_type="UNSUPPORTED_EXAGGERATION",
                            repair_class="CLASS_B",
                            action="soften_claim_exaggeration",
                            before={"text": old_text},
                            after={"text": new_text},
                            notes=f"Softened ungrounded absolute claim on Slide {s_num}",
                        )
                    )

            elif repair_action == "remove_claim" and matching_claim:
                slide.claim_units = [c for c in slide.claim_units if c.claim_id != claim_id]
                actions.append(
                    RepairAction(
                        slide_number=s_num,
                        issue_type="FABRICATED_CLAIM",
                        repair_class="CLASS_B",
                        action="remove_ungrounded_claim",
                        before={"claim_id": claim_id, "text": matching_claim.text},
                        after={"removed": True},
                        notes=f"Removed ungrounded/fabricated claim {claim_id} from Slide {s_num}",
                    )
                )

        return actions


class DeterministicRepairEngine:
    """Master Deterministic Repair Engine for Task 10."""

    MAX_REPAIR_ITERATIONS = 2

    def repair(
        self,
        plan: SlidePlan,
        visual_report: Optional[VisualQualityReport] = None,
        semantic_report: Optional[LayoutAlignmentResult] = None,
        quality_round: Optional[Any] = None,
        manifest: Optional[ContentManifest] = None,
        iteration: int = 1,
    ) -> RepairResult:
        """Applies comprehensive deterministic repairs across all reported gate failures."""
        if iteration > self.MAX_REPAIR_ITERATIONS:
            return RepairResult(
                success=False,
                iterations=iteration - 1,
                attempted=0,
                successful=0,
                failed=0,
                remaining_critical_issues=["Repair budget exhausted (MAX_REPAIR_ITERATIONS reached)"],
            )

        attempted = 0
        actions: list[RepairAction] = []
        slide_map = {s.slide_number: s for s in plan.slides}
        mutated_artifacts: set[str] = set()

        # -------------------------------------------------------------
        # 1. REPAIR GATE 5: Duplicate Slides (Class C)
        # -------------------------------------------------------------
        redundant_slides: list[int] = []
        if quality_round:
            for g in quality_round.gate_results:
                if g.gate_id == "GATE_5_DUPLICATES" and not g.passed:
                    redundant_slides = g.affected_slides

        if redundant_slides:
            attempted += len(redundant_slides)
            dedup_actions = SlideDeduplicationPlanner.deduplicate(
                plan=plan,
                redundant_slide_numbers=redundant_slides,
                manifest=manifest,
            )
            actions.extend(dedup_actions)
            if dedup_actions:
                mutated_artifacts.add("blueprint")
                # Refresh slide_map after deduplication re-indexing
                slide_map = {s.slide_number: s for s in plan.slides}

        # -------------------------------------------------------------
        # 2. REPAIR GATE 11: Claim Grounding & Provenance (Class B)
        # -------------------------------------------------------------
        unsupported_claims: list[dict[str, Any]] = []
        if quality_round:
            for g in quality_round.gate_results:
                if g.gate_id == "GATE_11_CLAIM_GROUNDING" and not g.passed:
                    unsupported_claims = g.evidence.get("unsupported_claims", [])

        if unsupported_claims:
            attempted += len(unsupported_claims)
            claim_actions = ClaimProvenanceRepairer.repair(
                plan=plan,
                unsupported_claims=unsupported_claims,
            )
            actions.extend(claim_actions)
            if claim_actions:
                mutated_artifacts.add("blueprint")

        # -------------------------------------------------------------
        # 3. REPAIR GATE 16: Semantic Layout Mismatch (Class B)
        # -------------------------------------------------------------
        violations = []
        if semantic_report and semantic_report.violations:
            violations = semantic_report.violations
        elif quality_round:
            for g in quality_round.gate_results:
                if g.gate_id == "GATE_16_SEMANTIC_LAYOUT_ALIGNMENT" and not g.passed:
                    violations = g.evidence.get("violations", [])

        if violations:
            for viol in violations:
                attempted += 1
                s_num = viol["slide_number"]
                slide = slide_map.get(s_num)
                if not slide:
                    continue

                old_layout = slide.layout
                role = slide.narrative_function.upper()
                rule = VISUAL_GRAMMAR_MATRIX.get(role, {})
                preferred_layouts = rule.get("preferred", ["two_column"])

                # Select preferred layout that differs from old avoided layout
                new_layout = preferred_layouts[0]
                if new_layout == old_layout and len(preferred_layouts) > 1:
                    new_layout = preferred_layouts[1]

                if new_layout != old_layout:
                    slide.layout = new_layout
                    mutated_artifacts.add("blueprint")
                    actions.append(
                        RepairAction(
                            slide_number=s_num,
                            issue_type="SEMANTIC_LAYOUT_MISMATCH",
                            repair_class="CLASS_B",
                            action="layout_remap",
                            before={"layout": old_layout, "role": role},
                            after={"layout": new_layout},
                            notes=f"Remapped Slide {s_num} from '{old_layout}' to canonical preferred layout '{new_layout}' for role {role}",
                        )
                    )

        # -------------------------------------------------------------
        # 4. REPAIR CLASS A: Visual QA Issues (Overflow, Collision, Tiny Text)
        # -------------------------------------------------------------
        if visual_report:
            for issue in visual_report.issues:
                attempted += 1
                s_num = issue.slide_number
                slide = slide_map.get(s_num)
                if not slide:
                    continue

                if issue.issue_type == "TEXT_OVERFLOW":
                    old_density = slide.text_density
                    old_layout = slide.layout
                    new_layout = "two_column" if old_layout == "concept_card" else old_layout
                    slide.text_density = "high"
                    slide.layout = new_layout
                    mutated_artifacts.add("blueprint")
                    actions.append(
                        RepairAction(
                            slide_number=s_num,
                            issue_type="TEXT_OVERFLOW",
                            repair_class="CLASS_A",
                            action="grid_reflow_and_compression",
                            before={"text_density": old_density, "layout": old_layout},
                            after={"text_density": "high", "layout": new_layout},
                            notes=f"Reflowed grid and increased text density to resolve text overflow on Slide {s_num}",
                        )
                    )

                elif issue.issue_type == "TINY_TEXT":
                    old_density = slide.text_density
                    slide.text_density = "low"
                    mutated_artifacts.add("blueprint")
                    actions.append(
                        RepairAction(
                            slide_number=s_num,
                            issue_type="TINY_TEXT",
                            repair_class="CLASS_A",
                            action="enlarge_base_typography",
                            before={"text_density": old_density},
                            after={"text_density": "low"},
                            notes=f"Set density to low on Slide {s_num} to enforce readable 14pt+ typography",
                        )
                    )

                elif issue.issue_type == "CARD_OVERLOAD":
                    old_layout = slide.layout
                    new_layout = "three_column_comparison" if len(slide.key_blocks) <= 3 else "two_column"
                    slide.layout = new_layout
                    mutated_artifacts.add("blueprint")
                    actions.append(
                        RepairAction(
                            slide_number=s_num,
                            issue_type="CARD_OVERLOAD",
                            repair_class="CLASS_A",
                            action="card_restructure",
                            before={"layout": old_layout},
                            after={"layout": new_layout},
                            notes=f"Restructured card layout on Slide {s_num} to avoid generic card overload",
                        )
                    )

        successful_count = len(actions)
        failed_count = max(0, attempted - successful_count)
        repaired_ids = [f"slide-{act.slide_number}" for act in actions]

        return RepairResult(
            success=successful_count > 0,
            iterations=iteration,
            max_iterations=self.MAX_REPAIR_ITERATIONS,
            attempted=attempted,
            successful=successful_count,
            failed=failed_count,
            actions_performed=actions,
            repaired_slide_ids=repaired_ids,
            remaining_critical_issues=[],
            mutated_artifacts=sorted(list(mutated_artifacts)),
        )
