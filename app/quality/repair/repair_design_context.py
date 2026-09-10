"""
Universal Document Intelligence System V5 — Repair Design Context.

Phase 3C.1: Design System as the SOLE visual and physical mutation authority.
Prevents repair strategies from hardcoding raw font sizes, colors, or padding.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from app.design_system.contracts.geometry import CanvasSpec
from app.design_system.contracts.components import ComponentSpec
from app.design_system.contracts.tokens import RenderToken
from app.design_system.contracts.spacing import SpacingScale, SpacingToken
from app.design_system.registry.component_registry import ComponentRegistry
from app.design_system.registry.font_registry import FontRegistry
from app.design_system.registry.profile_registry import ProfileRegistry
from app.design_system.resolver import DesignTokenResolver
from app.design_system.profiles import get_standard_profile_registry
from app.quality.repair.design_resolver import DesignAwareRepairResolver


class RepairDesignContext:
    """Encapsulates design system resolution services for repair strategies."""

    def __init__(
        self,
        profile_registry: Optional[ProfileRegistry] = None,
        component_registry: Optional[ComponentRegistry] = None,
        font_registry: Optional[FontRegistry] = None,
        token_resolver: Optional[DesignTokenResolver] = None,
    ) -> None:
        self.profile_registry = profile_registry or get_standard_profile_registry()
        self.component_registry = component_registry or ComponentRegistry()
        self.font_registry = font_registry or FontRegistry()
        self.token_resolver = token_resolver or DesignTokenResolver(
            profile_registry=self.profile_registry
        )
        self.repair_resolver = DesignAwareRepairResolver(
            profile_registry=self.profile_registry,
            token_resolver=self.token_resolver,
        )

    def resolve_token(
        self,
        artifact_type: str,
        renderer: str,
        token_name: str,
    ) -> RenderToken:
        """Resolves token down to renderer-executable primitive with full provenance."""
        render_token, _ = self.token_resolver.resolve(token_name, artifact_type, renderer)
        return render_token

    def resolve_component(
        self,
        component_id: str,
        artifact_type: str,
    ) -> Tuple[Optional[ComponentSpec], Optional[str]]:
        """Validates and retrieves component specification respecting artifact whitelist."""
        is_allowed, err = self.component_registry.validate_component_usage(component_id, artifact_type)
        if not is_allowed:
            return None, err
        return self.component_registry.get_component(component_id), None

    def resolve_geometry(self, artifact_type: str) -> Optional[CanvasSpec]:
        """Retrieves authoritative canvas dimensions and safe printable rect."""
        return self.repair_resolver.get_canvas_spec(artifact_type)

    def resolve_typography(
        self,
        role: str,
        target_size_pt: float,
        artifact_type: str,
    ) -> Tuple[float, bool]:
        """
        Enforces font size floors: clamps requested mutation size to profile minimum.
        Returns (safe_size_pt, was_clamped).
        """
        return self.repair_resolver.resolve_safe_font_size(artifact_type, role, target_size_pt)

    def resolve_color(
        self,
        background_hex: str,
        is_large_text: bool = False,
    ) -> str:
        """Selects accessible foreground text color satisfying WCAG AA contrast."""
        return self.repair_resolver.resolve_accessible_text_color(background_hex, is_large_text)

    def step_spacing(
        self,
        current_scale: SpacingScale,
        direction: str = "decrease",
    ) -> SpacingToken:
        """Steps along canonical discrete SpacingScale rather than arbitrary fractions."""
        return self.repair_resolver.step_spacing(current_scale, direction)
