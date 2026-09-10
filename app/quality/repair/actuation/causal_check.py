"""
Universal Document Intelligence System V5 — Pre-Actuation Causal Sufficiency Check.

Phase 4: Gatekeeper verifying causal reach alignment, layer permissions,
and mutation target viability before executing real physical mutations.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Tuple

from app.quality.repair.actuation.contracts import RepairActuationRequest, RepairActuator
from app.quality.repair.effectiveness.causal_reach import CausalReach
from app.quality.repair.mutation_contract import RepairMutationScope

logger = logging.getLogger("quality.repair.actuation.causal_check")


class CausalSufficiencyError(ValueError):
    """Raised when an actuator lacks sufficient causal reach for the target defect."""
    pass


class PreActuationCausalCheck:
    """Validates that an actuator is causally sufficient and scope-admissible."""

    @classmethod
    def verify(
        cls,
        actuator: RepairActuator,
        request: RepairActuationRequest,
        blueprint: Any,
    ) -> Tuple[bool, Optional[str]]:
        """
        Returns (is_valid, rejection_reason).
        Never permits under-reaching actuators to attempt repairs.
        """
        # 1. Causal Reach Check
        req_reach = request.required_causal_reach
        max_reach = actuator.maximum_causal_reach
        if max_reach.depth < req_reach.depth:
            return (
                False,
                f"Actuator '{actuator.actuator_id}' maximum reach {max_reach.name} "
                f"(depth {max_reach.depth}) is insufficient for required defect reach "
                f"{req_reach.name} (depth {req_reach.depth}).",
            )

        # 2. Artifact Compatibility Check
        norm_art = request.artifact_type.strip().upper()
        supp_arts = [s.strip().upper() for s in actuator.supported_artifact_types]
        if norm_art not in supp_arts and "ALL" not in supp_arts:
            return (
                False,
                f"Actuator '{actuator.actuator_id}' does not support artifact '{norm_art}'.",
            )

        # 3. Can Actuate Check
        try:
            if not actuator.can_actuate(request, blueprint):
                return (
                    False,
                    f"Actuator '{actuator.actuator_id}' can_actuate returned False for current blueprint.",
                )
        except Exception as err:
            return False, f"Actuator '{actuator.actuator_id}' failed pre-check: {err}"

        return True, None
