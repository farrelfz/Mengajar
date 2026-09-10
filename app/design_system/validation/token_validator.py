"""
Universal Design System — Token Integrity Validator.

Phase 3B.0: Validates token references, prevents circular or dangling token bindings,
and audits resolution traces (INV-DESIGN-007, INV-DESIGN-008).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.design_system.registry.token_registry import TokenRegistry
from app.design_system.resolver import DesignTokenResolver


class TokenValidationFinding:
    """Design-level finding for token resolution failure."""
    def __init__(
        self,
        token_name: str,
        artifact_type: str,
        renderer: str,
        is_fallback: bool,
        message: str,
    ) -> None:
        self.token_name = token_name
        self.artifact_type = artifact_type
        self.renderer = renderer
        self.is_fallback = is_fallback
        self.message = message


class TokenValidator:
    """Audits token definitions and resolution integrity."""

    def __init__(
        self,
        token_registry: Optional[TokenRegistry] = None,
        resolver: Optional[DesignTokenResolver] = None,
    ) -> None:
        self.resolver = resolver or DesignTokenResolver(token_registry=token_registry)
        self.token_registry = self.resolver.token_registry

    def validate_registry_integrity(self) -> List[str]:
        """Validates referential links between Raw, Semantic, and Artifact tokens."""
        return self.token_registry.validate_integrity()

    def validate_token_resolution(
        self,
        token_names: List[str],
        artifact_type: str,
        renderer: str,
    ) -> List[TokenValidationFinding]:
        """Verifies that a list of tokens resolve cleanly without unexpected degradation."""
        findings = []
        for name in token_names:
            render_token, trace = self.resolver.resolve(name, artifact_type, renderer)
            if render_token.fallback_applied:
                findings.append(
                    TokenValidationFinding(
                        token_name=name,
                        artifact_type=artifact_type,
                        renderer=renderer,
                        is_fallback=True,
                        message=render_token.degradation_note or f"Token '{name}' required fallback.",
                    )
                )
        return findings
