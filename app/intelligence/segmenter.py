"""
KIR AI Document Intelligence — Content Segmenter.

Responsibilities
----------------
- Split a NormalizedDocument into candidate ContentUnit objects
- Detect structural units: heading, paragraph, list, table, code, quote, formula
- Preserve source_order and parent relationships
- Assign initial depth based on heading level
- Assign preliminary structural content_type (refined later by classifier)

Rules
-----
- Never lose source content during segmentation.
- Preserve original order (source_order is monotonically increasing).
- Parent relationships are established by heading hierarchy.
- A heading followed by paragraphs forms a logical section.
- Empty sections are allowed (heading with no body) but warned.

Input contract
--------------
    NormalizedDocument (from InputNormalizer)

Output contract
---------------
    SegmentationResult
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field

from app.core.exceptions import SegmentationError
from app.core.logging import get_logger
from app.intelligence.normalizer import NormalizedDocument
from app.intelligence.schemas import ContentType, ContentUnit

log = get_logger(__name__)

# ── Regex patterns ────────────────────────────────────────────────────────────

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_CODE_FENCE_RE = re.compile(r"^```[\w]*\n.*?^```", re.MULTILINE | re.DOTALL)
_TABLE_BLOCK_RE = re.compile(
    r"(?:^\|.+\|\n)+(?:^\|[-|: ]+\|\n)?(?:^\|.+\|\n)*", re.MULTILINE
)
_BLOCKQUOTE_RE = re.compile(r"((?:^>+[^\n]*\n?)+)", re.MULTILINE)
_FORMULA_BLOCK_RE = re.compile(r"\$\$.*?\$\$", re.DOTALL)
_BULLET_LIST_RE = re.compile(r"((?:^[ \t]*[-*+] .+\n?)+)", re.MULTILINE)
_NUMBERED_LIST_RE = re.compile(r"((?:^[ \t]*\d+[.)].+\n?)+)", re.MULTILINE)

# Minimum characters for a paragraph (very short lines are often captions/labels)
_MIN_PARAGRAPH_CHARS = 30


# ── Data classes ──────────────────────────────────────────────────────────────


@dataclass
class RawSegment:
    """Intermediate segmentation unit before ContentUnit creation."""

    order: int
    segment_type: str  # heading|paragraph|list_bullet|list_numbered|table|code|quote|formula|caption
    text: str
    heading_level: int = 0  # 1-6 for headings, 0 otherwise
    parent_order: int | None = None


@dataclass
class SegmentationResult:
    """Output of the segmentation phase.

    Fields
    ------
    source_hint : str
    content_units : list[ContentUnit]
        Ordered ContentUnits with structural content_type assigned.
        Semantic classification happens in a later stage.
    segmentation_warnings : list[str]
    total_segments : int
    """

    source_hint: str
    content_units: list[ContentUnit]
    segmentation_warnings: list[str] = field(default_factory=list)
    total_segments: int = 0


# ── Segment type → ContentType mapping (structural only) ─────────────────────

_STRUCTURAL_TYPE_MAP: dict[str, ContentType] = {
    "heading": ContentType.TITLE,
    "paragraph": ContentType.OTHER,
    "list_bullet": ContentType.SEQUENCE,
    "list_numbered": ContentType.SEQUENCE,
    "table": ContentType.DATA,
    "code": ContentType.PROCEDURE,
    "quote": ContentType.EVIDENCE,
    "formula": ContentType.FORMULA,
    "caption": ContentType.INTRODUCTION,
}


# ── Segmenter ─────────────────────────────────────────────────────────────────


class ContentSegmenter:
    """Splits a NormalizedDocument into ordered ContentUnits.

    Algorithm
    ---------
    1. Extract and protect special blocks (code, tables, formulas, quotes).
    2. Split remaining text by headings to get section boundaries.
    3. Within each section, split by paragraph boundaries.
    4. Detect list blocks within paragraphs.
    5. Build ContentUnit list with parent relationships.
    6. Assign structural content_type (heading → TITLE, list → SEQUENCE, etc.).
    """

    def segment(
        self,
        doc: NormalizedDocument,
        job_id: str | None = None,
    ) -> SegmentationResult:
        """Segment a NormalizedDocument into ContentUnits.

        Parameters
        ----------
        doc:
            Output of InputNormalizer.normalize().
        job_id:
            Active pipeline job ID for log context.

        Raises
        ------
        SegmentationError
            If no content units can be extracted.
        """
        log.debug(
            "segmenter.start",
            source_hint=doc.source_hint,
            job_id=job_id,
            word_count=doc.word_count,
        )

        text = doc.normalized_text
        warnings: list[str] = []
        raw_segments: list[RawSegment] = []

        # Step 1: Extract and protect special blocks
        text, specials = self._extract_specials(text, raw_segments)

        # Step 2: Split by headings
        self._split_by_headings(text, raw_segments, warnings)

        # Step 3: Sort all segments by order
        raw_segments.sort(key=lambda s: s.order)

        # Step 4: Establish parent relationships via heading stack
        self._assign_parents(raw_segments)

        # Step 5: Convert to ContentUnit objects
        units = self._build_units(raw_segments, doc.source_hint, warnings)

        if not units:
            raise SegmentationError(
                "Segmentation produced zero content units",
                job_id=job_id,
                step="segmentation",
                details={"source_hint": doc.source_hint, "text_length": len(doc.normalized_text)},
            )

        if len(units) < 3:
            warnings.append(
                f"Very few segments ({len(units)}) detected — source may be too short or structure unclear"
            )

        log.info(
            "segmenter.complete",
            source_hint=doc.source_hint,
            job_id=job_id,
            unit_count=len(units),
            warning_count=len(warnings),
        )

        return SegmentationResult(
            source_hint=doc.source_hint,
            content_units=units,
            segmentation_warnings=warnings,
            total_segments=len(units),
        )

    # ── Internal helpers ──────────────────────────────────────────────────

    def _extract_specials(
        self,
        text: str,
        raw_segments: list[RawSegment],
    ) -> tuple[str, list[RawSegment]]:
        """Extract special blocks (code, table, formula, quote) with placeholders."""

        order_counter = [0]  # mutable int via list trick

        def _placeholder(segment_type: str, content: str, m: re.Match) -> str:
            seg = RawSegment(
                order=m.start(),  # use char position as initial order key
                segment_type=segment_type,
                text=content.strip(),
            )
            raw_segments.append(seg)
            order_counter[0] += 1
            return f"\n\x00SPECIAL_{len(raw_segments) - 1}\x00\n"

        text = _CODE_FENCE_RE.sub(
            lambda m: _placeholder("code", m.group(0), m), text
        )
        text = _FORMULA_BLOCK_RE.sub(
            lambda m: _placeholder("formula", m.group(0), m), text
        )
        text = _TABLE_BLOCK_RE.sub(
            lambda m: _placeholder("table", m.group(0), m), text
        )
        text = _BLOCKQUOTE_RE.sub(
            lambda m: _placeholder("quote", m.group(0), m), text
        )

        return text, raw_segments

    def _split_by_headings(
        self,
        text: str,
        raw_segments: list[RawSegment],
        warnings: list[str],
    ) -> None:
        """Split text by headings and parse each section's body."""

        # Find all heading positions
        heading_matches = list(_HEADING_RE.finditer(text))

        if not heading_matches:
            # No headings — treat entire text as paragraphs
            self._parse_body(text, 0, None, raw_segments, warnings)
            return

        # Text before first heading
        if heading_matches[0].start() > 0:
            pre = text[: heading_matches[0].start()].strip()
            if pre:
                self._parse_body(pre, heading_matches[0].start() - len(pre), None, raw_segments, warnings)

        for idx, m in enumerate(heading_matches):
            level = len(m.group(1))
            heading_text = m.group(2).strip()

            # Add heading segment
            raw_segments.append(
                RawSegment(
                    order=m.start(),
                    segment_type="heading",
                    text=heading_text,
                    heading_level=level,
                )
            )

            # Body between this heading and the next
            body_start = m.end() + 1
            body_end = heading_matches[idx + 1].start() if idx + 1 < len(heading_matches) else len(text)
            body = text[body_start:body_end].strip()

            if body:
                self._parse_body(body, body_start, m.start(), raw_segments, warnings)
            else:
                warnings.append(f"Empty section body under heading: '{heading_text[:60]}'")

    def _parse_body(
        self,
        body: str,
        base_offset: int,
        parent_order: int | None,
        raw_segments: list[RawSegment],
        warnings: list[str],
    ) -> None:
        """Parse a section body into paragraphs and lists."""

        # Handle SPECIAL placeholders
        special_re = re.compile(r"\x00SPECIAL_(\d+)\x00")

        # Split into chunks by double newline (paragraph boundary)
        chunks = re.split(r"\n\n+", body)

        for chunk_idx, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if not chunk:
                continue

            # Is this chunk a SPECIAL placeholder?
            if special_re.fullmatch(chunk):
                # Already in raw_segments — set its parent
                special_idx = int(special_re.fullmatch(chunk).group(1))
                if special_idx < len(raw_segments):
                    raw_segments[special_idx].parent_order = parent_order
                continue

            # Detect bullet list
            if _BULLET_LIST_RE.fullmatch(chunk + "\n"):
                raw_segments.append(
                    RawSegment(
                        order=base_offset + chunk_idx,
                        segment_type="list_bullet",
                        text=chunk,
                        parent_order=parent_order,
                    )
                )
                continue

            # Detect numbered list
            if _NUMBERED_LIST_RE.fullmatch(chunk + "\n"):
                raw_segments.append(
                    RawSegment(
                        order=base_offset + chunk_idx,
                        segment_type="list_numbered",
                        text=chunk,
                        parent_order=parent_order,
                    )
                )
                continue

            # Regular paragraph
            if len(chunk) >= _MIN_PARAGRAPH_CHARS or any(c.isalpha() for c in chunk):
                raw_segments.append(
                    RawSegment(
                        order=base_offset + chunk_idx,
                        segment_type="paragraph",
                        text=chunk,
                        parent_order=parent_order,
                    )
                )
            elif chunk:
                # Short text — treat as caption
                raw_segments.append(
                    RawSegment(
                        order=base_offset + chunk_idx,
                        segment_type="caption",
                        text=chunk,
                        parent_order=parent_order,
                    )
                )

    def _assign_parents(self, segments: list[RawSegment]) -> None:
        """Assign heading-based parent relationships using a heading stack."""
        heading_stack: list[tuple[int, int]] = []  # (heading_level, order)

        for seg in segments:
            if seg.segment_type == "heading":
                level = seg.heading_level
                # Pop stack until we find a parent of higher level
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                if heading_stack:
                    seg.parent_order = heading_stack[-1][1]
                heading_stack.append((level, seg.order))

    def _build_units(
        self,
        raw_segments: list[RawSegment],
        source_hint: str,
        warnings: list[str],
    ) -> list[ContentUnit]:
        """Convert RawSegment list to ContentUnit list with stable ordering."""

        # Re-number by final sorted order
        units: list[ContentUnit] = []
        order_to_unit_id: dict[int, str] = {}

        for source_order, seg in enumerate(raw_segments):
            unit_id = str(uuid.uuid4())
            order_to_unit_id[seg.order] = unit_id

            content_type = _STRUCTURAL_TYPE_MAP.get(seg.segment_type, ContentType.OTHER)
            depth = seg.heading_level if seg.segment_type == "heading" else 0

            unit = ContentUnit(
                unit_id=unit_id,
                source_order=source_order,
                parent_id=None,  # resolved below
                raw_text=seg.text,
                normalized_text=seg.text,  # already normalized
                title=seg.text[:80] if seg.segment_type == "heading" else None,
                depth=depth,
                content_type=content_type,
                density_score=min(1.0, len(seg.text.split()) / 200),
            )
            units.append(unit)

        # Resolve parent_id references
        raw_order_to_uid = {
            seg.order: order_to_unit_id.get(seg.order)
            for seg in raw_segments
        }
        parent_order_map = {
            seg.order: seg.parent_order for seg in raw_segments
        }

        for source_order, unit in enumerate(units):
            seg = raw_segments[source_order]
            parent_order = parent_order_map.get(seg.order)
            if parent_order is not None:
                unit.parent_id = raw_order_to_uid.get(parent_order)

        return units
