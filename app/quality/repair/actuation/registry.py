"""
Universal Document Intelligence System V5 — Repair Actuator Registry.

Phase 4: Authoritative registry for executable repair actuators. Connects
repair strategies to concrete transformation operators and supports capability queries.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.quality.repair.actuation.contracts import RepairActuationRequest, RepairActuator

logger = logging.getLogger("quality.repair.actuation.registry")


class RepairActuatorRegistry:
    """Registry maintaining mappings from strategy IDs and artifact types to executable actuators."""

    _instance: Optional[RepairActuatorRegistry] = None

    def __init__(self) -> None:
        self._actuators_by_id: Dict[str, RepairActuator] = {}
        self._actuators_by_strategy: Dict[str, List[RepairActuator]] = {}

    @classmethod
    def get_default(cls) -> RepairActuatorRegistry:
        if cls._instance is None:
            reg = cls()
            reg.populate_defaults()
            cls._instance = reg
        return cls._instance

    @classmethod
    def reset_default(cls) -> None:
        cls._instance = None

    def populate_defaults(self) -> None:
        """Registers canonical actuators and binds them to standard repair strategies."""
        from app.quality.repair.actuation.handout import (
            HandoutDensityReflowActuator,
            HandoutSectionBalanceActuator,
        )
        from app.quality.repair.actuation.presentation import (
            PresentationComponentReflowActuator,
            PresentationCompositionActuator,
            PresentationDiversityActuator,
            PresentationFormulaRecompositionActuator,
            PresentationSlideSplitActuator,
        )
        from app.quality.repair.actuation.scientific import (
            ScientificCitationVisibilityActuator,
            ScientificEvidenceLayoutActuator,
        )
        from app.quality.repair.actuation.typography_solver import TypographyRepairActuator
        from app.quality.repair.actuation.worksheet import (
            WorksheetInquiryRecompositionActuator,
        )

        # Presentation
        self.register(
            PresentationComponentReflowActuator(),
            ["presentation_component_reflow", "presentation_padding_adjustment"],
        )
        self.register(
            PresentationFormulaRecompositionActuator(),
            ["presentation_formula_recomposition", "presentation_layout_remap", "presentation_component_reflow"],
        )
        self.register(
            PresentationCompositionActuator(),
            ["presentation_composition_actuator", "presentation_layout_remap"],
        )
        self.register(
            PresentationSlideSplitActuator(),
            ["presentation_slide_split_actuator", "presentation_density_split"],
        )
        self.register(
            PresentationDiversityActuator(),
            ["presentation_diversity_actuator", "presentation_layout_remap"],
        )

        # Worksheet
        self.register(
            WorksheetInquiryRecompositionActuator(),
            [
                "worksheet_inquiry_recomposition",
                "worksheet_inquiry_sequence",
                "worksheet_layout_alternation",
                "worksheet_anti_spoiling",
                "worksheet_workspace_expansion",
            ],
        )

        # Typography
        self.register(
            TypographyRepairActuator(),
            [
                "typography_constraint_actuator",
                "worksheet_typography_scale",
                "presentation_padding_adjustment",
            ],
        )

        # Scientific Document
        self.register(
            ScientificCitationVisibilityActuator(),
            ["scientific_citation_visibility", "scientific_citation_linking"],
        )
        self.register(
            ScientificEvidenceLayoutActuator(),
            [
                "scientific_evidence_layout",
                "scientific_evidence_mapping",
                "scientific_claim_downgrade",
                "scientific_limitation_isolation",
                "scientific_methodology_order",
            ],
        )

        # Handout
        self.register(
            HandoutDensityReflowActuator(),
            ["handout_density_reflow", "handout_density_balance"],
        )
        self.register(
            HandoutSectionBalanceActuator(),
            ["handout_section_balance", "handout_pagination", "handout_hierarchy_repair"],
        )

    def register(
        self,
        actuator: RepairActuator,
        strategy_ids: Optional[Sequence[str]] = None,
    ) -> None:
        """Register an actuator, optionally binding it to specific strategy IDs."""
        self._actuators_by_id[actuator.actuator_id] = actuator
        sids = list(strategy_ids) if strategy_ids else [actuator.actuator_id]
        for sid in sids:
            if sid not in self._actuators_by_strategy:
                self._actuators_by_strategy[sid] = []
            if actuator not in self._actuators_by_strategy[sid]:
                self._actuators_by_strategy[sid].append(actuator)
        logger.debug(
            "Registered actuator '%s' for strategies: %s",
            actuator.actuator_id,
            sids,
        )

    def get_actuator_by_id(self, actuator_id: str) -> Optional[RepairActuator]:
        return self._actuators_by_id.get(actuator_id)

    def get_actuator_for_strategy(
        self,
        strategy_id: str,
        artifact_type: Optional[str] = None,
    ) -> Optional[RepairActuator]:
        """Find the most specific actuator for a given strategy_id and artifact_type."""
        candidates = self._actuators_by_strategy.get(strategy_id, [])
        if not candidates:
            # Fallback: check if an actuator exists with the exact actuator_id == strategy_id
            direct = self._actuators_by_id.get(strategy_id)
            if direct:
                candidates = [direct]

        if not candidates:
            return None

        if artifact_type is None:
            return candidates[0]

        norm_art = artifact_type.strip().upper()
        for cand in candidates:
            supp = [s.strip().upper() for s in getattr(cand, "supported_artifact_types", ())]
            if norm_art in supp or "ALL" in supp:
                return cand

        return None

    def has_actuator(self, strategy_id: str, artifact_type: Optional[str] = None) -> bool:
        return self.get_actuator_for_strategy(strategy_id, artifact_type) is not None

    def can_actuate(
        self,
        strategy_id: str,
        request: RepairActuationRequest,
        blueprint: Any,
    ) -> bool:
        """Checks whether a capable actuator exists and its can_actuate returns True."""
        actuator = self.get_actuator_for_strategy(strategy_id, request.artifact_type)
        if actuator is None:
            return False
        try:
            return actuator.can_actuate(request, blueprint)
        except Exception as err:
            logger.warning(
                "Actuator '%s' raised exception during can_actuate: %s",
                actuator.actuator_id,
                err,
            )
            return False

    def all_actuators(self) -> List[RepairActuator]:
        return list(self._actuators_by_id.values())

    def clear(self) -> None:
        self._actuators_by_id.clear()
        self._actuators_by_strategy.clear()
