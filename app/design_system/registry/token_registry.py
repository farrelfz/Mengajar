"""
Universal Design System — Token Registry.

Phase 3B.0: Central repository for Raw, Semantic, and Artifact tokens
with referential integrity validation.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from app.design_system.contracts.tokens import (
    RawToken,
    SemanticToken,
    ArtifactToken,
)


class TokenRegistry:
    """Registry maintaining the 4-tier token hierarchy and references."""

    def __init__(self) -> None:
        self._raw_tokens: Dict[str, RawToken] = {}
        self._semantic_tokens: Dict[str, SemanticToken] = {}
        self._artifact_tokens: Dict[Tuple[str, str], ArtifactToken] = {}

    def register_raw_token(self, token: RawToken) -> None:
        """Registers a Level-1 raw token."""
        self._raw_tokens[token.name] = token

    def register_semantic_token(self, token: SemanticToken) -> None:
        """Registers a Level-2 semantic token."""
        self._semantic_tokens[token.name] = token

    def register_artifact_token(self, token: ArtifactToken) -> None:
        """Registers a Level-3 artifact-specific token."""
        key = (token.artifact_type.upper(), token.name)
        self._artifact_tokens[key] = token

    def get_raw_token(self, name: str) -> Optional[RawToken]:
        """Retrieves raw token by name."""
        return self._raw_tokens.get(name)

    def get_semantic_token(self, name: str) -> Optional[SemanticToken]:
        """Retrieves semantic token by name."""
        return self._semantic_tokens.get(name)

    def get_artifact_token(self, artifact_type: str, name: str) -> Optional[ArtifactToken]:
        """Retrieves artifact-specific token override."""
        return self._artifact_tokens.get((artifact_type.upper(), name))

    def list_raw_tokens(self) -> List[RawToken]:
        """Returns all registered raw tokens."""
        return list(self._raw_tokens.values())

    def list_semantic_tokens(self) -> List[SemanticToken]:
        """Returns all registered semantic tokens."""
        return list(self._semantic_tokens.values())

    def list_artifact_tokens(self, artifact_type: Optional[str] = None) -> List[ArtifactToken]:
        """Returns registered artifact tokens, optionally filtered by artifact type."""
        if artifact_type:
            upper = artifact_type.upper()
            return [t for (a, _), t in self._artifact_tokens.items() if a == upper]
        return list(self._artifact_tokens.values())

    def validate_integrity(self) -> List[str]:
        """
        Validates referential integrity:
        - Every SemanticToken must reference an existing RawToken.
        - Every ArtifactToken must reference an existing SemanticToken.
        Returns a list of violation error strings.
        """
        violations: List[str] = []
        for name, sem_token in self._semantic_tokens.items():
            if sem_token.raw_token_ref not in self._raw_tokens:
                violations.append(
                    f"SemanticToken '{name}' references non-existent RawToken '{sem_token.raw_token_ref}'"
                )

        for (art_type, name), art_token in self._artifact_tokens.items():
            if art_token.semantic_token_ref not in self._semantic_tokens:
                violations.append(
                    f"ArtifactToken '{name}' for '{art_type}' references non-existent SemanticToken '{art_token.semantic_token_ref}'"
                )

        return violations

    def clear(self) -> None:
        """Clears all tokens from registry (mainly for testing)."""
        self._raw_tokens.clear()
        self._semantic_tokens.clear()
        self._artifact_tokens.clear()
