"""
Universal Design System — Profile Registry.

Phase 3B.0: Registry for format-specific design profiles (Presentation, Handout,
Worksheet, Scientific Document).
"""

from __future__ import annotations

from typing import Dict, List, Optional
from app.design_system.contracts.profiles import DesignProfile


class ProfileRegistry:
    """Registry maintaining active design profiles for document artifacts."""

    def __init__(self) -> None:
        self._profiles_by_id: Dict[str, DesignProfile] = {}
        self._profiles_by_artifact: Dict[str, DesignProfile] = {}

    def register_profile(self, profile: DesignProfile) -> None:
        """Registers a design profile."""
        self._profiles_by_id[profile.profile_id] = profile
        self._profiles_by_artifact[profile.artifact_type.upper()] = profile

    def get_profile(self, profile_id: str) -> Optional[DesignProfile]:
        """Retrieves design profile by its unique ID."""
        return self._profiles_by_id.get(profile_id)

    def get_profile_for_artifact(self, artifact_type: str) -> Optional[DesignProfile]:
        """Retrieves default design profile for an artifact type."""
        return self._profiles_by_artifact.get(artifact_type.upper())

    def list_profiles(self) -> List[DesignProfile]:
        """Returns all registered design profiles."""
        return list(self._profiles_by_id.values())
