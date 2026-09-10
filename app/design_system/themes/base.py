"""
Universal Design System — Base Theme.

Phase 3B.0: Foundational Raw and Semantic design tokens with accessible contrast
and standard physical measurements.
"""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, ConfigDict
from app.design_system.contracts.tokens import RawToken, SemanticToken
from app.design_system.registry.token_registry import TokenRegistry


class ThemeDefinition(BaseModel):
    """Encapsulates a collection of raw and semantic tokens defining a theme."""
    model_config = ConfigDict(frozen=True)

    theme_id: str
    name: str
    description: str
    raw_tokens: List[RawToken]
    semantic_tokens: List[SemanticToken]

    def apply_to_registry(self, registry: TokenRegistry) -> None:
        """Registers all tokens defined in this theme into the given registry."""
        for r_tok in self.raw_tokens:
            registry.register_raw_token(r_tok)
        for s_tok in self.semantic_tokens:
            registry.register_semantic_token(s_tok)


def get_base_theme() -> ThemeDefinition:
    """Constructs the canonical neutral base theme."""
    raw_tokens = [
        # Colors: Slate Palette
        RawToken(name="color.white", value="#ffffff", category="color"),
        RawToken(name="color.slate.50", value="#f8fafc", category="color"),
        RawToken(name="color.slate.100", value="#f1f5f9", category="color"),
        RawToken(name="color.slate.200", value="#e2e8f0", category="color"),
        RawToken(name="color.slate.300", value="#cbd5e1", category="color"),
        RawToken(name="color.slate.400", value="#94a3b8", category="color"),
        RawToken(name="color.slate.500", value="#64748b", category="color"),
        RawToken(name="color.slate.700", value="#334155", category="color"),
        RawToken(name="color.slate.800", value="#1e293b", category="color"),
        RawToken(name="color.slate.900", value="#0f172a", category="color"),

        # Brand / Accent Colors
        RawToken(name="color.blue.500", value="#3b82f6", category="color"),
        RawToken(name="color.blue.600", value="#2563eb", category="color"),
        RawToken(name="color.blue.700", value="#1d4ed8", category="color"),
        RawToken(name="color.green.600", value="#16a34a", category="color"),
        RawToken(name="color.amber.600", value="#d97706", category="color"),
        RawToken(name="color.red.600", value="#dc2626", category="color"),

        # Spacings (pt)
        RawToken(name="spacing.0", value=0.0, category="space"),
        RawToken(name="spacing.2", value=2.0, category="space"),
        RawToken(name="spacing.4", value=4.0, category="space"),
        RawToken(name="spacing.8", value=8.0, category="space"),
        RawToken(name="spacing.12", value=12.0, category="space"),
        RawToken(name="spacing.16", value=16.0, category="space"),
        RawToken(name="spacing.24", value=24.0, category="space"),
        RawToken(name="spacing.32", value=32.0, category="space"),
        RawToken(name="spacing.48", value=48.0, category="space"),
        RawToken(name="spacing.64", value=64.0, category="space"),

        # Corner Radii (pt)
        RawToken(name="radius.none", value=0.0, category="radius"),
        RawToken(name="radius.sm", value=4.0, category="radius"),
        RawToken(name="radius.md", value=8.0, category="radius"),
        RawToken(name="radius.lg", value=12.0, category="radius"),
        RawToken(name="radius.full", value=9999.0, category="radius"),

        # Typographic Sizes (pt)
        RawToken(name="font.size.display_xl", value=36.0, category="font"),
        RawToken(name="font.size.display_l", value=28.0, category="font"),
        RawToken(name="font.size.heading_xl", value=24.0, category="font"),
        RawToken(name="font.size.heading_l", value=20.0, category="font"),
        RawToken(name="font.size.heading_m", value=16.0, category="font"),
        RawToken(name="font.size.heading_s", value=14.0, category="font"),
        RawToken(name="font.size.body_l", value=12.0, category="font"),
        RawToken(name="font.size.body_m", value=10.0, category="font"),
        RawToken(name="font.size.body_s", value=9.0, category="font"),
        RawToken(name="font.size.caption", value=8.0, category="font"),
        RawToken(name="font.size.micro", value=7.0, category="font"),
    ]

    semantic_tokens = [
        # Color Semantics
        SemanticToken(name="color.text.primary", raw_token_ref="color.slate.900", role="Text Primary"),
        SemanticToken(name="color.text.secondary", raw_token_ref="color.slate.700", role="Text Secondary"),
        SemanticToken(name="color.text.muted", raw_token_ref="color.slate.500", role="Text Muted"),
        SemanticToken(name="color.bg.primary", raw_token_ref="color.white", role="Page Background"),
        SemanticToken(name="color.bg.secondary", raw_token_ref="color.slate.50", role="Container Background"),
        SemanticToken(name="color.border.subtle", raw_token_ref="color.slate.200", role="Subtle Border"),
        SemanticToken(name="color.border.strong", raw_token_ref="color.slate.400", role="Prominent Border"),
        SemanticToken(name="color.accent.primary", raw_token_ref="color.blue.600", role="Primary Brand Accent"),
        SemanticToken(name="color.accent.secondary", raw_token_ref="color.blue.500", role="Secondary Accent"),
        SemanticToken(name="color.feedback.success", raw_token_ref="color.green.600", role="Success State"),
        SemanticToken(name="color.feedback.warning", raw_token_ref="color.amber.600", role="Warning State"),
        SemanticToken(name="color.feedback.danger", raw_token_ref="color.red.600", role="Error/Danger State"),

        # Spacing Semantics
        SemanticToken(name="spacing.inset.sm", raw_token_ref="spacing.8", role="Small Card Inset"),
        SemanticToken(name="spacing.inset.md", raw_token_ref="spacing.16", role="Standard Card Inset"),
        SemanticToken(name="spacing.inset.lg", raw_token_ref="spacing.24", role="Large Section Inset"),
        SemanticToken(name="spacing.gap.sm", raw_token_ref="spacing.8", role="Small Grid Gap"),
        SemanticToken(name="spacing.gap.md", raw_token_ref="spacing.16", role="Standard Grid Gap"),
        SemanticToken(name="spacing.stack.sm", raw_token_ref="spacing.8", role="Tight Paragraph Gap"),
        SemanticToken(name="spacing.stack.md", raw_token_ref="spacing.16", role="Standard Paragraph Gap"),
        SemanticToken(name="spacing.stack.lg", raw_token_ref="spacing.24", role="Section Spacing"),

        # Typography Semantics
        SemanticToken(name="typography.title", raw_token_ref="font.size.display_l", role="Document Title"),
        SemanticToken(name="typography.heading", raw_token_ref="font.size.heading_m", role="Section Heading"),
        SemanticToken(name="typography.subheading", raw_token_ref="font.size.heading_s", role="Subheading"),
        SemanticToken(name="typography.body", raw_token_ref="font.size.body_m", role="Body Reading Text"),
        SemanticToken(name="typography.body.small", raw_token_ref="font.size.body_s", role="Compact Body Text"),
        SemanticToken(name="typography.caption", raw_token_ref="font.size.caption", role="Citations and Footnotes"),
    ]

    return ThemeDefinition(
        theme_id="base",
        name="Base Neutral Theme",
        description="Default neutral slate-and-blue theme with WCAG AA compliance",
        raw_tokens=raw_tokens,
        semantic_tokens=semantic_tokens,
    )
