"""
Universal Document Intelligence System V5 — Canonical Quality Decision Router.

Phase 3D: Deterministic routing of UnifiedQualityAuthority decisions.
THE ORCHESTRATOR MUST NEVER BECOME A SECOND QUALITY AUTHORITY.
Zero independent scoring, zero threshold inventing, zero overriding of hard blockers.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, Tuple

from app.quality.contracts.authority import UnifiedQualityReport
from app.quality.contracts.decisions import ExportDecision


class DecisionRouteAction(str, Enum):
    """Authoritative downstream action dictated by the Quality Authority decision."""
    PROCEED_TO_EXPORT = "PROCEED_TO_EXPORT"
    PROCEED_TO_EXPORT_WITH_WARNINGS = "PROCEED_TO_EXPORT_WITH_WARNINGS"
    TRIGGER_TARGETED_REPAIR = "TRIGGER_TARGETED_REPAIR"
    TRIGGER_RENDER_REPAIR = "TRIGGER_RENDER_REPAIR"
    TRIGGER_SEMANTIC_REPAIR = "TRIGGER_SEMANTIC_REPAIR"
    HALT_MANUAL_REVIEW = "HALT_MANUAL_REVIEW"
    HALT_BLOCKED = "HALT_BLOCKED"


@dataclass(frozen=True)
class QualityRoutingInstruction:
    """Immutable routing instruction derived strictly from a UnifiedQualityReport."""
    action: DecisionRouteAction
    can_export: bool
    repair_required: bool
    manual_review_required: bool
    is_terminal: bool
    hard_blockers: Tuple[str, ...]
    warnings: Tuple[str, ...]
    rationale: str


class QualityDecisionRouter:
    """Maps UnifiedQualityReport outcomes directly to canonical orchestration actions."""

    @classmethod
    def route_decision(cls, report: UnifiedQualityReport) -> QualityRoutingInstruction:
        """Evaluates canonical decision without calculating or overriding quality scores."""
        dec = report.decision

        if dec == ExportDecision.EXPORT_APPROVED:
            return QualityRoutingInstruction(
                action=DecisionRouteAction.PROCEED_TO_EXPORT,
                can_export=True,
                repair_required=False,
                manual_review_required=False,
                is_terminal=True,
                hard_blockers=report.hard_blockers,
                warnings=report.warnings,
                rationale=report.summary or "Export unconditionally approved by Quality Authority.",
            )

        elif dec == ExportDecision.EXPORT_APPROVED_WITH_WARNINGS:
            return QualityRoutingInstruction(
                action=DecisionRouteAction.PROCEED_TO_EXPORT_WITH_WARNINGS,
                can_export=True,
                repair_required=False,
                manual_review_required=False,
                is_terminal=True,
                hard_blockers=report.hard_blockers,
                warnings=report.warnings,
                rationale=report.summary or "Export approved with warnings attached.",
            )

        elif dec == ExportDecision.REPAIR_REQUIRED:
            return QualityRoutingInstruction(
                action=DecisionRouteAction.TRIGGER_TARGETED_REPAIR,
                can_export=False,
                repair_required=True,
                manual_review_required=False,
                is_terminal=False,
                hard_blockers=report.hard_blockers,
                warnings=report.warnings,
                rationale=report.summary or "Targeted repair required to address quality findings.",
            )

        elif dec == ExportDecision.RENDER_REPAIR_REQUIRED:
            return QualityRoutingInstruction(
                action=DecisionRouteAction.TRIGGER_RENDER_REPAIR,
                can_export=False,
                repair_required=True,
                manual_review_required=False,
                is_terminal=False,
                hard_blockers=report.hard_blockers,
                warnings=report.warnings,
                rationale=report.summary or "Physical render / layout repair required at lowest possible layer.",
            )

        elif dec == ExportDecision.SEMANTIC_REPAIR_REQUIRED:
            return QualityRoutingInstruction(
                action=DecisionRouteAction.TRIGGER_SEMANTIC_REPAIR,
                can_export=False,
                repair_required=True,
                manual_review_required=False,
                is_terminal=False,
                hard_blockers=report.hard_blockers,
                warnings=report.warnings,
                rationale=report.summary or "Semantic structure or claim repair required at blueprint layer.",
            )

        elif dec == ExportDecision.MANUAL_REVIEW_REQUIRED:
            return QualityRoutingInstruction(
                action=DecisionRouteAction.HALT_MANUAL_REVIEW,
                can_export=False,
                repair_required=False,
                manual_review_required=True,
                is_terminal=True,
                hard_blockers=report.hard_blockers,
                warnings=report.warnings,
                rationale=report.summary or "Document flagged for manual editorial review; auto-export forbidden.",
            )

        elif dec == ExportDecision.BLOCKED:
            if report.repair_required:
                return QualityRoutingInstruction(
                    action=DecisionRouteAction.TRIGGER_TARGETED_REPAIR,
                    can_export=False,
                    repair_required=True,
                    manual_review_required=False,
                    is_terminal=False,
                    hard_blockers=report.hard_blockers,
                    warnings=report.warnings,
                    rationale=report.summary or "Export blocked; targeted repair required.",
                )
            else:
                return QualityRoutingInstruction(
                    action=DecisionRouteAction.HALT_BLOCKED,
                    can_export=False,
                    repair_required=False,
                    manual_review_required=False,
                    is_terminal=True,
                    hard_blockers=report.hard_blockers,
                    warnings=report.warnings,
                    rationale=report.summary or "Document blocked due to unresolvable critical defects.",
                )

        else:
            # Safe default fallback for any unhandled decision
            return QualityRoutingInstruction(
                action=DecisionRouteAction.HALT_BLOCKED,
                can_export=False,
                repair_required=False,
                manual_review_required=False,
                is_terminal=True,
                hard_blockers=(f"UNKNOWN_DECISION_TYPE: {dec}",),
                warnings=(),
                rationale=f"Encountered unrecognized export decision type '{dec}'.",
            )
