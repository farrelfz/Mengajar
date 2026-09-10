"""
Universal Document Intelligence System V5 — Repair Escalation by Effectiveness.

Phase 3D.1: Governs strategy escalation based strictly on empirical causal failure,
disqualification, and reach insufficiency, rather than arbitrary iteration ticks.
"""

from __future__ import annotations

from enum import Enum
import logging
from typing import Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict

from app.quality.repair.effectiveness.causal_reach import CausalReach, CausalReachModel
from app.quality.repair.effectiveness.contracts import EffectivenessStatus, RepairEffectivenessResult
from app.quality.repair.effectiveness.coverage_matrix import RootCauseCoverageMatrix
from app.quality.repair.effectiveness.strategy_memory import SelfDisqualifyingStrategyMemory
from app.quality.repair.mutation_contract import RepairMutationScope
from app.quality.repair.root_cause import RootCauseType
from app.quality.repair.strategies.base import RepairStrategy

logger = logging.getLogger("quality.repair.escalation")


class RepairEscalationReason(str, Enum):
    """Reason triggering repair strategy or scope escalation."""
    INITIAL_SELECTION = "INITIAL_SELECTION"
    STRATEGY_INEFFECTIVE = "STRATEGY_INEFFECTIVE"
    ZERO_EFFECT_MUTATION = "ZERO_EFFECT_MUTATION"
    CAUSAL_REACH_INSUFFICIENT = "CAUSAL_REACH_INSUFFICIENT"
    STRATEGY_DISQUALIFIED = "STRATEGY_DISQUALIFIED"
    ROOT_CAUSE_PERSISTENT = "ROOT_CAUSE_PERSISTENT"
    REGRESSION_RISK = "REGRESSION_RISK"
    BUDGET_CONSTRAINT = "BUDGET_CONSTRAINT"
    NON_AUTOMATABLE_DEFECT = "NON_AUTOMATABLE_DEFECT"


class RepairEscalationDecision(BaseModel):
    """Authoritative escalation decision routing to next eligible strategy."""
    model_config = ConfigDict(frozen=True)

    previous_strategy_id: Optional[str]
    escalated_strategy_id: Optional[str]
    target_scope: RepairMutationScope
    target_owning_layer: str
    escalation_reason: RepairEscalationReason
    rationale: str
    is_terminal_manual_review: bool = False


class CausalEscalationEngine:
    """
    Decides whether and how to escalate strategies based on causal feedback.
    Enforces ordered preference sequences and disqualification filtering.
    """

    # Preferred escalation paths per canonical defect
    _PREFERRED_ESCALATION_SEQUENCES: Dict[Tuple[str, str], Tuple[str, ...]] = {
        ("ELEMENT_COLLISION", "PRESENTATION"): (
            "presentation_component_reflow",
            "presentation_layout_remap",
            "presentation_density_split",
        ),
        ("OVERLAPPING_CONTENT", "PRESENTATION"): (
            "presentation_component_reflow",
            "presentation_layout_remap",
            "presentation_density_split",
        ),
        ("TEXT_CLIPPING", "PRESENTATION"): (
            "presentation_padding_adjust",
            "presentation_layout_remap",
            "presentation_density_split",
        ),
        ("TEXT_OVERFLOW", "PRESENTATION"): (
            "presentation_padding_adjust",
            "presentation_density_split",
        ),
        ("REPETITION_STREAK", "WORKSHEET"): (
            "worksheet_layout_alternation",
            "worksheet_inquiry_sequence",
        ),
        ("TEXT_TOO_SMALL", "WORKSHEET"): (
            "worksheet_typography_scale",
            "worksheet_layout_alternation",
        ),
        ("SCIENTIFIC_CITATION_INVISIBLE", "SCIENTIFIC_DOCUMENT"): (
            "scientific_citation_linking",
        ),
    }

    @classmethod
    def resolve_escalation(
        cls,
        artifact_type: str,
        finding_code: str,
        root_cause: RootCauseType,
        previous_result: Optional[RepairEffectivenessResult],
        memory: SelfDisqualifyingStrategyMemory,
        available_strategies: Sequence[RepairStrategy],
        current_scope: RepairMutationScope,
    ) -> RepairEscalationDecision:
        """
        Determines the next strategy based on effectiveness history, disqualifications,
        and causal reach hierarchy.
        """
        norm_art = artifact_type.strip().upper()
        norm_code = finding_code.strip()

        # Check coverage
        coverage = RootCauseCoverageMatrix.lookup(norm_code, norm_art)
        if not coverage or not coverage.is_automatable:
            return RepairEscalationDecision(
                previous_strategy_id=previous_result.strategy_id if previous_result else None,
                escalated_strategy_id=None,
                target_scope=current_scope,
                target_owning_layer="R4",
                escalation_reason=RepairEscalationReason.NON_AUTOMATABLE_DEFECT,
                rationale=f"Finding '{norm_code}' on '{norm_art}' is non-automatable; escalating to manual review.",
                is_terminal_manual_review=True,
            )

        strat_map = {s.strategy_id: s for s in available_strategies}
        seq = cls._PREFERRED_ESCALATION_SEQUENCES.get(
            (norm_code, norm_art),
            coverage.eligible_strategy_ids,
        )

        prev_id = previous_result.strategy_id if previous_result else None

        # Determine if previous attempt failed
        if previous_result is not None:
            if previous_result.overall_status in (
                EffectivenessStatus.INEFFECTIVE,
                EffectivenessStatus.ZERO_EFFECT,
                EffectivenessStatus.REGRESSIVE,
            ):
                reason = (
                    RepairEscalationReason.ZERO_EFFECT_MUTATION
                    if previous_result.overall_status == EffectivenessStatus.ZERO_EFFECT
                    else (
                        RepairEscalationReason.REGRESSION_RISK
                        if previous_result.overall_status == EffectivenessStatus.REGRESSIVE
                        else RepairEscalationReason.STRATEGY_INEFFECTIVE
                    )
                )
            else:
                # Still progressing with current strategy
                reason = RepairEscalationReason.INITIAL_SELECTION
        else:
            reason = RepairEscalationReason.INITIAL_SELECTION

        # Iterate through preferred sequence to find first qualified, eligible strategy
        for candidate_id in seq:
            candidate_strat = strat_map.get(candidate_id)
            if not candidate_strat:
                continue

            # Check if disqualified in memory
            is_disqual, dis_reason = memory.is_strategy_disqualified(
                artifact_type=norm_art,
                artifact_id="default",
                root_cause_cluster=root_cause.name,
                strategy_id=candidate_id,
            )
            if is_disqual:
                logger.info("Candidate '%s' disqualified: %s", candidate_id, dis_reason)
                continue

            # Check if causal reach is sufficient
            strat_reach = getattr(candidate_strat, "causal_reach", None)
            if strat_reach and not CausalReachModel.is_reach_sufficient(strat_reach, root_cause):
                logger.info("Candidate '%s' reach (%s) insufficient for root cause %s", candidate_id, strat_reach, root_cause)
                continue

            # Scope of candidate
            cand_scope = getattr(candidate_strat, "mutation_scope", current_scope)
            cand_layer = getattr(candidate_strat, "owning_layer", coverage.owning_layer)

            return RepairEscalationDecision(
                previous_strategy_id=prev_id,
                escalated_strategy_id=candidate_id,
                target_scope=cand_scope,
                target_owning_layer=cand_layer,
                escalation_reason=reason if candidate_id != prev_id else RepairEscalationReason.INITIAL_SELECTION,
                rationale=f"Selected '{candidate_id}' for {norm_code} (Owning Layer: {cand_layer}).",
                is_terminal_manual_review=False,
            )

        # All strategies exhausted or disqualified
        return RepairEscalationDecision(
            previous_strategy_id=prev_id,
            escalated_strategy_id=None,
            target_scope=current_scope,
            target_owning_layer=coverage.owning_layer,
            escalation_reason=RepairEscalationReason.STRATEGY_DISQUALIFIED,
            rationale=f"All eligible strategies for {norm_code} are exhausted or disqualified. Manual review required.",
            is_terminal_manual_review=True,
        )
