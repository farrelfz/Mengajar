"""
Universal Document Intelligence System V5 — Comparison Module.
"""

from .base import BenchmarkComparison
from .semantic import SemanticComparison
from .structural import StructuralComparison
from .visual import VisualComparison
from .artifact_specific import (
    ArtifactSpecificComparison,
    create_pedagogical_comparison,
    create_scientific_comparison
)

__all__ = [
    "BenchmarkComparison",
    "SemanticComparison",
    "StructuralComparison",
    "VisualComparison",
    "ArtifactSpecificComparison",
    "create_pedagogical_comparison",
    "create_scientific_comparison",
]
