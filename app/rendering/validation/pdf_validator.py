"""
KIR AI Document Intelligence — Real PDF Validation.
"""
from __future__ import annotations

from pathlib import Path
try:
    import pymupdf as fitz
except ImportError:
    import fitz

from app.formats.contracts import ArtifactFormat
from app.formats.registry import get_format, UnknownFormatError


class PDFValidator:
    def validate(
        self, 
        pdf_path: Path, 
        expected_format: str | ArtifactFormat | None = None,
        tolerance_pt: float = 4.0,
    ) -> dict:
        result = {
            "valid": False,
            "errors": [],
            "page_count": 0,
            "metadata": {}
        }
        
        if not pdf_path.exists():
            result["errors"].append(f"PDF not found at {pdf_path}")
            return result
            
        if pdf_path.stat().st_size == 0:
            result["errors"].append("PDF is empty.")
            return result
            
        try:
            with fitz.open(pdf_path) as doc:
                result["page_count"] = len(doc)
                if result["page_count"] == 0:
                    result["errors"].append("PDF has 0 pages.")
                    
                if result["page_count"] > 0:
                    page = doc[0]
                    rect = page.rect
                    result["metadata"]["width"] = rect.width
                    result["metadata"]["height"] = rect.height
                    result["metadata"]["text_length"] = len(page.get_text())
                    
                    if result["metadata"]["text_length"] < 5 and not page.get_images():
                        result["errors"].append("Page 1 appears completely blank (no text, no images).")
                    
                    # Validate physical dimensions against expected format contract
                    if expected_format:
                        try:
                            fmt = get_format(expected_format)
                            result["metadata"]["format_id"] = fmt.id
                            if not fmt.matches_dimensions(rect.width, rect.height, tolerance_pt=tolerance_pt):
                                result["errors"].append(
                                    f"PDF dimensions ({rect.width:.1f}x{rect.height:.1f} pt) do not match "
                                    f"expected format '{fmt.id}' ({fmt.width_pt:.1f}x{fmt.height_pt:.1f} pt)"
                                )
                        except UnknownFormatError:
                            pass
                
            if not result["errors"]:
                result["valid"] = True
                
        except Exception as e:
            result["errors"].append(f"Failed to parse PDF: {str(e)}")
            
        return result
