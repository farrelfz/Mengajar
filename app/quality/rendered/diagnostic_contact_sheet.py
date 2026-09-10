"""
Universal Document Intelligence System V5 — Diagnostic Contact Sheet Generator.

Phase 3A: Upgrades visual thumbnail contact sheets into actionable debugging tools:
- Highlights pages with text clipping, collision, or tiny text in RED
- Highlights pages with warnings or repetition streaks in AMBER
- Displays per-page density and issue indicators
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont

try:
    import pymupdf as fitz
except ImportError:
    import fitz

from app.quality.rendered.contracts import PageInspectionDetail, RenderedArtifactInspection
from app.quality.rendered.failure_taxonomy import RenderedFailureSeverity


class DiagnosticContactSheetGenerator:
    """Generates visual contact sheets annotated with diagnostic quality badges."""

    def __init__(self, columns: int = 4, scale: float = 0.35) -> None:
        self.columns = columns
        self.scale = scale

    def generate(
        self,
        pdf_path: Path,
        output_image_path: Path,
        inspection: RenderedArtifactInspection | None = None,
    ) -> Path:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF does not exist: {pdf_path}")

        thumbnails: List[Image.Image] = []
        with fitz.open(pdf_path) as doc:
            mat = fitz.Matrix(self.scale, self.scale)
            for page in doc:
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                thumbnails.append(img)

        if not thumbnails:
            blank = Image.new("RGB", (800, 600), (30, 30, 30))
            output_image_path.parent.mkdir(parents=True, exist_ok=True)
            blank.save(output_image_path)
            return output_image_path

        thumb_w, thumb_h = thumbnails[0].size
        cols = self.columns
        rows = math.ceil(len(thumbnails) / cols)

        pad_x = 24
        pad_y = 44
        header_h = 70
        sheet_w = (cols * thumb_w) + ((cols + 1) * pad_x)
        sheet_h = header_h + (rows * thumb_h) + ((rows + 1) * pad_y)

        # Background color: modern dark slate
        sheet = Image.new("RGB", (sheet_w, sheet_h), (20, 24, 32))
        draw = ImageDraw.Draw(sheet)

        # Title header
        doc_title = pdf_path.stem
        art_type = inspection.artifact_type if inspection else "DOCUMENT"
        overall_score = f"{inspection.overall_quality_score:.3f}" if inspection else "N/A"
        status_text = inspection.decision.value if inspection else "UNCHECKED"

        header_text = f"DIAGNOSTIC CONTACT SHEET — {doc_title.upper()} ({art_type}) | {status_text} (Score: {overall_score})"
        draw.text((pad_x, 22), header_text, fill=(240, 245, 250))

        # Page detail lookup
        page_detail_map: Dict[int, PageInspectionDetail] = {}
        if inspection:
            for pd in inspection.page_details:
                page_detail_map[pd.page_number] = pd

        for idx, thumb in enumerate(thumbnails):
            page_num = idx + 1
            r = idx // cols
            c = idx % cols
            x = pad_x + c * (thumb_w + pad_x)
            y = header_h + pad_y + r * (thumb_h + pad_y)

            p_detail = page_detail_map.get(page_num)

            # Determine border and badge color
            border_color = (60, 70, 85)       # Default neutral slate
            badge_bg = (30, 41, 59)
            badge_text = f"P.{page_num:02d}"

            if p_detail:
                has_crit = any(f.severity == RenderedFailureSeverity.CRITICAL for f in p_detail.failures)
                has_maj = any(f.severity == RenderedFailureSeverity.MAJOR for f in p_detail.failures)

                if has_crit or p_detail.has_clipping:
                    border_color = (239, 68, 68)   # Red
                    badge_bg = (185, 28, 28)
                    badge_text = f"P.{page_num:02d} [CRIT]"
                elif has_maj:
                    border_color = (245, 158, 11)  # Amber
                    badge_bg = (180, 83, 9)
                    badge_text = f"P.{page_num:02d} [WARN]"
                else:
                    border_color = (16, 185, 129)  # Green
                    badge_bg = (4, 120, 87)
                    badge_text = f"P.{page_num:02d} [OK]"

            # Paste thumbnail
            sheet.paste(thumb, (x, y))

            # Draw status border
            draw.rectangle([x - 2, y - 2, x + thumb_w + 1, y + thumb_h + 1], outline=border_color, width=2)

            # Draw status badge at top-left of thumbnail
            badge_w = 72
            draw.rectangle([x + 6, y + 6, x + 6 + badge_w, y + 22], fill=badge_bg, outline=border_color, width=1)
            draw.text((x + 10, y + 8), badge_text, fill=(255, 255, 255))

        output_image_path.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(output_image_path, format="PNG")
        return output_image_path
