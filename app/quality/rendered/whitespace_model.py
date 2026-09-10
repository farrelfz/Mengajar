"""
Universal Document Intelligence System V5 — Context-Aware Whitespace Model.

Phase 3A: Disentangles intentional breathing room and student workspace from
accidental emptiness and suspicious void.
CRITICAL RULE: Worksheet student answer areas must NEVER be penalized as empty space.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.rendered.failure_taxonomy import (
    FutureRepairClass,
    RenderedFailureCode,
    RenderedFailureSeverity,
    RenderedQualityFailure,
)


class WhitespaceEvaluation(BaseModel):
    """Contextual classification of page whitespace."""
    model_config = ConfigDict(frozen=True)

    page_number: int
    total_whitespace_ratio: float
    intentional_whitespace_ratio: float
    suspicious_void_ratio: float
    is_acceptable: bool
    status: str  # OPTIMAL, ACCEPTABLE, SUSPICIOUS_VOID, CRAMPED
    failure: Optional[RenderedQualityFailure] = None


class WhitespaceIntentModel:
    """Evaluates page whitespace contextually based on artifact type and page role."""

    # Target whitespace bounds by artifact type: (min_acceptable, max_acceptable)
    ARTIFACT_WHITESPACE_BOUNDS: Dict[str, Tuple[float, float]] = {
        "PRESENTATION": (0.25, 0.75),   # Generous breathing room is encouraged
        "HANDOUT": (0.15, 0.50),        # Continuous reading; >50% wastes paper
        "WORKSHEET": (0.20, 0.70),      # High whitespace reserved for student responses
        "SCIENTIFIC_DOCUMENT": (0.15, 0.45), # Formal academic density
    }

    @classmethod
    def evaluate_page(
        cls,
        page_idx: int,
        artifact_type: str,
        occupancy_ratio: float,
        text_length: int,
        is_last_page: bool = False,
        reserved_workspace_area_ratio: float = 0.0,
        page_role: str = "BODY",
    ) -> WhitespaceEvaluation:
        norm_type = artifact_type.upper()
        raw_whitespace = max(0.0, 1.0 - occupancy_ratio)

        # In worksheets, student workspace box area is explicitly intentional
        intentional_ws = reserved_workspace_area_ratio
        if norm_type == "WORKSHEET":
            # For worksheets, up to 45% additional whitespace is treated as intentional student canvas
            intentional_ws = max(intentional_ws, min(0.50, raw_whitespace * 0.80))
        elif norm_type == "PRESENTATION" and page_role in ("HERO", "TITLE", "CONCLUSION"):
            intentional_ws = min(0.60, raw_whitespace * 0.85)
        else:
            intentional_ws = min(0.30, raw_whitespace * 0.50)

        suspicious_void = max(0.0, raw_whitespace - intentional_ws)

        min_bound, max_bound = cls.ARTIFACT_WHITESPACE_BOUNDS.get(norm_type, (0.20, 0.60))

        status = "OPTIMAL"
        failure: Optional[RenderedQualityFailure] = None
        is_acceptable = True

        # Check for underfilled / suspicious void (except on document final page or title slides)
        is_title_or_hero = page_role in ("HERO", "TITLE", "CONCLUSION") or (norm_type == "PRESENTATION" and page_idx == 1)
        if not is_last_page and not is_title_or_hero and raw_whitespace > (max_bound + 0.15) and text_length < 80 and norm_type != "WORKSHEET":
            status = "SUSPICIOUS_VOID"
            is_acceptable = False
            failure = RenderedQualityFailure(
                code=RenderedFailureCode.SUSPICIOUS_VOID,
                severity=RenderedFailureSeverity.MAJOR if raw_whitespace > 0.90 else RenderedFailureSeverity.MINOR,
                artifact_type=norm_type,
                page_indices=(page_idx,),
                description=(
                    f"Page {page_idx}: Excessive accidental void ({raw_whitespace * 100:.1f}% empty, "
                    f"{text_length} chars). Underdeveloped content block."
                ),
                evidence={"whitespace_ratio": raw_whitespace, "text_length": text_length},
                recommended_future_repair=FutureRepairClass.CLASS_C_PAGINATION_PACING,
                repair_guidance="Consolidate with adjacent page or expand explanatory detail.",
            )
        # Check for cramped / overloaded page
        elif raw_whitespace < (min_bound - 0.08) and text_length > 1200 and norm_type in ("PRESENTATION", "WORKSHEET"):
            status = "CRAMPED"
            is_acceptable = False
            failure = RenderedQualityFailure(
                code=RenderedFailureCode.DENSITY_OVERLOAD,
                severity=RenderedFailureSeverity.MAJOR if text_length > 1500 else RenderedFailureSeverity.MINOR,
                artifact_type=norm_type,
                page_indices=(page_idx,),
                description=(
                    f"Page {page_idx}: Cramped viewport ({raw_whitespace * 100:.1f}% whitespace, "
                    f"{text_length} chars). Lacks adequate breathing room."
                ),
                evidence={"whitespace_ratio": raw_whitespace, "text_length": text_length},
                recommended_future_repair=FutureRepairClass.CLASS_C_PAGINATION_PACING,
                repair_guidance="Split content across multiple slides or expand card spacing.",
            )

        return WhitespaceEvaluation(
            page_number=page_idx,
            total_whitespace_ratio=round(raw_whitespace, 3),
            intentional_whitespace_ratio=round(intentional_ws, 3),
            suspicious_void_ratio=round(suspicious_void, 3),
            is_acceptable=is_acceptable,
            status=status,
            failure=failure,
        )
