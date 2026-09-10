"""
Universal Document Intelligence System V5 — Repair Authority Matrix.

Phase 3A.1: Enforces strict boundaries on which layer is authorized to repair
specific root causes, defining allowed repair classes and explicit forbidden fixes.
"""

from __future__ import annotations

from typing import Dict, List, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.causal.cause_catalog import CausalDefectCatalog
from app.quality.causal.taxonomy import (
    ArchitectureLayer,
    CanonicalRepairClass,
    CausalConfidenceLevel,
)


class RepairPolicyRule(BaseModel):
    """Repair permission contract for an attributed root cause."""
    model_config = ConfigDict(frozen=True)

    cause_code: str
    owning_layer: ArchitectureLayer
    allowed_repair_classes: Tuple[CanonicalRepairClass, ...]
    forbidden_repairs: Tuple[str, ...]
    requires_manual_review: bool = False
    rationale: str = ""


class RepairAuthorityMatrix:
    """Authoritative gatekeeper validating future repair strategies before execution."""

    @classmethod
    def get_repair_policy(
        cls,
        cause_code: str,
        confidence_level: CausalConfidenceLevel = CausalConfidenceLevel.HIGH,
    ) -> RepairPolicyRule:
        # If confidence is LOW or AMBIGUOUS, auto repair is forbidden!
        if confidence_level in (CausalConfidenceLevel.LOW, CausalConfidenceLevel.AMBIGUOUS):
            return RepairPolicyRule(
                cause_code=cause_code,
                owning_layer=ArchitectureLayer.ARTIFACT_POLICY,
                allowed_repair_classes=(CanonicalRepairClass.CLASS_G_MANUAL_REVIEW,),
                forbidden_repairs=("ANY_AUTOMATIC_REPAIR",),
                requires_manual_review=True,
                rationale=f"Confidence is {confidence_level.value}. Automatic repair is forbidden to prevent regression.",
            )

        cause_def = CausalDefectCatalog.get_cause(cause_code)
        if cause_def:
            return RepairPolicyRule(
                cause_code=cause_code,
                owning_layer=cause_def.repair_authority,
                allowed_repair_classes=cause_def.allowed_repair_classes,
                forbidden_repairs=cause_def.forbidden_repairs,
                requires_manual_review=False,
                rationale=f"Attributed to {cause_def.repair_authority.value}. Allowed: {[c.value for c in cause_def.allowed_repair_classes]}",
            )

        # Unknown cause default
        return RepairPolicyRule(
            cause_code=cause_code,
            owning_layer=ArchitectureLayer.ARTIFACT_POLICY,
            allowed_repair_classes=(CanonicalRepairClass.CLASS_G_MANUAL_REVIEW,),
            forbidden_repairs=("UNVALIDATED_REPAIR",),
            requires_manual_review=True,
            rationale=f"Uncataloged cause code '{cause_code}'. Requires human architectural review.",
        )

    @classmethod
    def is_repair_allowed(
        cls,
        cause_code: str,
        repair_class: CanonicalRepairClass,
        confidence_level: CausalConfidenceLevel,
    ) -> bool:
        policy = cls.get_repair_policy(cause_code, confidence_level)
        return repair_class in policy.allowed_repair_classes
