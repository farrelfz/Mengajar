"""A4 Landscape format constraints."""
from app.formats.schemas import FormatConfig
from app.intelligence.schemas import DocumentMode

a4_landscape_config = FormatConfig(
    mode=DocumentMode.A4_LANDSCAPE,
    max_words_per_page=400,
    preferred_regions=["header", "primary", "secondary"],
    supports_multi_column=True,
    aggressively_splits_content=False,
)

# Alias for backwards compatibility
a4_config = a4_landscape_config
