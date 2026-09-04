"""Presentation 16:9 format constraints."""
from app.formats.schemas import FormatConfig
from app.intelligence.schemas import DocumentMode

presentation_config = FormatConfig(
    mode=DocumentMode.PRESENTATION_16_9,
    max_words_per_page=120,
    preferred_regions=["header", "primary"],
    supports_multi_column=False,
    aggressively_splits_content=True
)
