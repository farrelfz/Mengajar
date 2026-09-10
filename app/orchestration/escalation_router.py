"""
Universal Document Intelligence System V5 — Repair Escalation Router.

Phase 3D: Maps quality findings and root causes to the minimal owning architectural layer (R0–R5)
to prevent catastrophic full-pipeline re-execution for local styling or component defects.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.findings import QualityFinding
from app.quality.repair.mutation_contract import RepairMutationScope
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType


class RepairEscalationLayer(str, Enum):
    """Architectural layer responsible for addressing a defect."""
    LEVEL_R0_RENDER_TOKEN = "LEVEL_R0_RENDER_TOKEN"
    LEVEL_R1_COMPONENT_PARAM = "LEVEL_R1_COMPONENT_PARAM"
    LEVEL_R2_LAYOUT_STRUCTURE = "LEVEL_R2_LAYOUT_STRUCTURE"
    LEVEL_R3_ARTIFACT_STRUCTURE = "LEVEL_R3_ARTIFACT_STRUCTURE"
    LEVEL_R4_SEMANTIC_TRANSFORMATION = "LEVEL_R4_SEMANTIC_TRANSFORMATION"
    LEVEL_R5_SOURCE_INTELLIGENCE = "LEVEL_R5_SOURCE_INTELLIGENCE"

    @property
    def rank(self) -> int:
        _RANKS = {
            "LEVEL_R0_RENDER_TOKEN": 0,
            "LEVEL_R1_COMPONENT_PARAM": 1,
            "LEVEL_R2_LAYOUT_STRUCTURE": 2,
            "LEVEL_R3_ARTIFACT_STRUCTURE": 3,
            "LEVEL_R4_SEMANTIC_TRANSFORMATION": 4,
            "LEVEL_R5_SOURCE_INTELLIGENCE": 5,
        }
        return _RANKS[self.value]


class LayerEscalationPlan(BaseModel):
    """Deterministic routing plan indicating minimal affected scope and re-execution entrypoint."""
    model_config = ConfigDict(frozen=True)

    layer: RepairEscalationLayer
    target_scope: RepairMutationScope
    requires_re_transform: bool
    requires_re_bridge: bool
    requires_re_render: bool
    affected_elements: Tuple[str, ...] = Field(default_factory=tuple)
    rationale: str = ""


class RepairEscalationRouter:
    """Classifies findings to ensure targeted local repairs rather than full pipeline restarts."""

    _ROOT_CAUSE_TO_LAYER: Dict[RootCauseType, RepairEscalationLayer] = {
        RootCauseType.PADDING_SPACING: RepairEscalationLayer.LEVEL_R0_RENDER_TOKEN,
        RootCauseType.TYPOGRAPHY: RepairEscalationLayer.LEVEL_R0_RENDER_TOKEN,
        RootCauseType.GRID_GEOMETRY: RepairEscalationLayer.LEVEL_R1_COMPONENT_PARAM,
        RootCauseType.CONTENT_GROUPING: RepairEscalationLayer.LEVEL_R2_LAYOUT_STRUCTURE,
        RootCauseType.LAYOUT_SELECTION: RepairEscalationLayer.LEVEL_R2_LAYOUT_STRUCTURE,
        RootCauseType.SEMANTIC_LAYOUT_MAPPING: RepairEscalationLayer.LEVEL_R2_LAYOUT_STRUCTURE,
        RootCauseType.CONTENT_DENSITY: RepairEscalationLayer.LEVEL_R3_ARTIFACT_STRUCTURE,
        RootCauseType.PAGE_BREAK: RepairEscalationLayer.LEVEL_R3_ARTIFACT_STRUCTURE,
        RootCauseType.INQUIRY_STRUCTURE: RepairEscalationLayer.LEVEL_R3_ARTIFACT_STRUCTURE,
        RootCauseType.NARRATIVE_ORDER: RepairEscalationLayer.LEVEL_R3_ARTIFACT_STRUCTURE,
        RootCauseType.EVIDENCE_MAPPING: RepairEscalationLayer.LEVEL_R4_SEMANTIC_TRANSFORMATION,
        RootCauseType.TRACEABILITY_MAPPING: RepairEscalationLayer.LEVEL_R4_SEMANTIC_TRANSFORMATION,
        RootCauseType.SOURCE_INSUFFICIENCY: RepairEscalationLayer.LEVEL_R5_SOURCE_INTELLIGENCE,
    }

    _FAILURE_CODE_TO_LAYER: Dict[str, RepairEscalationLayer] = {
        "TEXT_CLIPPING": RepairEscalationLayer.LEVEL_R0_RENDER_TOKEN,
        "MARGIN_VIOLATION": RepairEscalationLayer.LEVEL_R0_RENDER_TOKEN,
        "CONTRAST_DEFICIT": RepairEscalationLayer.LEVEL_R0_RENDER_TOKEN,
        "LOW_CONTRAST": RepairEscalationLayer.LEVEL_R0_RENDER_TOKEN,
        "FONT_TOO_SMALL": RepairEscalationLayer.LEVEL_R0_RENDER_TOKEN,
        "WORKSPACE_UNDERSIZED": RepairEscalationLayer.LEVEL_R1_COMPONENT_PARAM,
        "GRID_COLLAPSE": RepairEscalationLayer.LEVEL_R1_COMPONENT_PARAM,
        "LAYOUT_INVERSION": RepairEscalationLayer.LEVEL_R2_LAYOUT_STRUCTURE,
        "INCOMPATIBLE_COMPONENT": RepairEscalationLayer.LEVEL_R2_LAYOUT_STRUCTURE,
        "SLIDE_OVERDENSITY": RepairEscalationLayer.LEVEL_R3_ARTIFACT_STRUCTURE,
        "PAGE_OVERFLOW": RepairEscalationLayer.LEVEL_R3_ARTIFACT_STRUCTURE,
        "ANTI_SPOILING_BREACH": RepairEscalationLayer.LEVEL_R3_ARTIFACT_STRUCTURE,
        "HEADING_SKIPPED": RepairEscalationLayer.LEVEL_R3_ARTIFACT_STRUCTURE,
        "CHAPTER_ORDER_INVALID": RepairEscalationLayer.LEVEL_R3_ARTIFACT_STRUCTURE,
        "UNSUPPORTED_SCIENTIFIC_CLAIM": RepairEscalationLayer.LEVEL_R4_SEMANTIC_TRANSFORMATION,
        "UNSUPPORTED_CLAIM_AS_FACT": RepairEscalationLayer.LEVEL_R4_SEMANTIC_TRANSFORMATION,
        "MISATTRIBUTED_EVIDENCE": RepairEscalationLayer.LEVEL_R4_SEMANTIC_TRANSFORMATION,
        "SOURCE_CONTRADICTION": RepairEscalationLayer.LEVEL_R5_SOURCE_INTELLIGENCE,
        "EXTRACTION_AMBIGUITY": RepairEscalationLayer.LEVEL_R5_SOURCE_INTELLIGENCE,
    }

    @classmethod
    def resolve_escalation(
        cls,
        findings: Sequence[QualityFinding],
        hypotheses: Sequence[RootCauseHypothesis] = (),
    ) -> LayerEscalationPlan:
        """Determines the minimal architectural owning layer across all active findings."""
        if not findings and not hypotheses:
            return LayerEscalationPlan(
                layer=RepairEscalationLayer.LEVEL_R0_RENDER_TOKEN,
                target_scope=RepairMutationScope.LEVEL_0_NO_MUTATION,
                requires_re_transform=False,
                requires_re_bridge=False,
                requires_re_render=False,
                rationale="No findings to escalate.",
            )

        highest_layer = RepairEscalationLayer.LEVEL_R0_RENDER_TOKEN
        affected: List[str] = []

        # 1. Inspect hypotheses
        for hyp in hypotheses:
            layer = cls._ROOT_CAUSE_TO_LAYER.get(hyp.cause_type, RepairEscalationLayer.LEVEL_R3_ARTIFACT_STRUCTURE)
            if layer.rank > highest_layer.rank:
                highest_layer = layer
            for t in hyp.affected_targets:
                if t.element_id:
                    affected.append(t.element_id)

        # 2. Inspect findings
        for f in findings:
            layer = cls._FAILURE_CODE_TO_LAYER.get(f.failure_code, RepairEscalationLayer.LEVEL_R3_ARTIFACT_STRUCTURE)
            if layer.rank > highest_layer.rank:
                highest_layer = layer
            if f.affected_elements:
                affected.extend(f.affected_elements)

        # 3. Map layer to scope and re-execution requirements
        if highest_layer == RepairEscalationLayer.LEVEL_R0_RENDER_TOKEN:
            scope = RepairMutationScope.LEVEL_1_LOCAL_TOKEN
            re_tx = False
            re_br = False
            re_rd = True
        elif highest_layer == RepairEscalationLayer.LEVEL_R1_COMPONENT_PARAM:
            scope = RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY
            re_tx = False
            re_br = False
            re_rd = True
        elif highest_layer == RepairEscalationLayer.LEVEL_R2_LAYOUT_STRUCTURE:
            scope = RepairMutationScope.LEVEL_3_PAGE_COMPOSITION
            re_tx = False
            re_br = True
            re_rd = True
        elif highest_layer == RepairEscalationLayer.LEVEL_R3_ARTIFACT_STRUCTURE:
            scope = RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING
            re_tx = False
            re_br = True
            re_rd = True
        elif highest_layer == RepairEscalationLayer.LEVEL_R4_SEMANTIC_TRANSFORMATION:
            scope = RepairMutationScope.LEVEL_5_ARTIFACT_STRUCTURE
            re_tx = True
            re_br = True
            re_rd = True
        else:  # R5
            scope = RepairMutationScope.LEVEL_6_MANUAL_REVIEW
            re_tx = True
            re_br = True
            re_rd = True

        return LayerEscalationPlan(
            layer=highest_layer,
            target_scope=scope,
            requires_re_transform=re_tx,
            requires_re_bridge=re_br,
            requires_re_render=re_rd,
            affected_elements=tuple(dict.fromkeys(affected)),
            rationale=f"Escalated to minimal owning layer {highest_layer.value} (scope {scope.name}).",
        )
