"""
Universal Document Intelligence System V5 — Symptom vs Cause Classifier.

Phase 3B: Explicitly separates observed physical symptoms from upstream structural
and semantic root cause candidates within a FailureCluster.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.causal.contracts import FailureCluster, QualitySignal
from app.quality.causal.taxonomy import CanonicalFailureDomain


class FailureRole(str, Enum):
    """Categorical role of a diagnostic signal within a failure cluster."""
    PRIMARY_SYMPTOM = "PRIMARY_SYMPTOM"
    SECONDARY_SYMPTOM = "SECONDARY_SYMPTOM"
    POSSIBLE_CAUSE = "POSSIBLE_CAUSE"
    ROOT_CAUSE_CANDIDATE = "ROOT_CAUSE_CANDIDATE"
    UNKNOWN_ROLE = "UNKNOWN_ROLE"


class FailureRoleAssignment(BaseModel):
    """Assignment of a functional failure role to a specific QualitySignal."""
    model_config = ConfigDict(frozen=True)

    signal_id: str
    failure_code: str
    role: FailureRole
    rationale: str
    architectural_stage: str


class SymptomCauseClassifier:
    """Classifies signals into symptoms, intermediate causes, and root cause candidates."""

    # Stage ordering: lower number = upstream (closer to cause), higher number = downstream (symptoms)
    STAGE_ORDERING: Dict[str, int] = {
        "SOURCE": 1,
        "SEMANTIC": 2,
        "TRANSFORMATION": 3,
        "BLUEPRINT": 4,
        "LAYOUT": 5,
        "COMPOSITION": 6,
        "TYPOGRAPHY": 7,
        "RENDER": 8,
        "VALIDATION": 9,
    }

    PRIMARY_SYMPTOM_CODES = {
        "TEXT_CLIPPING",
        "ELEMENT_COLLISION",
        "TEXT_TOO_SMALL",
        "PAGE_BOUNDARY_VIOLATION",
        "BLANK_PAGE",
        "OVERFLOW_HIDDEN_CUTOFF",
        "CONTRAST_DEFICIT",
    }

    POSSIBLE_CAUSE_CODES = {
        "DENSITY_OVERLOAD",
        "WALL_OF_TEXT",
        "CARD_OVERLOAD",
        "COGNITIVE_LOAD_OVERFLOW",
        "SUSPICIOUS_VOID",
        "DENSITY_IMBALANCE",
        "LAYOUT_MONOTONY",
    }

    ROOT_CAUSE_CODES = {
        "LAYOUT_CAPACITY_MISMATCH",
        "LAYOUT_SEMANTIC_MISMATCH",
        "BLUEPRINT_CAPACITY_MISMATCH",
        "NARRATIVE_FRAGMENTATION",
        "SOURCE_GROUNDING_FAILURE",
        "UNSUPPORTED_CLAIM",
        "TRACEABILITY_BREAK",
        "INQUIRY_FLOW_BREAK",
        "WORKSHEET_SPOILING_FAILURE",
        "SCIENTIFIC_CITATION_INVISIBLE",
        "SCIENTIFIC_HIERARCHY_FAILURE",
        "WORKSHEET_QUIZ_COLLAPSE",
    }

    @classmethod
    def classify_cluster_signals(cls, cluster: FailureCluster) -> List[FailureRoleAssignment]:
        """Classifies each signal in the cluster based on domain, code, and lineage."""
        assignments: List[FailureRoleAssignment] = []

        for sig in sorted(cluster.signals, key=lambda s: s.signal_id):
            code_str = sig.failure_code.value
            domain = sig.failure_domain

            # 1. Physical render defects are almost always primary symptoms
            if code_str in cls.PRIMARY_SYMPTOM_CODES or domain == CanonicalFailureDomain.PHYSICAL_RENDER:
                role = FailureRole.PRIMARY_SYMPTOM
                rationale = f"Physical render flaw '{code_str}' observed directly on output canvas"
                stage = "RENDER"

            # 2. Density / cognitive load are intermediate causes or symptoms
            elif code_str in cls.POSSIBLE_CAUSE_CODES or domain == CanonicalFailureDomain.COGNITIVE_LOAD:
                role = FailureRole.POSSIBLE_CAUSE
                rationale = f"Content density defect '{code_str}' exerts pressure on composition geometry"
                stage = "COMPOSITION"

            # 3. Blueprint / semantic flaws are root cause candidates
            elif code_str in cls.ROOT_CAUSE_CODES or domain in (
                CanonicalFailureDomain.BLUEPRINT_INTEGRITY,
                CanonicalFailureDomain.SEMANTIC_TRACEABILITY,
                CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
                CanonicalFailureDomain.SCIENTIFIC_RIGOR,
            ):
                role = FailureRole.ROOT_CAUSE_CANDIDATE
                rationale = f"Upstream structural defect '{code_str}' dictates downstream layout failure"
                stage = "BLUEPRINT"

            # 4. Style design flaws
            elif domain == CanonicalFailureDomain.STYLE_DESIGN:
                role = FailureRole.POSSIBLE_CAUSE
                rationale = f"Template/layout defect '{code_str}' contributes to visual hierarchy degradation"
                stage = "LAYOUT"

            else:
                role = FailureRole.UNKNOWN_ROLE
                rationale = f"Unclassified defect role for code '{code_str}'"
                stage = "UNKNOWN"

            assignments.append(
                FailureRoleAssignment(
                    signal_id=sig.signal_id,
                    failure_code=code_str,
                    role=role,
                    rationale=rationale,
                    architectural_stage=stage,
                )
            )

        return assignments
