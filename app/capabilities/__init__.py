"""
KIR AI Document Intelligence — Capabilities & Registry Subsystem.

Provides the Capability contracts, central CapabilityRegistry, and LibraryResolver.
"""

from app.capabilities.contracts import (
    Capability,
    CapabilityMetadata,
    CapabilityOutput,
    CapabilityRenderer,
    CapabilitySpec,
)
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.resolver import (
    LibraryResolver,
    ResolutionCandidate,
    ResolutionResult,
)

__all__ = [
    "Capability",
    "CapabilityMetadata",
    "CapabilityOutput",
    "CapabilityRenderer",
    "CapabilitySpec",
    "CapabilityRegistry",
    "LibraryResolver",
    "ResolutionCandidate",
    "ResolutionResult",
]
