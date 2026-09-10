"""Unit tests for Universal Design System Token contracts and resolver."""

import pytest
from app.design_system.contracts.tokens import (
    RawToken,
    SemanticToken,
    ArtifactToken,
    TokenLevel,
)
from app.design_system.registry.token_registry import TokenRegistry
from app.design_system.resolver import DesignTokenResolver
from app.design_system.themes.base import get_base_theme


def test_token_registry_referential_integrity():
    """Verifies that missing references trigger integrity violations."""
    registry = TokenRegistry()
    raw = RawToken(name="color.blue", value="#0000ff", category="color")
    registry.register_raw_token(raw)

    # Valid semantic token
    sem_valid = SemanticToken(name="color.primary", raw_token_ref="color.blue", role="Primary")
    registry.register_semantic_token(sem_valid)

    # Invalid semantic token (missing raw token)
    sem_invalid = SemanticToken(name="color.secondary", raw_token_ref="color.red", role="Secondary")
    registry.register_semantic_token(sem_invalid)

    violations = registry.validate_integrity()
    assert len(violations) == 1
    assert "references non-existent RawToken 'color.red'" in violations[0]


def test_token_resolver_hierarchical_resolution():
    """Verifies 4-tier token resolution and provenance trail."""
    resolver = DesignTokenResolver()

    # 1. Resolve semantic token for HTML
    token_html, trace_html = resolver.resolve("color.text.primary", "PRESENTATION", "HTML")
    assert token_html.resolved_value == "#0f172a"
    assert not token_html.fallback_applied
    assert trace_html.raw_token == "color.slate.900"
    assert trace_html.semantic_token == "color.text.primary"

    # 2. Resolve for ReportLab (should convert to RGB float tuple)
    token_rl, _ = resolver.resolve("color.text.primary", "PRESENTATION", "REPORTLAB")
    assert isinstance(token_rl.resolved_value, tuple)
    assert len(token_rl.resolved_value) == 3
    assert all(0.0 <= c <= 1.0 for c in token_rl.resolved_value)

    # 3. Resolve for Pillow (should convert to 0..255 integer tuple)
    token_pil, _ = resolver.resolve("color.text.primary", "PRESENTATION", "PILLOW")
    assert isinstance(token_pil.resolved_value, tuple)
    assert all(isinstance(c, int) and 0 <= c <= 255 for c in token_pil.resolved_value)


def test_token_resolver_artifact_override():
    """Verifies that artifact-specific overrides take precedence."""
    resolver = DesignTokenResolver()

    token_pres, trace_pres = resolver.resolve("typography.presentation.title", "PRESENTATION", "HTML")
    assert token_pres.resolved_value == "28.0pt"
    assert trace_pres.artifact_token is not None


def test_token_resolver_graceful_fallback():
    """Verifies safe fallback when an unmapped token is requested."""
    resolver = DesignTokenResolver()

    token, trace = resolver.resolve("unknown.nonexistent.color", "HANDOUT", "HTML")
    assert token.fallback_applied is True
    assert token.resolved_value == "#64748b"  # safe neutral slate-500
    assert trace.degradation_recorded is True
