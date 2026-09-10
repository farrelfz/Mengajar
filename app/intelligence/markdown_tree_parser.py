"""
Deterministic Markdown Structural Tree Parser.

Converts raw Markdown documents into a canonical ContentTree with stable,
hierarchical section IDs and fine-grained semantic content blocks.
"""

from __future__ import annotations

import re
import uuid
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class SemanticBlockType(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    BULLET_LIST = "bullet_list"
    NUMBERED_LIST = "numbered_list"
    TABLE = "table"
    FORMULA = "formula"
    WARNING = "warning"
    COMPARISON = "comparison"
    DIAGRAM = "diagram"
    ASCII_DIAGRAM = "ascii_diagram"
    PROCEDURE = "procedure"
    QUESTION = "question"
    CRITICAL_THINKING = "critical_thinking"
    CONCLUSION = "conclusion"
    SUMMARY = "summary"
    RISK_MATRIX = "risk_matrix"
    CHECKLIST = "checklist"
    DEFINITION = "definition"
    OBSERVATION_DATA = "observation_data"
    CODE = "code"


class ContentBlock(BaseModel):
    """Atomic content unit parsed deterministically from Markdown."""
    id: str
    type: SemanticBlockType
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_line_start: int = 0
    source_line_end: int = 0


class ContentSection(BaseModel):
    """Hierarchical section node within a ContentTree."""
    id: str
    level: int
    title: str
    blocks: list[ContentBlock] = Field(default_factory=list)
    children: list[ContentSection] = Field(default_factory=list)
    parent_id: str | None = None

    def all_blocks_recursive(self) -> list[ContentBlock]:
        """Collect all blocks within this section and its child sections."""
        collected = list(self.blocks)
        for child in self.children:
            collected.extend(child.all_blocks_recursive())
        return collected


class ContentTree(BaseModel):
    """Canonical intermediate representation of parsed Markdown content."""
    document_id: str
    title: str
    sections: list[ContentSection] = Field(default_factory=list)
    total_blocks_count: int = 0
    total_sections_count: int = 0

    def all_sections_flat(self) -> list[ContentSection]:
        """Return a flattened list of all sections in depth-first order."""
        result: list[ContentSection] = []

        def _traverse(sec: ContentSection):
            result.append(sec)
            for child in sec.children:
                _traverse(child)

        for sec in self.sections:
            _traverse(sec)
        return result

    def all_blocks_flat(self) -> list[ContentBlock]:
        """Return all blocks across the entire document."""
        result: list[ContentBlock] = []
        for sec in self.all_sections_flat():
            result.extend(sec.blocks)
        return result

    def get_section(self, section_id: str) -> ContentSection | None:
        for sec in self.all_sections_flat():
            if sec.id == section_id:
                return sec
        return None

    def get_block(self, block_id: str) -> ContentBlock | None:
        for blk in self.all_blocks_flat():
            if blk.id == block_id:
                return blk
        return None


def slugify_id(text: str, prefix: str = "sec") -> str:
    """Generate a clean, deterministic, URL-friendly slug ID."""
    clean = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    slug = re.sub(r"[-\s]+", "-", clean)
    slug = slug[:50] if slug else f"item-{uuid.uuid4().hex[:6]}"
    return f"{prefix}-{slug}"


class MarkdownTreeParser:
    """Deterministic structural parser transforming Markdown into ContentTree."""

    _HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
    _TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")
    _TABLE_SEP_RE = re.compile(r"^\|[-: |]+\|$")
    _BLOCKQUOTE_RE = re.compile(r"^>\s?(.*)$")
    _BULLET_RE = re.compile(r"^[ \t]*[-*+]\s+(.+)$")
    _NUMBERED_RE = re.compile(r"^[ \t]*(\d+)[.)]\s+(.+)$")
    _FORMULA_BLOCK_RE = re.compile(r"^\$\$(.*?)\$\$$", re.DOTALL)
    _CODE_FENCE_RE = re.compile(r"^```(\w*)")

    def parse(self, markdown_text: str, document_title: str | None = None) -> ContentTree:
        """Parse raw markdown text into a structured ContentTree."""
        lines = markdown_text.splitlines()
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"

        # Detect primary document title if not provided
        detected_title = document_title
        if not detected_title:
            for line in lines:
                h_match = self._HEADING_RE.match(line.strip())
                if h_match and len(h_match.group(1)) == 1:
                    raw_title = h_match.group(2).strip()
                    # Strip emojis and leading icons
                    detected_title = re.sub(r"^[^\w\s]+", "", raw_title).strip() or raw_title
                    break
        if not detected_title:
            detected_title = "Dokumen Presentasi Pembelajaran"

        root_sections: list[ContentSection] = []
        section_stack: list[ContentSection] = []

        # Virtual root section if content appears before first heading
        current_section: ContentSection | None = None

        def get_active_section() -> ContentSection:
            nonlocal current_section, root_sections
            if current_section is None:
                current_section = ContentSection(
                    id="section-overview",
                    level=1,
                    title=detected_title,
                )
                root_sections.append(current_section)
                section_stack.append(current_section)
            return current_section

        i = 0
        total_lines = len(lines)

        while i < total_lines:
            line = lines[i]
            stripped = line.strip()

            if not stripped:
                i += 1
                continue

            # Skip horizontal divider rules
            if re.match(r"^[-*_]{3,}$", stripped):
                i += 1
                continue

            # 1. Heading check
            h_match = self._HEADING_RE.match(stripped)
            if h_match:
                level = len(h_match.group(1))
                raw_title = h_match.group(2).strip()
                title_clean = re.sub(r"^[^\w\s]+", "", raw_title).strip() or raw_title
                sec_id = slugify_id(title_clean, prefix=f"sec-l{level}")

                # Guarantee unique section ID
                existing_ids = {s.id for s in root_sections}
                suffix_count = 1
                unique_sec_id = sec_id
                while unique_sec_id in existing_ids:
                    unique_sec_id = f"{sec_id}-{suffix_count}"
                    suffix_count += 1

                new_section = ContentSection(
                    id=unique_sec_id,
                    level=level,
                    title=title_clean,
                )

                # Pop sections of same or deeper level from stack
                while section_stack and section_stack[-1].level >= level:
                    section_stack.pop()

                if section_stack:
                    new_section.parent_id = section_stack[-1].id
                    section_stack[-1].children.append(new_section)
                else:
                    root_sections.append(new_section)

                section_stack.append(new_section)
                current_section = new_section
                i += 1
                continue

            active_sec = get_active_section()

            # 2. Code fence / ASCII Diagram check
            fence_match = self._CODE_FENCE_RE.match(stripped)
            if fence_match:
                code_lines: list[str] = []
                lang = fence_match.group(1)
                start_line = i
                i += 1
                while i < total_lines and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                if i < total_lines:
                    i += 1  # consume closing fence
                raw_code = "\n".join(code_lines)
                is_diagram = any(sym in raw_code for sym in ["-->", "---", "+--", "|", " / ", "\\", "<--"]) or lang in ["mermaid", "ascii", "diagram"]
                b_type = SemanticBlockType.ASCII_DIAGRAM if is_diagram else SemanticBlockType.CODE
                blk_id = f"block-{active_sec.id}-code-{len(active_sec.blocks) + 1}"
                active_sec.blocks.append(
                    ContentBlock(
                        id=blk_id,
                        type=b_type,
                        content=raw_code,
                        metadata={"language": lang, "is_diagram": is_diagram},
                        source_line_start=start_line,
                        source_line_end=i,
                    )
                )
                continue

            # 3. Formula block check ($$ ... $$)
            if stripped.startswith("$$"):
                formula_lines: list[str] = []
                start_line = i
                if stripped.endswith("$$") and len(stripped) > 2:
                    formula_lines.append(stripped[2:-2].strip())
                    i += 1
                else:
                    i += 1
                    while i < total_lines and not lines[i].strip().endswith("$$"):
                        formula_lines.append(lines[i])
                        i += 1
                    if i < total_lines:
                        end_line = lines[i].strip()
                        if end_line != "$$":
                            formula_lines.append(end_line[:-2].strip())
                        i += 1
                formula_str = "\n".join(formula_lines).strip()
                blk_id = f"block-{active_sec.id}-formula-{len(active_sec.blocks) + 1}"
                active_sec.blocks.append(
                    ContentBlock(
                        id=blk_id,
                        type=SemanticBlockType.FORMULA,
                        content=formula_str,
                        metadata={"latex": formula_str},
                        source_line_start=start_line,
                        source_line_end=i,
                    )
                )
                continue

            # 4. Table check
            if self._TABLE_ROW_RE.match(stripped):
                table_lines: list[str] = []
                start_line = i
                while i < total_lines and self._TABLE_ROW_RE.match(lines[i].strip()):
                    table_lines.append(lines[i].strip())
                    i += 1
                table_content = "\n".join(table_lines)
                parsed_table = self._parse_markdown_table(table_lines)
                blk_id = f"block-{active_sec.id}-table-{len(active_sec.blocks) + 1}"
                
                # Check if table is risk matrix or observation data
                t_lower = table_content.lower()
                is_risk = any(k in t_lower for k in ["bahaya", "risiko", "pencegahan", "mitigasi", "k3", "hazard"])
                is_obs = any(k in t_lower for k in ["pengamatan", "observasi", "hasil", "ulangan", "triplo", "tinggi"])
                
                table_block_type = SemanticBlockType.RISK_MATRIX if is_risk else (SemanticBlockType.OBSERVATION_DATA if is_obs else SemanticBlockType.TABLE)

                active_sec.blocks.append(
                    ContentBlock(
                        id=blk_id,
                        type=table_block_type,
                        content=table_content,
                        metadata=parsed_table,
                        source_line_start=start_line,
                        source_line_end=i,
                    )
                )
                continue

            # 5. Blockquote / Warning check
            if stripped.startswith(">"):
                quote_lines: list[str] = []
                start_line = i
                while i < total_lines and lines[i].strip().startswith(">"):
                    q_line = re.sub(r"^>\s?", "", lines[i].strip())
                    quote_lines.append(q_line)
                    i += 1
                quote_text = "\n".join(quote_lines).strip()
                is_warning = any(w in quote_text.lower() for w in ["peringatan", "warning", "bahaya", "hati-hati", "caution", "safety", "k3"])
                b_type = SemanticBlockType.WARNING if is_warning else SemanticBlockType.PARAGRAPH
                blk_id = f"block-{active_sec.id}-quote-{len(active_sec.blocks) + 1}"
                active_sec.blocks.append(
                    ContentBlock(
                        id=blk_id,
                        type=b_type,
                        content=quote_text,
                        metadata={"is_warning": is_warning},
                        source_line_start=start_line,
                        source_line_end=i,
                    )
                )
                continue

            # 6. Bullet List check
            if self._BULLET_RE.match(stripped):
                list_items: list[str] = []
                start_line = i
                while i < total_lines and (self._BULLET_RE.match(lines[i].strip()) or (lines[i].startswith("   ") and list_items)):
                    item_m = self._BULLET_RE.match(lines[i].strip())
                    if item_m:
                        list_items.append(item_m.group(1).strip())
                    elif list_items:
                        list_items[-1] += " " + lines[i].strip()
                    i += 1
                list_text = "\n".join(f"- {it}" for it in list_items)
                blk_id = f"block-{active_sec.id}-bullet-{len(active_sec.blocks) + 1}"
                
                # Check for comparison signals (e.g. Konduksi vs Konveksi vs Radiasi)
                is_comparison = len(list_items) >= 2 and all(":" in it or "**" in it for it in list_items) and any(
                    comp_w in active_sec.title.lower() or comp_w in list_text.lower() for comp_w in ["perpindahan", "jenis", "perbedaan", "versus", "komponen", "konduksi"]
                )
                b_type = SemanticBlockType.COMPARISON if is_comparison else SemanticBlockType.BULLET_LIST

                active_sec.blocks.append(
                    ContentBlock(
                        id=blk_id,
                        type=b_type,
                        content=list_text,
                        metadata={"items": list_items, "is_comparison": is_comparison},
                        source_line_start=start_line,
                        source_line_end=i,
                    )
                )
                continue

            # 7. Numbered List check (Procedures, objectives, questions)
            first_num_m = self._NUMBERED_RE.match(stripped)
            if first_num_m:
                num_items: list[tuple[int, str]] = []
                start_line = i
                while i < total_lines:
                    curr_stripped = lines[i].strip()
                    n_match = self._NUMBERED_RE.match(curr_stripped)
                    if not n_match:
                        break
                    num = int(n_match.group(1))
                    val = n_match.group(2).strip()
                    num_items.append((num, val))
                    i += 1
                num_text = "\n".join(f"{num}. {val}" for num, val in num_items)
                blk_id = f"block-{active_sec.id}-numlist-{len(active_sec.blocks) + 1}"
                
                sec_lower = active_sec.title.lower()
                is_procedure = any(p in sec_lower for p in ["prosedur", "langkah", "tahapan", "cara kerja", "metode", "aktivitas"])
                is_question = any(q in sec_lower for q in ["pertanyaan", "diskusi", "analisis", "refleksi", "evaluasi", "rumusan"])
                
                b_type = SemanticBlockType.PROCEDURE if is_procedure else (SemanticBlockType.QUESTION if is_question else SemanticBlockType.NUMBERED_LIST)

                active_sec.blocks.append(
                    ContentBlock(
                        id=blk_id,
                        type=b_type,
                        content=num_text,
                        metadata={"items": [v for _, v in num_items], "is_procedure": is_procedure},
                        source_line_start=start_line,
                        source_line_end=i,
                    )
                )
                continue

            # 8. Regular Paragraph (with inline formula check)
            start_line = i
            para_lines: list[str] = []
            while i < total_lines:
                curr = lines[i].strip()
                if not curr:
                    break
                if (self._HEADING_RE.match(curr) or self._TABLE_ROW_RE.match(curr)
                        or curr.startswith(">") or self._BULLET_RE.match(curr)
                        or self._NUMBERED_RE.match(curr) or curr.startswith("$$")
                        or curr.startswith("```")):
                    break
                para_lines.append(lines[i].strip())
                i += 1

            para_text = " ".join(para_lines).strip()
            if para_text:
                blk_id = f"block-{active_sec.id}-p-{len(active_sec.blocks) + 1}"
                p_lower = para_text.lower()
                
                # Semantic detection on paragraph content
                is_formula = ("=" in para_text and any(sym in para_text for sym in ["\\Delta", "\\rightarrow", "->", "+", "\\times", "Q ="]))
                is_question = ("?" in para_text and any(qw in p_lower for qw in ["mengapa", "bagaimana", "apakah", "kenapa", "why", "how"]))
                is_definition = any(dw in p_lower for dw in ["merupakan", "adalah", "didefinisikan", "yaitu", "artinya"])
                is_conclusion = any(cw in p_lower for cw in ["kesimpulan", "disimpulkan", "dengan demikian", "hasil akhirnya"])

                b_type = (
                    SemanticBlockType.FORMULA if is_formula
                    else SemanticBlockType.QUESTION if is_question
                    else SemanticBlockType.CONCLUSION if is_conclusion
                    else SemanticBlockType.DEFINITION if is_definition
                    else SemanticBlockType.PARAGRAPH
                )

                active_sec.blocks.append(
                    ContentBlock(
                        id=blk_id,
                        type=b_type,
                        content=para_text,
                        metadata={"is_formula": is_formula, "is_question": is_question},
                        source_line_start=start_line,
                        source_line_end=i,
                    )
                )

        tree = ContentTree(
            document_id=doc_id,
            title=detected_title,
            sections=root_sections,
            total_sections_count=len(root_sections),
            total_blocks_count=sum(len(s.all_blocks_recursive()) for s in root_sections),
        )
        return tree

    def _parse_markdown_table(self, table_lines: list[str]) -> dict[str, Any]:
        """Extract structured headers and rows from markdown table."""
        if not table_lines:
            return {"headers": [], "rows": []}
        headers: list[str] = []
        rows: list[list[str]] = []
        for line in table_lines:
            if self._TABLE_SEP_RE.match(line):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not headers:
                headers = cells
            else:
                rows.append(cells)
        return {"headers": headers, "rows": rows, "row_count": len(rows), "col_count": len(headers)}
