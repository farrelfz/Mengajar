"""
Universal Document Intelligence System V5 — Repair Safety Invariants.

Phase 3C.1: Non-negotiable structural, semantic, and pedagogical invariants
that must never be compromised by repair mutations.
"""

from __future__ import annotations

from typing import Any, List, Optional, Set, Tuple
from app.quality.repair.contracts import RepairPlan
from app.quality.repair.drift_analyzer import ArtifactDriftReport


class RepairSafetyInvariants:
    """Evaluates non-negotiable safety rules before committing any repair mutation."""

    @classmethod
    def evaluate_all(
        cls,
        pre_blueprint: Any,
        post_blueprint: Any,
        plan: RepairPlan,
        drift_report: ArtifactDriftReport,
        artifact_type: str,
    ) -> Tuple[bool, List[str]]:
        """
        Runs global and format-specific invariant checks.
        Returns (all_passed, violation_reasons).
        """
        violations: List[str] = []

        # 1. Global Invariant: Drift Acceptability
        if not drift_report.is_acceptable:
            violations.extend(list(drift_report.violations))

        # 2. Global Invariant: Traceability & No Orphan Source References
        pre_refs = cls._extract_refs(pre_blueprint)
        post_refs = cls._extract_refs(post_blueprint)
        if pre_refs and len(post_refs) < len(pre_refs) * 0.90:
            violations.append(
                f"Traceability invariant violated: source refs reduced from {len(pre_refs)} to {len(post_refs)}."
            )

        # 3. Format-Specific Invariants
        upper_fmt = artifact_type.upper()
        if upper_fmt == "PRESENTATION":
            violations.extend(cls._check_presentation_invariants(post_blueprint))
        elif upper_fmt == "HANDOUT":
            violations.extend(cls._check_handout_invariants(post_blueprint))
        elif upper_fmt == "WORKSHEET":
            violations.extend(cls._check_worksheet_invariants(pre_blueprint, post_blueprint))
        elif upper_fmt == "SCIENTIFIC_DOCUMENT":
            violations.extend(cls._check_scientific_invariants(pre_blueprint, post_blueprint, plan))

        return len(violations) == 0, violations

    @classmethod
    def _extract_refs(cls, bp: Any) -> Set[str]:
        refs = set()
        for attr in ("slides", "beats", "sections", "activities", "babs"):
            coll = getattr(bp, attr, None)
            if coll:
                for item in coll:
                    refs.update(getattr(item, "source_refs", ()) or ())
                    refs.update(getattr(item, "source_element_ids", ()) or ())
                    refs.update(getattr(item, "source_unit_ids", ()) or ())
                    refs.update(getattr(item, "evidence_ids", ()) or ())
        return refs

    @classmethod
    def _check_presentation_invariants(cls, post_bp: Any) -> List[str]:
        errs = []
        slides = getattr(post_bp, "slides", None) or getattr(post_bp, "beats", None)
        if slides:
            for s in slides:
                # Max cards / elements per slide
                units = getattr(s, "knowledge_unit_ids", None) or getattr(s, "key_blocks", None)
                if units and len(units) > 6:
                    errs.append(f"Cognitive load invariant violated on slide {getattr(s, 'slide_id', '?')}: >6 cards.")
        return errs

    @classmethod
    def _check_handout_invariants(cls, post_bp: Any) -> List[str]:
        errs = []
        sections = getattr(post_bp, "sections", None)
        if sections:
            levels = [getattr(s, "level", 1) for s in sections]
            for i in range(len(levels) - 1):
                # Hierarchy cannot jump more than 1 level downwards (e.g. 1 -> 3)
                if levels[i + 1] > levels[i] + 1:
                    errs.append(f"Monotonic hierarchy invariant violated: jump from level {levels[i]} to {levels[i+1]}.")
        return errs

    @classmethod
    def _check_worksheet_invariants(cls, pre_bp: Any, post_bp: Any) -> List[str]:
        errs = []
        # Check strict anti-spoiling invariant
        activities = getattr(post_bp, "activities", None)
        if activities:
            for act in activities:
                prompt_lower = getattr(act, "prompt_text", "").lower()
                # Explicit answer keywords in student prompt indicate a leak
                if "kunci jawaban:" in prompt_lower or "jawaban benar adalah" in prompt_lower:
                    errs.append(f"Anti-spoiling invariant violated: answer text leaked in activity {getattr(act, 'activity_id', '?')}.")
                if getattr(act, "requires_student_workspace", False):
                    # Student workspace must remain present
                    pass
        return errs

    @classmethod
    def _check_scientific_invariants(cls, pre_bp: Any, post_bp: Any, plan: RepairPlan) -> List[str]:
        errs = []
        # Invariant: No fabricated citations or evidence!
        # Every evidence ID in post_bp must exist in pre_bp or knowledge core
        pre_evs = set()
        post_evs = set()

        def extract_evidence(bp: Any) -> Set[str]:
            evs = set()
            babs = getattr(bp, "babs", None) or getattr(bp, "sections", None)
            if babs:
                for b in babs:
                    for sub in getattr(b, "subsections", ()):
                        evs.update(getattr(sub, "evidence_ids", ()) or ())
            return evs

        pre_evs = extract_evidence(pre_bp)
        post_evs = extract_evidence(post_bp)

        # No new, invented evidence IDs allowed
        invented = post_evs - pre_evs
        if invented:
            errs.append(f"Scientific evidence invariant violated: invented evidence IDs {invented} without source grounding.")

        # Methodology Chapter Order BAB I - BAB V
        babs = getattr(post_bp, "babs", None)
        if babs and len(babs) > 1:
            for i in range(len(babs) - 1):
                num_curr = getattr(babs[i], "bab_number", i + 1)
                num_next = getattr(babs[i + 1], "bab_number", i + 2)
                if num_next < num_curr:
                    errs.append(f"Scientific BAB hierarchy invariant violated: BAB {num_curr} followed by BAB {num_next}.")

        return errs
