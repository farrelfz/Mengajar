"""
KIR AI Document Intelligence — Artifact Format Registry.
"""
from __future__ import annotations

from app.formats.contracts import ArtifactFormat
from app.formats.presets import A4_PORTRAIT, A4_LANDSCAPE, PRESENTATION_16_9, CANONICAL_PRESETS
from app.intelligence.schemas import DocumentMode


class UnknownFormatError(ValueError):
    """Raised when an unknown format identifier is requested."""
    pass


class FormatRegistry:
    """Central registry of authoritative physical artifact formats with alias resolution."""
    _instance: FormatRegistry | None = None

    def __init__(self) -> None:
        self._formats: dict[str, ArtifactFormat] = dict(CANONICAL_PRESETS)
        self._aliases: dict[str, str] = {
            # Presentation aliases
            "presentation-16-9": PRESENTATION_16_9.id,
            "presentation_16_9": PRESENTATION_16_9.id,
            "presentation": PRESENTATION_16_9.id,
            "16:9": PRESENTATION_16_9.id,
            "16_9": PRESENTATION_16_9.id,
            
            # A4 Portrait aliases
            "a4-portrait": A4_PORTRAIT.id,
            "a4_portrait": A4_PORTRAIT.id,
            "a4": A4_PORTRAIT.id,
            "portrait": A4_PORTRAIT.id,
            "a4_handout": A4_PORTRAIT.id,
            
            # A4 Landscape aliases
            "a4-landscape": A4_LANDSCAPE.id,
            "a4_landscape": A4_LANDSCAPE.id,
            "a4-tutorial": A4_LANDSCAPE.id,
            "a4_tutorial": A4_LANDSCAPE.id,
            "landscape": A4_LANDSCAPE.id,
        }

    @classmethod
    def get_instance(cls) -> FormatRegistry:
        if cls._instance is None:
            cls._instance = FormatRegistry()
        return cls._instance

    def register(self, fmt: ArtifactFormat, aliases: list[str] | None = None) -> None:
        """Register a new format preset and optional aliases."""
        self._formats[fmt.id] = fmt
        if aliases:
            for alias in aliases:
                self._aliases[alias.lower().strip()] = fmt.id

    def get(self, identifier: str | DocumentMode | ArtifactFormat) -> ArtifactFormat:
        """Retrieve an ArtifactFormat by canonical ID, alias, DocumentMode, or pass-through."""
        if isinstance(identifier, ArtifactFormat):
            return identifier

        if isinstance(identifier, DocumentMode):
            identifier = identifier.value

        key = str(identifier).lower().strip()

        # Check canonical
        if key in self._formats:
            return self._formats[key]

        # Check alias
        if key in self._aliases:
            canonical_id = self._aliases[key]
            return self._formats[canonical_id]

        available = list(self._formats.keys()) + list(self._aliases.keys())
        raise UnknownFormatError(
            f"Unknown format identifier '{identifier}'. Available formats and aliases: {sorted(set(available))}"
        )

    def list_formats(self) -> list[ArtifactFormat]:
        """List all canonical formats."""
        return list(self._formats.values())


# Global helper
def get_format(identifier: str | DocumentMode | ArtifactFormat) -> ArtifactFormat:
    return FormatRegistry.get_instance().get(identifier)
