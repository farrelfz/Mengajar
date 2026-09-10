"""
Presentation Visual Contact Sheet Generator.

Generates a 4-column visual thumbnail contact sheet from rendered PDF pages
for rapid visual quality inspection and QA review.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any
from PIL import Image, ImageDraw, ImageFont

try:
    import pymupdf as fitz
except ImportError:
    import fitz


class ContactSheetGenerator:
    """Renders PDF pages into a unified multi-column contact sheet grid."""

    def __init__(self, columns: int = 4, scale: float = 0.35) -> None:
        self.columns = columns
        self.scale = scale

    def generate(self, pdf_path: Path, output_image_path: Path) -> Path:
        """Renders all PDF pages into a contact sheet image."""
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF does not exist: {pdf_path}")

        thumbnails: list[Image.Image] = []
        with fitz.open(pdf_path) as doc:
            mat = fitz.Matrix(self.scale, self.scale)
            for page in doc:
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                thumbnails.append(img)

        if not thumbnails:
            # Fallback blank image
            blank = Image.new("RGB", (800, 600), (30, 30, 30))
            output_image_path.parent.mkdir(parents=True, exist_ok=True)
            blank.save(output_image_path)
            return output_image_path

        thumb_w, thumb_h = thumbnails[0].size
        cols = self.columns
        rows = math.ceil(len(thumbnails) / cols)

        pad_x = 24
        pad_y = 36
        header_h = 60
        sheet_w = (cols * thumb_w) + ((cols + 1) * pad_x)
        sheet_h = header_h + (rows * thumb_h) + ((rows + 1) * pad_y)

        # Background color: modern dark slate
        sheet = Image.new("RGB", (sheet_w, sheet_h), (24, 28, 36))
        draw = ImageDraw.Draw(sheet)

        # Title header
        title_text = f"Visual Contact Sheet — {pdf_path.stem} ({len(thumbnails)} slides)"
        draw.text((pad_x, 20), title_text, fill=(240, 243, 246))

        for idx, thumb in enumerate(thumbnails):
            r = idx // cols
            c = idx % cols
            x = pad_x + c * (thumb_w + pad_x)
            y = header_h + pad_y + r * (thumb_h + pad_y)

            # Paste thumbnail
            sheet.paste(thumb, (x, y))

            # Draw subtle border
            draw.rectangle([x - 1, y - 1, x + thumb_w, y + thumb_h], outline=(70, 80, 100), width=1)

            # Slide number badge
            badge_text = f"Slide {idx + 1:02d}"
            draw.rectangle([x + 6, y + 6, x + 62, y + 24], fill=(15, 23, 42, 220), outline=(56, 189, 248), width=1)
            draw.text((x + 10, y + 8), badge_text, fill=(255, 255, 255))

        output_image_path.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(output_image_path, format="PNG")
        return output_image_path
