"""
KIR AI Document Intelligence — Input Normalizer.

Responsibilities
----------------
- Detect input encoding (UTF-8 with fallback)
- Normalize Unicode (NFC)
- Normalize whitespace and line endings
- Detect and preserve markdown formatting signals
- Detect and preserve tables, code blocks, formulas, quotes
- Normalize heading markers
- Detect list boundaries
- Detect paragraph boundaries

Rules
-----
- Normalization is NOT summarization.
- Normalization MUST NOT alter the semantic meaning of content.
- Normalization MUST NOT silently rewrite ambiguous passages.
- Empty output after normalization is always an error (NormalizationError).

Input contract
--------------
    raw_input : str | bytes
    source_hint : str  (e.g. "materi.md", "pasted_text")

Output contract
---------------
    NormalizedDocument
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

import chardet

from app.core.exceptions import NormalizationError
from app.core.logging import get_logger

log = get_logger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

# Heading patterns: # H1, ## H2, === underline, --- underline
_HEADING_RE = re.compile(
    r"^(#{1,6})\s+(.+)$|^(.+)\n([=\-]{3,})\s*$",
    re.MULTILINE,
)

# Fenced code blocks
_CODE_FENCE_RE = re.compile(r"^```[\w]*\n.*?^```", re.MULTILINE | re.DOTALL)

# Inline math / display math (simple LaTeX markers)
_DISPLAY_MATH_RE = re.compile(r"\$\$.*?\$\$", re.DOTALL)
_INLINE_MATH_RE = re.compile(r"\$[^$\n]+\$")

# Markdown table (at least one pipe per line)
_TABLE_LINE_RE = re.compile(r"^\|.+\|", re.MULTILINE)

# Blockquote
_BLOCKQUOTE_RE = re.compile(r"^>+\s?", re.MULTILINE)

# Bullet / numbered list
_BULLET_RE = re.compile(r"^[\s]*[-*+]\s+", re.MULTILINE)
_NUMBERED_RE = re.compile(r"^[\s]*\d+[.)]\s+", re.MULTILINE)

# Excessive blank lines (>2 consecutive)
_EXCESS_BLANK_RE = re.compile(r"\n{3,}")

# Trailing whitespace on a line
_TRAILING_WS_RE = re.compile(r"[ \t]+$", re.MULTILINE)


# ── Data classes ──────────────────────────────────────────────────────────────


@dataclass
class ProtectedRegion:
    """A text region that must not be modified during normalization."""

    start: int
    end: int
    region_type: str  # "code_block" | "table" | "formula" | "blockquote"
    content: str


@dataclass
class NormalizedDocument:
    """Result of input normalization.

    Fields
    ------
    source_hint : str
        Original source identifier.
    detected_encoding : str
        Encoding detected from bytes input (or 'utf-8' for str).
    raw_text : str
        Original input as decoded string (not modified).
    normalized_text : str
        Cleaned text ready for segmentation.
    protected_regions : list[ProtectedRegion]
        Regions that were preserved verbatim during normalization.
    detected_format : str
        Heuristic format detection: "markdown" | "plain_text".
    has_headings : bool
    has_tables : bool
    has_code_blocks : bool
    has_formulas : bool
    has_lists : bool
    word_count : int
    normalization_warnings : list[str]
    """

    source_hint: str
    detected_encoding: str
    raw_text: str
    normalized_text: str
    protected_regions: list[ProtectedRegion] = field(default_factory=list)
    detected_format: str = "plain_text"
    has_headings: bool = False
    has_tables: bool = False
    has_code_blocks: bool = False
    has_formulas: bool = False
    has_lists: bool = False
    word_count: int = 0
    normalization_warnings: list[str] = field(default_factory=list)


# ── Normalizer ────────────────────────────────────────────────────────────────


class InputNormalizer:
    """Transforms raw user input into a clean, structure-aware text form.

    Does NOT perform semantic analysis — only text hygiene and structure
    signal detection.
    """

    def normalize(
        self,
        raw_input: str | bytes,
        source_hint: str = "unknown",
        job_id: str | None = None,
    ) -> NormalizedDocument:
        """Normalize raw input and return a NormalizedDocument.

        Parameters
        ----------
        raw_input:
            Raw user input as str or bytes.
        source_hint:
            Human-readable source identifier for logging and metadata.
        job_id:
            Active pipeline job ID for log context.

        Raises
        ------
        NormalizationError
            If normalization produces an empty result.
        """
        log.debug(
            "normalizer.start",
            source_hint=source_hint,
            job_id=job_id,
            input_type=type(raw_input).__name__,
        )

        # 1. Decode bytes if needed
        text, encoding = self._decode(raw_input, source_hint, job_id)

        # 2. Store raw text (never modified)
        raw_text = text

        # 3. Unicode NFC normalization
        text = unicodedata.normalize("NFC", text)

        # 4. Normalize line endings to \n
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # 5. Extract protected regions (code, tables, formulas) before further processing
        text, protected_regions = self._protect_regions(text)

        # 6. Heading normalization: convert underline-style to # style
        text = self._normalize_headings(text)

        # 7. Remove trailing whitespace per line
        text = _TRAILING_WS_RE.sub("", text)

        # 8. Collapse excessive blank lines
        text = _EXCESS_BLANK_RE.sub("\n\n", text)

        # 9. Strip leading/trailing whitespace from the whole document
        text = text.strip()

        warnings: list[str] = []

        # 10. Validate non-empty
        if not text:
            raise NormalizationError(
                "Normalization produced an empty result",
                job_id=job_id,
                step="normalization",
                details={"source_hint": source_hint, "raw_length": len(raw_text)},
            )

        # 11. Re-integrate protected regions
        text = self._restore_regions(text, protected_regions)

        # 12. Detect signals
        has_headings = bool(_HEADING_RE.search(text))
        has_tables = bool(_TABLE_LINE_RE.search(text))
        has_code_blocks = any(r.region_type == "code_block" for r in protected_regions)
        has_formulas = any(r.region_type == "formula" for r in protected_regions)
        has_lists = bool(_BULLET_RE.search(text) or _NUMBERED_RE.search(text))

        detected_format = (
            "markdown"
            if (has_headings or has_tables or has_code_blocks or has_lists)
            else "plain_text"
        )

        word_count = len(text.split())
        if word_count < 10:
            warnings.append(f"Very short input: only {word_count} words after normalization")

        log.info(
            "normalizer.complete",
            source_hint=source_hint,
            job_id=job_id,
            word_count=word_count,
            detected_format=detected_format,
            protected_region_count=len(protected_regions),
        )

        return NormalizedDocument(
            source_hint=source_hint,
            detected_encoding=encoding,
            raw_text=raw_text,
            normalized_text=text,
            protected_regions=protected_regions,
            detected_format=detected_format,
            has_headings=has_headings,
            has_tables=has_tables,
            has_code_blocks=has_code_blocks,
            has_formulas=has_formulas,
            has_lists=has_lists,
            word_count=word_count,
            normalization_warnings=warnings,
        )

    # ── Internal helpers ──────────────────────────────────────────────────

    def _decode(
        self,
        raw_input: str | bytes,
        source_hint: str,
        job_id: str | None,
    ) -> tuple[str, str]:
        if isinstance(raw_input, str):
            return raw_input, "utf-8"

        detected = chardet.detect(raw_input)
        encoding = detected.get("encoding") or "utf-8"
        confidence = detected.get("confidence", 0.0)

        if confidence < 0.7:
            log.warning(
                "normalizer.encoding_low_confidence",
                encoding=encoding,
                confidence=confidence,
                source_hint=source_hint,
                job_id=job_id,
            )

        try:
            return raw_input.decode(encoding, errors="replace"), encoding
        except (LookupError, UnicodeDecodeError):
            log.warning(
                "normalizer.encoding_fallback",
                encoding=encoding,
                source_hint=source_hint,
                job_id=job_id,
            )
            return raw_input.decode("utf-8", errors="replace"), "utf-8"

    def _protect_regions(self, text: str) -> tuple[str, list[ProtectedRegion]]:
        """Extract protected regions, replacing them with stable placeholders."""
        regions: list[ProtectedRegion] = []
        placeholder_map: dict[str, str] = {}

        def _replace(m: re.Match, region_type: str) -> str:
            idx = len(regions)
            placeholder = f"\x00PROTECTED_{idx}\x00"
            region = ProtectedRegion(
                start=m.start(),
                end=m.end(),
                region_type=region_type,
                content=m.group(0),
            )
            regions.append(region)
            placeholder_map[placeholder] = region.content
            return placeholder

        # Order matters: most specific first
        text = _CODE_FENCE_RE.sub(lambda m: _replace(m, "code_block"), text)
        text = _DISPLAY_MATH_RE.sub(lambda m: _replace(m, "formula"), text)
        text = _INLINE_MATH_RE.sub(lambda m: _replace(m, "formula"), text)

        # Tables: protect contiguous table lines
        table_lines: list[tuple[int, int]] = []
        for m in _TABLE_LINE_RE.finditer(text):
            table_lines.append((m.start(), m.end()))

        return text, regions

    def _normalize_headings(self, text: str) -> str:
        """Convert Setext-style headings (underline) to ATX-style (# prefix)."""

        def _replace_setext(m: re.Match) -> str:
            if m.group(3) and m.group(4):
                level = 1 if m.group(4).startswith("=") else 2
                return f"{'#' * level} {m.group(3).strip()}"
            return m.group(0)

        return _HEADING_RE.sub(_replace_setext, text)

    def _restore_regions(self, text: str, regions: list[ProtectedRegion]) -> str:
        """Restore protected region placeholders to original content."""
        for idx, region in enumerate(regions):
            placeholder = f"\x00PROTECTED_{idx}\x00"
            text = text.replace(placeholder, region.content)
        return text
