"""
Universal Design System — Token Resolver.

Phase 3B.0: Contextual, deterministic 4-tier token resolution across
renderers (HTML, ReportLab, Pillow, PyMuPDF) with full provenance tracking
(INV-DESIGN-007, INV-DESIGN-008, INV-DESIGN-009).
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from app.design_system.contracts.tokens import (
    RawToken,
    SemanticToken,
    ArtifactToken,
    RenderToken,
    DesignResolutionTrace,
)
from app.design_system.contracts.colors import ColorValue
from app.design_system.contracts.geometry import pt_to_px
from app.design_system.contracts.shadows import SHADOW_MAP, ElevationScale
from app.design_system.registry.token_registry import TokenRegistry
from app.design_system.registry.profile_registry import ProfileRegistry
from app.design_system.themes.base import get_base_theme
from app.design_system.profiles import get_standard_profile_registry


class DesignTokenResolver:
    """Resolves abstract semantic tokens into renderer-bound execution tokens."""

    def __init__(
        self,
        token_registry: Optional[TokenRegistry] = None,
        profile_registry: Optional[ProfileRegistry] = None,
    ) -> None:
        if token_registry is None:
            token_registry = TokenRegistry()
            # Initialize with canonical base theme
            get_base_theme().apply_to_registry(token_registry)
        self.token_registry = token_registry

        if profile_registry is None:
            profile_registry = get_standard_profile_registry()
        self.profile_registry = profile_registry

    def resolve(
        self,
        token_name: str,
        artifact_type: str,
        renderer: str,
    ) -> Tuple[RenderToken, DesignResolutionTrace]:
        """
        Resolves a design token deterministically for a given artifact and renderer.
        Enforces INV-DESIGN-007, INV-DESIGN-008, and INV-DESIGN-009.
        """
        renderer_upper = renderer.upper()
        artifact_upper = artifact_type.upper()

        trace_semantic: Optional[str] = None
        trace_artifact: Optional[str] = None
        trace_raw: Optional[str] = None
        fallback_applied = False
        degradation_note: Optional[str] = None

        resolved_value: Any = None
        unit: Optional[str] = None

        # 1. Check Profile-specific token overrides (Artifact level)
        profile = self.profile_registry.get_profile_for_artifact(artifact_upper)
        if profile and token_name in profile.token_overrides:
            resolved_value = profile.token_overrides[token_name]
            trace_artifact = f"profile({profile.profile_id}).overrides[{token_name}]"
        else:
            # 2. Check explicit ArtifactToken in TokenRegistry
            art_token = self.token_registry.get_artifact_token(artifact_upper, token_name)
            if art_token:
                trace_artifact = art_token.name
                if art_token.override_value is not None:
                    resolved_value = art_token.override_value
                else:
                    token_name = art_token.semantic_token_ref

        # 3. If not resolved by artifact override, look up SemanticToken
        if resolved_value is None:
            sem_token = self.token_registry.get_semantic_token(token_name)
            if sem_token:
                trace_semantic = sem_token.name
                raw_token = self.token_registry.get_raw_token(sem_token.raw_token_ref)
                if raw_token:
                    trace_raw = raw_token.name
                    resolved_value = raw_token.value
                else:
                    fallback_applied = True
                    degradation_note = (
                        f"Raw token '{sem_token.raw_token_ref}' referenced by '{token_name}' not found."
                    )
            else:
                # Direct check if token_name is a raw token name
                raw_token = self.token_registry.get_raw_token(token_name)
                if raw_token:
                    trace_raw = raw_token.name
                    resolved_value = raw_token.value
                else:
                    # Missing token fallback
                    fallback_applied = True
                    resolved_value = self._get_safe_fallback_value(token_name)
                    degradation_note = f"Token '{token_name}' unresolved; applied safe fallback."

        # 4. Renderer-specific translation & degradation (INV-DESIGN-009)
        final_val, unit, rend_deg = self._adapt_to_renderer(
            resolved_value, renderer_upper, token_name
        )
        if rend_deg:
            fallback_applied = True
            degradation_note = (
                f"{degradation_note}; {rend_deg}" if degradation_note else rend_deg
            )

        render_token = RenderToken(
            renderer=renderer_upper,
            token_name=token_name,
            resolved_value=final_val,
            unit=unit,
            fallback_applied=fallback_applied,
            degradation_note=degradation_note,
        )

        trace = DesignResolutionTrace(
            artifact_type=artifact_upper,
            renderer=renderer_upper,
            requested_token=token_name,
            semantic_token=trace_semantic,
            artifact_token=trace_artifact,
            raw_token=trace_raw,
            resolved_value=final_val,
            fallback_applied=fallback_applied,
            degradation_recorded=degradation_note is not None,
        )

        return render_token, trace

    def _get_safe_fallback_value(self, token_name: str) -> Any:
        """Determines safe fallback value based on token naming convention."""
        name_lower = token_name.lower()
        if "color" in name_lower or "bg" in name_lower or "border" in name_lower:
            return "#64748b"  # Neutral slate-500
        if "size" in name_lower or "typography" in name_lower or "font" in name_lower:
            return 10.0       # Safe 10 pt
        if "space" in name_lower or "gap" in name_lower or "padding" in name_lower:
            return 8.0        # Safe 8 pt
        if "radius" in name_lower:
            return 0.0
        return 0.0

    def _adapt_to_renderer(
        self, raw_val: Any, renderer: str, token_name: str
    ) -> Tuple[Any, Optional[str], Optional[str]]:
        """
        Translates raw value into renderer-appropriate format.
        Returns (adapted_value, unit, degradation_note).
        """
        degradation = None

        # Check if color
        is_color = isinstance(raw_val, str) and raw_val.startswith("#")
        is_number = isinstance(raw_val, (int, float))

        if renderer in ("HTML", "CSS"):
            if is_color:
                return raw_val, None, None
            if is_number:
                return f"{raw_val}pt", "pt", None
            return str(raw_val), None, None

        elif renderer == "REPORTLAB":
            if is_color:
                # ReportLab uses RGB float tuple (0.0 .. 1.0) or HexColor
                color_val = ColorValue(hex=raw_val)
                return color_val.to_rgb_float_tuple(), "rgb_float", None
            if is_number:
                # ReportLab points are raw floats
                return float(raw_val), "pt", None
            # Check for shadows/elevations in ReportLab (graceful degradation to border)
            if "shadow" in token_name.lower() or "elevation" in token_name.lower():
                degradation = "Box-shadow unsupported in ReportLab; degraded to outline border stroke."
                return 0.5, "pt", degradation
            return raw_val, None, None

        elif renderer == "PILLOW":
            if is_color:
                color_val = ColorValue(hex=raw_val)
                return color_val.to_rgb_tuple(), "rgb_int", None
            if is_number:
                # Pillow uses pixels (96 DPI default)
                px_val = pt_to_px(float(raw_val))
                return round(px_val), "px", None
            return raw_val, None, None

        elif renderer == "PYMUPDF":
            if is_number:
                return float(raw_val), "pt", None
            return raw_val, None, None

        return raw_val, None, None
