"""
KIR AI Document Intelligence — Multi-Artifact Curriculum Bundle Subsystem.
"""

from app.bundles.allocation import ContentAllocationPolicy, ObjectiveCoverageMatrix
from app.bundles.coherence import BundleCoherenceValidator
from app.bundles.contracts import (
    ArtifactBundleRequest,
    ArtifactRole,
    BundleItemResult,
    BundleResult,
)
from app.bundles.planner import BundlePlanner
from app.bundles.producer import ArtifactBundleProducer

__all__ = [
    "ArtifactBundleProducer",
    "ArtifactBundleRequest",
    "ArtifactRole",
    "BundleCoherenceValidator",
    "BundleItemResult",
    "BundlePlanner",
    "BundleResult",
    "ContentAllocationPolicy",
    "ObjectiveCoverageMatrix",
]
