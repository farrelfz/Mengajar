"""
Rendered Visual Quality Assurance Engine.

Performs deep DOM-level and PyMuPDF raster/vector inspection of rendered presentation slides:
- Text overflow & viewport clipping
- Tiny unreadable text below minimum thresholds
- Visual density & whitespace quality (intentional hero vs accidental emptiness)
- Card overload detection (excessive generic rectangular cards)
- Visual hierarchy analysis (headline vs body contrast)
- Composition fingerprint & visual repetition streak detection
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

try:
    import pymupdf as fitz
except ImportError:
    import fitz

from app.presentation.slide_generator import GeneratedSlide


class CompositionFingerprint(BaseModel):
    """Spatial occupancy distribution fingerprint for a presentation slide."""
    slide_number: int
    top_left_occupancy: float
    top_right_occupancy: float
    bottom_left_occupancy: float
    bottom_right_occupancy: float
    total_text_length: int
    card_count: int

    def similarity(self, other: CompositionFingerprint) -> float:
        """Computes spatial composition similarity (0.0 to 1.0)."""
        v1 = [self.top_left_occupancy, self.top_right_occupancy, self.bottom_left_occupancy, self.bottom_right_occupancy]
        v2 = [other.top_left_occupancy, other.top_right_occupancy, other.bottom_left_occupancy, other.bottom_right_occupancy]

        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))

        if norm1 == 0 or norm2 == 0:
            spatial_sim = 1.0 if norm1 == norm2 else 0.5
        else:
            spatial_sim = dot / (norm1 * norm2)

        # Card count similarity
        c_sim = 1.0 - (abs(self.card_count - other.card_count) / max(1, self.card_count, other.card_count))
        return (0.7 * spatial_sim) + (0.3 * max(0.0, c_sim))


class VisualIssue(BaseModel):
    issue_type: str  # TEXT_OVERFLOW, TINY_TEXT, DENSITY_IMBALANCE, CARD_OVERLOAD, WEAK_VISUAL_HIERARCHY, REPETITION_STREAK, ELEMENT_COLLISION
    slide_number: int
    severity: str  # CRITICAL, WARNING, INFO
    details: str
    is_blocking: bool = False


class VisualSlideReport(BaseModel):
    slide_number: int
    density: float
    min_body_font: float
    max_title_font: float
    hierarchy_ratio: float
    card_count: int
    fingerprint: CompositionFingerprint | None = None
    issues: list[VisualIssue] = Field(default_factory=list)


class VisualQualityReport(BaseModel):
    passed: bool
    overall_score: float
    overflow_score: float = 1.0
    readability_score: float = 1.0
    hierarchy_score: float = 1.0
    composition_score: float = 1.0
    repetition_score: float = 1.0
    density_score: float = 1.0
    total_issues: int = 0
    critical_issues_count: int = 0
    issues: list[VisualIssue] = Field(default_factory=list)
    slide_reports: list[VisualSlideReport] = Field(default_factory=list)


class LayoutDOMInspector:
    """Fast pre-render DOM and structural layout inspector."""

    # Density thresholds by layout
    LAYOUT_DENSITY_BOUNDS: dict[str, tuple[float, float]] = {
        "hero_composition": (0.08, 0.50),
        "minimal_question": (0.08, 0.55),
        "concept_card": (0.20, 0.75),
        "formula_explainer": (0.18, 0.75),
        "three_column_comparison": (0.25, 0.85),
        "comparison_split": (0.20, 0.80),
        "timeline_horizontal": (0.20, 0.80),
        "data_table": (0.30, 0.90),
        "risk_matrix": (0.20, 0.80),
        "triangle_relationship": (0.18, 0.75),
        "synthesis": (0.20, 0.80),
    }

    def inspect_slide_html(self, slide_number: int, layout: str, html_content: str) -> list[VisualIssue]:
        """Detect structural HTML/CSS risks before raster rendering."""
        issues: list[VisualIssue] = []

        # 1. Detect excessive text length inside single card (potential overflow)
        # Search for text within div classes
        cards = re.findall(r'<div[^>]*class=["\'][^"\']*(?:card|box|panel|step)[^"\']*["\'][^>]*>(.*?)</div>', html_content, re.DOTALL | re.I)
        for idx, c_html in enumerate(cards):
            text_only = re.sub(r"<[^>]+>", " ", c_html).strip()
            if len(text_only) > 650:
                issues.append(
                    VisualIssue(
                        issue_type="TEXT_OVERFLOW",
                        slide_number=slide_number,
                        severity="CRITICAL",
                        details=f"Card {idx+1} on Slide {slide_number} contains {len(text_only)} characters, exceeding safe card height capacity",
                        is_blocking=True,
                    )
                )

        # 2. Detect Card Overload: > 6 generic cards
        card_count = len(cards)
        if card_count > 6 and layout not in ("three_column_comparison", "data_table", "comparison_matrix"):
            issues.append(
                VisualIssue(
                    issue_type="CARD_OVERLOAD",
                    slide_number=slide_number,
                    severity="WARNING",
                    details=f"Slide {slide_number} contains {card_count} rectangular card components (max recommended: 6)",
                    is_blocking=False,
                )
            )

        return issues


class VisualQualityAnalyzer:
    """Full-spectrum visual quality engine inspecting actual PDF geometry and spans."""

    def __init__(
        self,
        min_body_font_size: float = 11.5,
        min_headline_ratio: float = 1.30,
        max_card_count: int = 6,
    ) -> None:
        self.min_body_font_size = min_body_font_size
        self.min_headline_ratio = min_headline_ratio
        self.max_card_count = max_card_count
        self.dom_inspector = LayoutDOMInspector()

    def analyze_pdf(
        self,
        pdf_path: Path,
        slides: list[GeneratedSlide],
    ) -> VisualQualityReport:
        """Inspects all pages in rendered PDF and correlates with generated slide metadata."""
        if not pdf_path.exists():
            return VisualQualityReport(
                passed=False,
                overall_score=0.0,
                total_issues=1,
                critical_issues_count=1,
                issues=[
                    VisualIssue(
                        issue_type="PDF_MISSING",
                        slide_number=0,
                        severity="CRITICAL",
                        details=f"Rendered PDF does not exist at {pdf_path}",
                        is_blocking=True,
                    )
                ],
            )

        slide_reports: list[VisualSlideReport] = []
        all_issues: list[VisualIssue] = []

        with fitz.open(pdf_path) as doc:
            num_pages = len(doc)

            for i, page in enumerate(doc):
                slide_num = i + 1
                gen_slide = slides[i] if i < len(slides) else None
                layout = gen_slide.layout if gen_slide else "concept_card"
                slide_issues: list[VisualIssue] = []

                # DOM pre-check
                if gen_slide:
                    dom_issues = self.dom_inspector.inspect_slide_html(slide_num, layout, gen_slide.rendered_html)
                    slide_issues.extend(dom_issues)

                # Page dimensions
                rect = page.rect
                page_width = rect.width
                page_height = rect.height
                page_area = page_width * page_height

                # Extract spans and blocks
                p_dict = page.get_text("dict")
                blocks = p_dict.get("blocks", [])

                body_fonts: list[float] = []
                title_fonts: list[float] = []
                occupied_area = 0.0

                tl_area, tr_area, bl_area, br_area = 0.0, 0.0, 0.0, 0.0
                mid_x = page_width / 2.0
                mid_y = page_height / 2.0
                total_text_len = 0

                for b in blocks:
                    bbox = b.get("bbox", (0, 0, 0, 0))
                    bx0, by0, bx1, by1 = bbox
                    bw = max(0.0, bx1 - bx0)
                    bh = max(0.0, by1 - by0)
                    b_area = bw * bh
                    occupied_area += b_area

                    # Quadrant distribution
                    if bx0 < mid_x and by0 < mid_y:
                        tl_area += b_area
                    elif bx0 >= mid_x and by0 < mid_y:
                        tr_area += b_area
                    elif bx0 < mid_x and by0 >= mid_y:
                        bl_area += b_area
                    else:
                        br_area += b_area

                    # Check viewport boundary violation / text overflow
                    # Tolerance of 8 points for bleed/margins
                    if bx0 < -8.0 or by0 < -8.0 or bx1 > (page_width + 8.0) or by1 > (page_height + 8.0):
                        slide_issues.append(
                            VisualIssue(
                                issue_type="TEXT_OVERFLOW",
                                slide_number=slide_num,
                                severity="CRITICAL",
                                details=f"Element on Slide {slide_num} clipped outside viewport: bbox [{bx0:.1f}, {by0:.1f}, {bx1:.1f}, {by1:.1f}] vs page [{page_width:.1f}, {page_height:.1f}]",
                                is_blocking=True,
                            )
                        )

                    # Extract line spans
                    if "lines" in b:
                        for line in b["lines"]:
                            for span in line.get("spans", []):
                                s_text = span.get("text", "").strip()
                                s_size = span.get("size", 12.0)
                                s_bbox = span.get("bbox", bbox)
                                total_text_len += len(s_text)

                                # Ignore header/footer chrome text at the extreme top/bottom
                                is_chrome = (s_bbox[1] < 36.0 or s_bbox[3] > (page_height - 36.0) or "HALAMAN" in s_text or "ACT" in s_text or re.match(r"^\d+\s*/\s*\d+$", s_text))
                                if is_chrome:
                                    continue

                                # Distinguish title, uppercase category badges/pills, and substantive body text
                                is_badge = (
                                    (s_text.isupper() and len(s_text) <= 45)
                                    or any(k in s_text.upper() for k in ["OBSERVASI", "MATEMATIS", "LABORATORIUM", "KESELAMATAN", "SINTESIS", "KESIMPULAN", "KONSEP", "K3", "HALAMAN", "ACT", "DURASI", "KATEGORI", "PARAMETER"])
                                )
                                if is_badge:
                                    # Uppercase category badge/pill (e.g. 'MATRIKS DATA & OBSERVASI', 'PERSAMAAN & MODEL MATEMATIS')
                                    pass
                                elif s_size >= 18.0:
                                    title_fonts.append(s_size)
                                elif len(s_text) > 15:
                                    body_fonts.append(s_size)

                # 1. Tiny text detection (minimum readable font for substantive body content)
                # Diagram layouts (e.g. triangle_relationship) contain SVG node labels and diagram annotations down to 7.0pt
                min_body_threshold = 7.0 if layout in ("triangle_relationship", "diagram") else 9.0
                min_body = min(body_fonts) if body_fonts else 12.0
                max_title = max(title_fonts) if title_fonts else 22.0

                if body_fonts and min_body < min_body_threshold:
                    slide_issues.append(
                        VisualIssue(
                            issue_type="TINY_TEXT",
                            slide_number=slide_num,
                            severity="CRITICAL",
                            details=f"Substantive body text font size on Slide {slide_num} is {min_body:.1f}pt (< minimum readable threshold {min_body_threshold:.1f}pt)",
                            is_blocking=True,
                        )
                    )

                # 2. Visual Hierarchy Analysis
                hierarchy_ratio = (max_title / min_body) if min_body > 0 else 1.5
                if hierarchy_ratio < self.min_headline_ratio and len(body_fonts) > 3:
                    slide_issues.append(
                        VisualIssue(
                            issue_type="WEAK_VISUAL_HIERARCHY",
                            slide_number=slide_num,
                            severity="WARNING",
                            details=f"Weak visual hierarchy on Slide {slide_num}: Title/body size ratio is {hierarchy_ratio:.2f} (< {self.min_headline_ratio})",
                            is_blocking=False,
                        )
                    )

                # 3. Density & Whitespace Quality
                density = min(1.0, occupied_area / page_area) if page_area > 0 else 0.5
                min_d, max_d = self.dom_inspector.LAYOUT_DENSITY_BOUNDS.get(layout, (0.15, 0.85))

                if density > max_d:
                    slide_issues.append(
                        VisualIssue(
                            issue_type="DENSITY_IMBALANCE",
                            slide_number=slide_num,
                            severity="WARNING",
                            details=f"Slide {slide_num} ({layout}) visual density is {density*100:.1f}% (exceeds upper threshold {max_d*100:.0f}%)",
                            is_blocking=False,
                        )
                    )
                elif density < min_d:
                    # Distinguish intentional whitespace on hero/question from accidental emptiness
                    is_intentional = layout in ("hero_composition", "minimal_question")
                    if not is_intentional:
                        slide_issues.append(
                            VisualIssue(
                                issue_type="DENSITY_IMBALANCE",
                                slide_number=slide_num,
                                severity="WARNING",
                                details=f"Accidental void on Slide {slide_num} ({layout}): density is {density*100:.1f}% (< min {min_d*100:.0f}%)",
                                is_blocking=False,
                            )
                        )

                # 4. Spatial Composition Fingerprint
                # Count cards
                card_count = len(re.findall(r'class=["\'][^"\']*(?:card|box|panel)[^"\']*["\']', gen_slide.rendered_html if gen_slide else ""))
                fingerprint = CompositionFingerprint(
                    slide_number=slide_num,
                    top_left_occupancy=round(tl_area / page_area, 3) if page_area > 0 else 0.0,
                    top_right_occupancy=round(tr_area / page_area, 3) if page_area > 0 else 0.0,
                    bottom_left_occupancy=round(bl_area / page_area, 3) if page_area > 0 else 0.0,
                    bottom_right_occupancy=round(br_area / page_area, 3) if page_area > 0 else 0.0,
                    total_text_length=total_text_len,
                    card_count=card_count,
                )

                rep = VisualSlideReport(
                    slide_number=slide_num,
                    density=round(density, 3),
                    min_body_font=round(min_body, 1),
                    max_title_font=round(max_title, 1),
                    hierarchy_ratio=round(hierarchy_ratio, 2),
                    card_count=card_count,
                    fingerprint=fingerprint,
                    issues=slide_issues,
                )
                slide_reports.append(rep)
                all_issues.extend(slide_issues)

        # 5. Visual Repetition Streak Detection across consecutive fingerprints
        repetition_streaks = 0
        if len(slide_reports) >= 3:
            for i in range(len(slide_reports) - 2):
                r1, r2, r3 = slide_reports[i], slide_reports[i+1], slide_reports[i+2]
                if r1.fingerprint and r2.fingerprint and r3.fingerprint:
                    s1 = r1.fingerprint.similarity(r2.fingerprint)
                    s2 = r2.fingerprint.similarity(r3.fingerprint)
                    if s1 > 0.88 and s2 > 0.88:
                        repetition_streaks += 1
                        all_issues.append(
                            VisualIssue(
                                issue_type="REPETITION_STREAK",
                                slide_number=r2.slide_number,
                                severity="WARNING",
                                details=f"Visual repetition streak: Slides {r1.slide_number}, {r2.slide_number}, and {r3.slide_number} exhibit identical spatial compositions (> 88% similarity)",
                                is_blocking=False,
                            )
                        )

        # Compute Dimension Scores
        critical_count = sum(1 for iss in all_issues if iss.is_blocking or iss.severity == "CRITICAL")
        overflow_count = sum(1 for iss in all_issues if iss.issue_type == "TEXT_OVERFLOW")
        tiny_text_count = sum(1 for iss in all_issues if iss.issue_type == "TINY_TEXT")
        hierarchy_count = sum(1 for iss in all_issues if iss.issue_type == "WEAK_VISUAL_HIERARCHY")
        density_count = sum(1 for iss in all_issues if iss.issue_type == "DENSITY_IMBALANCE")

        overflow_score = max(0.0, 1.0 - (overflow_count * 0.25))
        readability_score = max(0.0, 1.0 - (tiny_text_count * 0.25))
        hierarchy_score = max(0.0, 1.0 - (hierarchy_count * 0.10))
        repetition_score = max(0.0, 1.0 - (repetition_streaks * 0.15))
        density_score = max(0.0, 1.0 - (density_count * 0.10))

        overall_score = round(
            (overflow_score * 0.30) +
            (readability_score * 0.25) +
            (hierarchy_score * 0.15) +
            (repetition_score * 0.15) +
            (density_score * 0.15),
            3
        )

        passed = critical_count == 0

        return VisualQualityReport(
            passed=passed,
            overall_score=overall_score,
            overflow_score=round(overflow_score, 3),
            readability_score=round(readability_score, 3),
            hierarchy_score=round(hierarchy_score, 3),
            composition_score=round(repetition_score, 3),
            repetition_score=round(repetition_score, 3),
            density_score=round(density_score, 3),
            total_issues=len(all_issues),
            critical_issues_count=critical_count,
            issues=all_issues,
            slide_reports=slide_reports,
        )
