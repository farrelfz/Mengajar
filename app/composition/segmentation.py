"""
KIR AI Document Intelligence — Page Segmentation & Boundaries.
"""
from enum import Enum
from pydantic import BaseModel
from app.formats.schemas import FormatConfig

class BoundaryStrategy(str, Enum):
    KEEP_TOGETHER = "KEEP_TOGETHER"
    SPLIT_AFTER_UNIT = "SPLIT_AFTER_UNIT"
    MOVE_SECONDARY_CONTENT = "MOVE_SECONDARY_CONTENT"
    CREATE_CONTINUATION = "CREATE_CONTINUATION"
    CREATE_NEW_PAGE = "CREATE_NEW_PAGE"
    CHANGE_PAGE_TYPE = "CHANGE_PAGE_TYPE"


class PageBoundaryDecision(BaseModel):
    decision: BoundaryStrategy
    reason: str
    source_unit_ids: list[str]
    estimated_words: int


def evaluate_boundary(word_count: int, format_config: FormatConfig, unit_ids: list[str]) -> PageBoundaryDecision:
    """Evaluates if content should be split based on the format limits."""
    if word_count <= format_config.max_words_per_page:
        return PageBoundaryDecision(
            decision=BoundaryStrategy.KEEP_TOGETHER,
            reason="Within density limits.",
            source_unit_ids=unit_ids,
            estimated_words=word_count
        )
        
    if format_config.aggressively_splits_content:
        # e.g., Presentation mode
        return PageBoundaryDecision(
            decision=BoundaryStrategy.CREATE_CONTINUATION,
            reason=f"Exceeds max words ({word_count} > {format_config.max_words_per_page}) in aggressive split mode.",
            source_unit_ids=unit_ids,
            estimated_words=word_count
        )
    else:
        # A4 Mode might tolerate slight overflow or use columns
        if word_count > format_config.max_words_per_page * 1.5:
            return PageBoundaryDecision(
                decision=BoundaryStrategy.CREATE_CONTINUATION,
                reason="Significantly exceeds max words for A4.",
                source_unit_ids=unit_ids,
                estimated_words=word_count
            )
        else:
            return PageBoundaryDecision(
                decision=BoundaryStrategy.KEEP_TOGETHER,
                reason="Slight overflow in A4, keeping together.",
                source_unit_ids=unit_ids,
                estimated_words=word_count
            )
