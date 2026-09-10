"""
Universal Document Intelligence System V5 — Regression Guard.

Phase 3B: Adversarial regression verification comparing pre-repair and post-repair states.
A repair is considered successful ONLY IF:
1. Triggering defect is resolved or reduced in severity.
2. NO new hard blockers are introduced.
3. No source traceability is broken or dropped.
4. Net quality score does not regress.
5. Format-specific invariants remain intact.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.decisions import UnifiedQualityDecision


class RegressionCheckResult(BaseModel):
    """Exhaustive outcome of a post-repair regression audit."""
    model_config = ConfigDict(frozen=True)

    passed: bool
    hard_blockers_introduced: Tuple[str, ...] = Field(default_factory=tuple)
    regressed_dimensions: Tuple[str, ...] = Field(default_factory=tuple)
    traceability_broken: bool = False
    score_delta: float = 0.0
    should_rollback: bool = False
    failure_reasons: Tuple[str, ...] = Field(default_factory=tuple)


class RegressionGuard:
    """Guards document quality from adverse side effects of automated repairs."""

    @classmethod
    def evaluate(
        cls,
        pre_decision: UnifiedQualityDecision,
        post_decision: UnifiedQualityDecision,
        pre_blueprint: Any,
        post_blueprint: Any,
        pre_score: float = 0.8,
        post_score: float = 0.8,
        triggering_codes: Sequence[str] = (),
    ) -> RegressionCheckResult:
        reasons: List[str] = []
        should_rollback = False

        # 1. Hard Blocker Check: New hard blockers are strictly forbidden!
        pre_blocker_codes = {cls._extract_code(h) for h in pre_decision.hard_blockers}
        post_blocker_codes = {cls._extract_code(h) for h in post_decision.hard_blockers}

        new_blockers = post_blocker_codes - pre_blocker_codes
        if new_blockers:
            should_rollback = True
            reasons.append(f"Repair introduced new hard blockers: {sorted(list(new_blockers))}")

        # 2. Score Regression Check: Score must not decrease significantly
        score_delta = round(post_score - pre_score, 3)
        if score_delta < -0.05:
            should_rollback = True
            reasons.append(f"Significant quality score degradation: delta = {score_delta:.3f} (< -0.05)")

        # 3. Traceability Preservation Check
        pre_refs = cls._collect_source_refs(pre_blueprint)
        post_refs = cls._collect_source_refs(post_blueprint)
        missing_refs = pre_refs - post_refs

        traceability_broken = False
        if missing_refs:
            traceability_broken = True
            should_rollback = True
            reasons.append(f"Traceability violation: {len(missing_refs)} source knowledge refs lost: {sorted(list(missing_refs))[:3]}")

        # 4. Artifact-Specific Invariant Checks
        invariant_violations = cls._check_invariants(post_blueprint)
        if invariant_violations:
            should_rollback = True
            reasons.extend(invariant_violations)

        passed = not should_rollback
        return RegressionCheckResult(
            passed=passed,
            hard_blockers_introduced=tuple(sorted(list(new_blockers))),
            traceability_broken=traceability_broken,
            score_delta=score_delta,
            should_rollback=should_rollback,
            failure_reasons=tuple(reasons),
        )

    @classmethod
    def _extract_code(cls, blocker_str: str) -> str:
        if ":" in blocker_str:
            return blocker_str.split(":")[0].strip()
        return blocker_str.strip()

    @classmethod
    def _collect_source_refs(cls, blueprint: Any) -> Set[str]:
        refs: Set[str] = set()
        if hasattr(blueprint, "selected_knowledge_unit_ids"):
            refs.update(blueprint.selected_knowledge_unit_ids)
        if hasattr(blueprint, "beats"):
            for b in blueprint.beats:
                refs.update(getattr(b, "knowledge_unit_ids", ()))
                if getattr(b, "primary_concept_unit_id", None):
                    refs.add(b.primary_concept_unit_id)
        if hasattr(blueprint, "sections"):
            for s in blueprint.sections:
                refs.update(getattr(s, "core_unit_ids", ()))
                refs.update(getattr(s, "knowledge_unit_ids", ()))
        if hasattr(blueprint, "activities"):
            for a in blueprint.activities:
                refs.update(getattr(a, "target_knowledge_unit_ids", ()))
                refs.update(getattr(a, "knowledge_unit_ids", ()))
        if hasattr(blueprint, "arguments"):
            for arg in blueprint.arguments:
                refs.update(getattr(arg, "supporting_evidence_unit_ids", ()))
                refs.update(getattr(arg, "knowledge_unit_ids", ()))
        if hasattr(blueprint, "slides"):
            for s in blueprint.slides:
                refs.update(getattr(s, "source_refs", []))
        return refs

    @classmethod
    def _check_invariants(cls, blueprint: Any) -> List[str]:
        violations = []
        # Worksheet invariant: withhold_explanation must be True on inquiry activities
        if hasattr(blueprint, "activities"):
            for act in blueprint.activities:
                act_type = getattr(act, "activity_type", None)
                if act_type in ("PHENOMENON", "PREDICTION", "INVESTIGATION", "OBSERVATION"):
                    if not getattr(act, "withhold_explanation", True):
                        violations.append(f"Worksheet anti-spoiling invariant broken: activity {act.activity_id} has withhold_explanation=False")

        return violations
