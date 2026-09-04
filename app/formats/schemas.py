"""
KIR AI Document Intelligence — Format Schemas (Batch 4).

Abstract format constraints and settings.
"""

from pydantic import BaseModel
from app.intelligence.schemas import DocumentMode


class FormatConfig(BaseModel):
    """Constraints applicable to a specific document format."""
    mode: DocumentMode
    max_words_per_page: int
    preferred_regions: list[str]
    supports_multi_column: bool
    aggressively_splits_content: bool
