"""
KIR AI Document Intelligence — Artifact Format Contract Package.
"""
from app.formats.contracts import ArtifactFormat
from app.formats.presets import (
    A4_PORTRAIT,
    A4_LANDSCAPE,
    PRESENTATION_16_9,
    CANONICAL_PRESETS,
)
from app.formats.registry import (
    FormatRegistry,
    UnknownFormatError,
    get_format,
)
from app.formats.resolution import (
    DEFAULT_ARTIFACT_FORMAT_MAPPING,
    resolve_format,
)
from app.formats.schemas import FormatConfig
from app.formats.a4_portrait import a4_portrait_config
from app.formats.a4_landscape import a4_landscape_config, a4_config
from app.formats.presentation_16_9 import presentation_config

__all__ = [
    "ArtifactFormat",
    "A4_PORTRAIT",
    "A4_LANDSCAPE",
    "PRESENTATION_16_9",
    "CANONICAL_PRESETS",
    "FormatRegistry",
    "UnknownFormatError",
    "get_format",
    "DEFAULT_ARTIFACT_FORMAT_MAPPING",
    "resolve_format",
    "FormatConfig",
    "a4_portrait_config",
    "a4_landscape_config",
    "a4_config",
    "presentation_config",
]
