"""Unit tests for ContentSegmenter."""


from app.intelligence.normalizer import InputNormalizer
from app.intelligence.schemas import ContentType
from app.intelligence.segmenter import ContentSegmenter


def test_segment_heading_hierarchy():
    """Verify H1 -> Paragraph -> H2 -> Paragraph parent-child relationship."""
    normalizer = InputNormalizer()
    segmenter = ContentSegmenter()

    raw = """
# BAB 1 PENDAHULUAN
Latar belakang penelitian ini membahas degradasi tanah.

## 1.1 Rumusan Masalah
Bagaimana pengaruh perlakuan?
"""
    doc = normalizer.normalize(raw, "hierarchy_test")
    res = segmenter.segment(doc)
    units = res.content_units

    assert len(units) == 4
    # Unit 0: H1
    assert units[0].content_type == ContentType.TITLE
    assert units[0].depth == 1
    assert units[0].parent_id is None

    # Unit 1: Paragraph under H1
    assert units[1].depth == 0
    assert units[1].parent_id == units[0].unit_id

    # Unit 2: H2 under H1
    assert units[2].content_type == ContentType.TITLE
    assert units[2].depth == 2
    assert units[2].parent_id == units[0].unit_id

    # Unit 3: Paragraph under H2
    assert units[3].depth == 0
    assert units[3].parent_id == units[2].unit_id


def test_segment_bullet_and_numbered_lists():
    """Verify unordered and ordered lists are segmented as SEQUENCE."""
    normalizer = InputNormalizer()
    segmenter = ContentSegmenter()

    raw = """
# Metodologi

Langkah kerja:

- Langkah 1
- Langkah 2
- Langkah 3

Tahapan berikutnya:

1. Tahap persiapan
2. Tahap pengujian
"""
    doc = normalizer.normalize(raw, "list_test")
    res = segmenter.segment(doc)
    units = res.content_units

    # Heading, paragraph, bullet list, paragraph, numbered list
    list_units = [u for u in units if u.content_type == ContentType.SEQUENCE]
    assert len(list_units) == 2
    assert "- Langkah 1" in list_units[0].normalized_text
    assert "1. Tahap persiapan" in list_units[1].normalized_text


def test_segment_preserves_source_order():
    """Verify source_order is monotonically increasing from 0 to N-1."""
    normalizer = InputNormalizer()
    segmenter = ContentSegmenter()

    raw = "# Titik 1\nTeks 1\n\n# Titik 2\nTeks 2\n\n# Titik 3\nTeks 3"
    doc = normalizer.normalize(raw, "order_test")
    res = segmenter.segment(doc)

    for i, u in enumerate(res.content_units):
        assert u.source_order == i


def test_segment_special_blocks_tables_and_code():
    """Verify special blocks are categorized with structural ContentType."""
    normalizer = InputNormalizer()
    segmenter = ContentSegmenter()

    raw = """
# Analisis

| Data 1 | Data 2 |
|---|---|
| 100 | 200 |

```python
x = 100
```
"""
    doc = normalizer.normalize(raw, "special_test")
    res = segmenter.segment(doc)
    types = [u.content_type for u in res.content_units]

    assert ContentType.DATA in types  # Table -> DATA
    assert ContentType.PROCEDURE in types  # Code -> PROCEDURE
