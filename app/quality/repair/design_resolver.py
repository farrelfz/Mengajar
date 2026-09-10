"""
Universal Document Intelligence System V5 — Design-Aware Repair Resolver.

Phase 3B.0: Binds the repair engine to canonical design system tokens,
guaranteeing that mutations (font adjustments, spacing, geometry, contrast)
respect design profile floors and discrete scales (INV-DESIGN-006, INV-DESIGN-007).
"""

from __future__ import annotations

from typing import Optional, Tuple
from app.design_system.contracts.geometry import CanvasSpec
from app.design_system.contracts.spacing import SpacingScale, SpacingToken, SPACING_PT_MAP
from app.design_system.contracts.colors import ColorValue, evaluate_contrast, ContrastLevel
from app.design_system.registry.profile_registry import ProfileRegistry
from app.design_system.profiles import get_standard_profile_registry
from app.design_system.resolver import DesignTokenResolver


class DesignAwareRepairResolver:
    """Provides design-governed parameters and bounds for repair mutations."""

    def __init__(
        self,
        profile_registry: Optional[ProfileRegistry] = None,
        token_resolver: Optional[DesignTokenResolver] = None,
    ) -> None:
        self.profile_registry = profile_registry or get_standard_profile_registry()
        self.token_resolver = token_resolver or DesignTokenResolver(
            profile_registry=self.profile_registry
        )

    def resolve_safe_font_size(
        self,
        artifact_type: str,
        role: str,
        target_size_pt: float,
    ) -> Tuple[float, bool]:
        """
        Enforces INV-DESIGN-006: Clamps target font size to the profile's minimum floor.
        Returns (safe_size_pt, was_clamped).
        """
        profile = self.profile_registry.get_profile_for_artifact(artifact_type)
        if not profile:
            return max(8.0, target_size_pt), False

        is_valid, min_req, _ = profile.validate_font_size(role, target_size_pt)
        if not is_valid:
            return min_req, True
        return target_size_pt, False

    def step_spacing(
        self,
        current_scale: SpacingScale,
        direction: str = "decrease",
    ) -> SpacingToken:
        """
        Moves spacing up or down along canonical discrete SpacingScale steps.
        Prevents arbitrary fractional padding adjustments.
        """
        scales = [
            SpacingScale.NONE,
            SpacingScale.XXS,
            SpacingScale.XS,
            SpacingScale.SM,
            SpacingScale.MD,
            SpacingScale.LG,
            SpacingScale.XL,
            SpacingScale.XXL,
            SpacingScale.XXXL,
        ]
        curr_idx = scales.index(current_scale) if current_scale in scales else 4  # default MD

        if direction == "decrease":
            next_idx = max(0, curr_idx - 1)
        else:
            next_idx = min(len(scales) - 1, curr_idx + 1)

        target_scale = scales[next_idx]
        return SpacingToken.from_scale(target_scale)

    def resolve_accessible_text_color(
        self,
        background_hex: str,
        is_large_text: bool = False,
    ) -> str:
        """
        Selects an accessible text color (slate-900 or white) that satisfies WCAG AA
        against the given background hex.
        """
        bg = ColorValue(hex=background_hex)
        dark_text = ColorValue(hex="#0f172a")
        light_text = ColorValue(hex="#ffffff")

        ratio_dark, _ = evaluate_contrast(dark_text, bg)
        ratio_light, _ = evaluate_contrast(light_text, bg)

        min_req = 3.0 if is_large_text else 4.5

        if ratio_dark >= min_req and ratio_dark >= ratio_light:
            return dark_text.hex
        elif ratio_light >= min_req:
            return light_text.hex
        return dark_text.hex if ratio_dark > ratio_light else light_text.hex

    def get_canvas_spec(self, artifact_type: str) -> Optional[CanvasSpec]:
        """Retrieves canvas specification for artifact type."""
        profile = self.profile_registry.get_profile_for_artifact(artifact_type)
        return profile.canvas_spec if profile else None
