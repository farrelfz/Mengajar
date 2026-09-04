"""
KIR AI Document Intelligence — Filename & Slug Utilities.
"""
from __future__ import annotations

from pathlib import Path
import re
import unicodedata


def sanitize_filename(name: str | None, fallback: str = "document", max_length: int = 80) -> str:
    """Convert an arbitrary string (title, file path, source hint) into a clean, safe filename slug.
    
    Examples
    --------
    >>> sanitize_filename("Panduan Metodologi Penelitian Eksperimen untuk Siswa")
    'panduan_metodologi_penelitian_eksperimen_untuk_siswa'
    >>> sanitize_filename("research_problem_guide.md")
    'research_problem_guide'
    >>> sanitize_filename("Physics: Rotational Torque & Dynamics #1")
    'physics_rotational_torque_dynamics_1'
    """
    if not name:
        return fallback

    # Extract stem if name looks like a file path
    name_str = str(name).strip()
    if "/" in name_str or "\\" in name_str or "." in name_str:
        stem = Path(name_str).stem
        if stem:
            name_str = stem

    # Normalize unicode (convert accents, diacritics)
    normalized = unicodedata.normalize("NFKD", name_str).encode("ascii", "ignore").decode("ascii")

    # Replace non-alphanumeric chars (excluding hyphens and underscores) with underscores
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", normalized).strip("_")

    # Collapse multiple consecutive underscores or hyphens
    cleaned = re.sub(r"_+", "_", cleaned)
    cleaned = cleaned.lower()

    if not cleaned:
        cleaned = fallback

    # Truncate to max_length without breaking awkwardly
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip("_")

    return cleaned or fallback
