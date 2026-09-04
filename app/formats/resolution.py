"""
KIR AI Document Intelligence — Deterministic Format Resolution.
"""
from __future__ import annotations

from app.blueprints.production import TargetArtifactType
from app.formats.contracts import ArtifactFormat
from app.formats.presets import A4_PORTRAIT, A4_LANDSCAPE, PRESENTATION_16_9
from app.formats.registry import FormatRegistry, get_format
from app.intelligence.schemas import DocumentMode

# Default format mappings by artifact type (recommendations, NOT immutable constraints)
DEFAULT_ARTIFACT_FORMAT_MAPPING: dict[TargetArtifactType, ArtifactFormat] = {
    TargetArtifactType.TEACHING_PRESENTATION: PRESENTATION_16_9,
    TargetArtifactType.RESEARCH_PRESENTATION: PRESENTATION_16_9,
    TargetArtifactType.DETAILED_HANDOUT: A4_PORTRAIT,
    TargetArtifactType.STUDENT_WORKSHEET: A4_PORTRAIT,
    TargetArtifactType.SCIENTIFIC_POSTER: A4_LANDSCAPE,
    TargetArtifactType.ONE_PAGE_SUMMARY: A4_PORTRAIT,
    TargetArtifactType.KTI_DOCUMENT: A4_PORTRAIT,
}


def resolve_format(
    explicit_format: str | DocumentMode | ArtifactFormat | None = None,
    artifact_type: TargetArtifactType | str | None = None,
    pedagogical_mode: str | None = None,
    fallback: ArtifactFormat = A4_PORTRAIT,
) -> ArtifactFormat:
    """Deterministically resolve an ArtifactFormat with clear precedence.

    Precedence
    ----------
    1. Explicit format requested by caller (overrides all defaults).
    2. Default format mapped from TargetArtifactType (recommendation).
    3. Safe system fallback (A4_PORTRAIT).
    """
    registry = FormatRegistry.get_instance()

    # 1. Explicit format override
    if explicit_format is not None:
        return registry.get(explicit_format)

    # 2. Artifact default recommendation
    if artifact_type is not None:
        if isinstance(artifact_type, str):
            try:
                target_enum = TargetArtifactType(artifact_type.lower())
            except ValueError:
                target_enum = None
        else:
            target_enum = artifact_type

        if target_enum and target_enum in DEFAULT_ARTIFACT_FORMAT_MAPPING:
            return DEFAULT_ARTIFACT_FORMAT_MAPPING[target_enum]

    # 3. Fallback
    return fallback
