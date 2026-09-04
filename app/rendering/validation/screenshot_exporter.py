"""
KIR AI Document Intelligence — PDF Screenshot Exporter & Visual Truth Inspector.

Renders every physical page of a generated PDF into high-resolution PNG images
and verifies visual invariants (e.g. non-empty pages, pixel variance).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import pymupdf


class VisualPageReport:
    def __init__(self, page_number: int, image_path: str, is_blank: bool, text_content: str):
        self.page_number = page_number
        self.image_path = image_path
        self.is_blank = is_blank
        self.text_content = text_content


class PDFScreenshotExporter:
    """Exports PDF pages as PNG images and performs visual blank-page inspection."""

    def export_pages(
        self,
        pdf_path: Path | str,
        output_dir: Path | str,
        dpi: int = 150,
    ) -> list[VisualPageReport]:
        """Export all pages of the PDF to PNG screenshots in output_dir."""
        p_path = Path(pdf_path)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        # Clean existing png files to prevent leftover pages
        for old_img in out_dir.glob("page_*.png"):
            try:
                old_img.unlink()
            except Exception:
                pass

        if not p_path.exists():
            raise FileNotFoundError(f"PDF file does not exist: {p_path}")

        doc = pymupdf.open(str(p_path))
        reports: list[VisualPageReport] = []

        for page_idx, page in enumerate(doc, start=1):
            pix = page.get_pixmap(dpi=dpi)
            img_path = out_dir / f"page_{page_idx}.png"
            pix.save(str(img_path))

            text = page.get_text().strip()
            
            # Check if page is blank: text is empty and pixmap has uniform color
            # Sample samples buffer to test for emptiness
            samples = pix.samples
            is_uniform = len(set(samples[::100])) <= 1  # Fast uniformity heuristic
            is_blank = (len(text) == 0) and is_uniform

            reports.append(
                VisualPageReport(
                    page_number=page_idx,
                    image_path=str(img_path.resolve()),
                    is_blank=is_blank,
                    text_content=text,
                )
            )

        doc.close()
        return reports
