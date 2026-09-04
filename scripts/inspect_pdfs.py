#!/usr/bin/env python3
"""
KIR AI Document Intelligence — Safe PDF Inspection Utility.

Inspects generated PDF files for page counts, dimensions (points & mm), and integrity
using safe directory pruning to avoid traversing venv or dependency trees.

Usage
-----
python scripts/inspect_pdfs.py [directory]
PYTHONPATH=. python scripts/inspect_pdfs.py outputs
PYTHONPATH=. python scripts/inspect_pdfs.py outputs/visual_benchmark
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        print("Error: PyMuPDF is required. Install via `pip install pymupdf`.", file=sys.stderr)
        sys.exit(1)

from app.utils.file_discovery import find_files


def format_dimensions(width_pt: float, height_pt: float) -> str:
    """Format dimensions in points and millimeters."""
    width_mm = width_pt * 25.4 / 72.0
    height_mm = height_pt * 25.4 / 72.0
    return f"{width_pt:.1f}x{height_pt:.1f} pt ({width_mm:.1f}x{height_mm:.1f} mm)"


def inspect_pdf(pdf_path: Path) -> dict:
    """Inspect a single PDF file and return its metrics."""
    metrics = {
        "path": str(pdf_path),
        "valid": False,
        "pages": 0,
        "width_pt": 0.0,
        "height_pt": 0.0,
        "width_mm": 0.0,
        "height_mm": 0.0,
        "error": None,
    }

    try:
        with fitz.open(pdf_path) as doc:
            metrics["pages"] = len(doc)
            if len(doc) > 0:
                page0 = doc[0]
                rect = page0.rect
                metrics["width_pt"] = rect.width
                metrics["height_pt"] = rect.height
                metrics["width_mm"] = rect.width * 25.4 / 72.0
                metrics["height_mm"] = rect.height * 25.4 / 72.0
            metrics["valid"] = True
    except Exception as exc:
        metrics["error"] = str(exc)

    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect PDF page count and dimensions safely.")
    parser.add_argument(
        "target",
        nargs="?",
        default="outputs",
        help="Target directory or PDF file to inspect (default: outputs)",
    )
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Target path does not exist: {target_path}", file=sys.stderr)
        return 1

    pdf_files = find_files(target_path, patterns="*.pdf")

    if not pdf_files:
        print(f"No PDF files found under: {target_path}")
        return 0

    print(f"\nFound {len(pdf_files)} PDF file(s) under '{target_path}':")
    print("-" * 90)
    print(f"{'Path':<50} {'Pages':<8} {'Dimensions (pt / mm)':<30}")
    print("-" * 90)

    for p in pdf_files:
        info = inspect_pdf(p)
        if not info["valid"]:
            print(f"{str(p):<50} {'ERR':<8} Error: {info['error']}")
        else:
            dim_str = format_dimensions(info["width_pt"], info["height_pt"])
            print(f"{str(p):<50} {info['pages']:<8} {dim_str}")

    print("-" * 90)
    return 0


if __name__ == "__main__":
    sys.exit(main())
