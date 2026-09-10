"""
Universal Design System — Geometry & Canvas Validator.

Phase 3B.0: Enforces canvas boundaries, safe margins, and layout limits (INV-DESIGN-002).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.design_system.registry.profile_registry import ProfileRegistry
from app.design_system.profiles import get_standard_profile_registry


class GeometryValidationFinding:
    """Design-level finding for canvas overflow or safe zone intrusion."""
    def __init__(
        self,
        element_id: str,
        violation_type: str,  # "CANVAS_OVERFLOW" or "SAFE_MARGIN_INTRUSION"
        bounding_box: Dict[str, float],
        canvas_limits: Dict[str, float],
        artifact_type: str,
        message: str,
    ) -> None:
        self.element_id = element_id
        self.violation_type = violation_type
        self.bounding_box = bounding_box
        self.canvas_limits = canvas_limits
        self.artifact_type = artifact_type
        self.message = message


class GeometryValidator:
    """Validates physical layout coordinates against canvas specifications."""

    def __init__(self, profile_registry: Optional[ProfileRegistry] = None) -> None:
        self.profile_registry = profile_registry or get_standard_profile_registry()

    def validate_bounding_box(
        self,
        element_id: str,
        x: float,
        y: float,
        width: float,
        height: float,
        artifact_type: str,
        allow_margin_bleed: bool = False,
    ) -> Optional[GeometryValidationFinding]:
        """
        Validates element placement in points:
        - Must not extend beyond total canvas width and height.
        - Unless allow_margin_bleed is True, must not intrude into safe margins.
        """
        profile = self.profile_registry.get_profile_for_artifact(artifact_type)
        if not profile:
            return None

        canvas = profile.canvas_spec
        right = x + width
        bottom = y + height

        # Check total canvas overflow
        if x < 0 or y < 0 or right > canvas.width_pt or bottom > canvas.height_pt:
            return GeometryValidationFinding(
                element_id=element_id,
                violation_type="CANVAS_OVERFLOW",
                bounding_box={"x": x, "y": y, "width": width, "height": height},
                canvas_limits={"width": canvas.width_pt, "height": canvas.height_pt},
                artifact_type=artifact_type,
                message=(
                    f"Element '{element_id}' [{x:.1f}, {y:.1f}, {right:.1f}, {bottom:.1f}] "
                    f"overflows canvas dimensions [{canvas.width_pt:.1f} x {canvas.height_pt:.1f}]"
                ),
            )

        # Check safe margin violation
        if not allow_margin_bleed:
            safe_x0 = canvas.safe_margin_left_pt
            safe_y0 = canvas.safe_margin_top_pt
            safe_x1 = canvas.width_pt - canvas.safe_margin_right_pt
            safe_y1 = canvas.height_pt - canvas.safe_margin_bottom_pt

            if x < safe_x0 or y < safe_y0 or right > safe_x1 or bottom > safe_y1:
                return GeometryValidationFinding(
                    element_id=element_id,
                    violation_type="SAFE_MARGIN_INTRUSION",
                    bounding_box={"x": x, "y": y, "width": width, "height": height},
                    canvas_limits={"safe_x0": safe_x0, "safe_y0": safe_y0, "safe_x1": safe_x1, "safe_y1": safe_y1},
                    artifact_type=artifact_type,
                    message=(
                        f"Element '{element_id}' penetrates printable safe margins "
                        f"[{safe_x0:.1f}, {safe_y0:.1f}, {safe_x1:.1f}, {safe_y1:.1f}]"
                    ),
                )

        return None
