"""Unit tests for InputNormalizer."""

import pytest

from app.core.exceptions import NormalizationError
from app.intelligence.normalizer import InputNormalizer


def test_normalize_whitespace_and_newlines():
    """Verify that excessive blank lines, carriage returns, and trailing spaces are cleaned."""
    normalizer = InputNormalizer()
    raw = "Heading 1   \r\n\r\n\r\n\r\nParagraph text with  trailing   \r\n\r\n\r\n"
    doc = normalizer.normalize(raw, "test_source")

    assert "\r" not in doc.normalized_text
    assert "\n\n\n" not in doc.normalized_text
    assert "Heading 1" in doc.normalized_text
    assert "Paragraph text" in doc.normalized_text


def test_normalize_preserves_code_blocks():
    """Verify code blocks with backticks and formatting are preserved verbatim."""
    normalizer = InputNormalizer()
    raw = """
# Code Example

```python
def calculate(a, b):
    return a * b + 10
```

End of example.
"""
    doc = normalizer.normalize(raw, "code_test")
    assert doc.has_code_blocks is True
    assert len(doc.protected_regions) >= 1
    assert "def calculate(a, b):" in doc.normalized_text


def test_normalize_preserves_tables():
    """Verify markdown table syntax is detected and preserved."""
    normalizer = InputNormalizer()
    raw = """
# Data Table

| Col A | Col B |
|---|---|
| 10 | 20 |
| 30 | 40 |
"""
    doc = normalizer.normalize(raw, "table_test")
    assert doc.has_tables is True
    assert "| Col A | Col B |" in doc.normalized_text


def test_normalize_preserves_formulas():
    """Verify LaTeX math markers $$ and $ are detected and protected."""
    normalizer = InputNormalizer()
    raw = "The formula is $$E = mc^2$$ and inline $a^2 + b^2 = c^2$."
    doc = normalizer.normalize(raw, "formula_test")
    assert doc.has_formulas is True
    assert "$$E = mc^2$$" in doc.normalized_text


def test_normalize_empty_input_raises_error():
    """Verify empty string or whitespace-only input raises NormalizationError."""
    normalizer = InputNormalizer()
    with pytest.raises(NormalizationError):
        normalizer.normalize("   \n\t  \n  ", "empty_test")


def test_normalize_setext_heading_conversion():
    """Verify underline style headings are normalized to ATX # style."""
    normalizer = InputNormalizer()
    raw = "Main Section\n============\n\nSubsection\n----------\n\nContent here."
    doc = normalizer.normalize(raw, "heading_test")
    assert "# Main Section" in doc.normalized_text
    assert "## Subsection" in doc.normalized_text
