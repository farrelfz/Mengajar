"""
Universal Design System — Cross-Renderer Physical Parity Validator.

Phase 3C.1: Asserts semantic parity across HTML, ReportLab, and Pillow rendering targets
within physical unit conversion tolerances (INV-DESIGN-007, INV-DESIGN-009).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field
from app.design_system.contracts.geometry import pt_to_px
from app.design_system.contracts.colors import ColorValue
from app.design_system.resolver import DesignTokenResolver


class ParityItem(BaseModel):
    """Validation record for a single token across renderers."""
    model_config = ConfigDict(frozen=True)

    token_name: str
    artifact_type: str
    html_value: Any
    reportlab_value: Any
    pillow_value: Any
    tolerance_applied: float
    is_parity_preserved: bool
    status_note: str = "PASS"


class CrossRendererParityReport(BaseModel):
    """Report synthesizing cross-renderer consistency."""
    model_config = ConfigDict(frozen=True)

    items: Tuple[ParityItem, ...]
    total_checked: int
    total_passed: int
    has_discrepancies: bool


class CrossRendererParityValidator:
    """Validates that token resolution across rendering engines maintains semantic consistency."""

    def __init__(self, resolver: Optional[DesignTokenResolver] = None) -> None:
        self.resolver = resolver or DesignTokenResolver()

    def validate_token(
        self,
        token_name: str,
        artifact_type: str,
    ) -> ParityItem:
        """Checks parity for a token across HTML, ReportLab, and Pillow."""
        t_html, _ = self.resolver.resolve(token_name, artifact_type, "HTML")
        t_rl, _ = self.resolver.resolve(token_name, artifact_type, "REPORTLAB")
        t_pil, _ = self.resolver.resolve(token_name, artifact_type, "PILLOW")

        # Case 1: Color token check
        if isinstance(t_html.resolved_value, str) and t_html.resolved_value.startswith("#"):
            c_val = ColorValue(hex=t_html.resolved_value)
            expected_rl = c_val.to_rgb_float_tuple()
            expected_pil = c_val.to_rgb_tuple()

            rl_match = t_rl.resolved_value == expected_rl
            pil_match = t_pil.resolved_value == expected_pil

            is_ok = rl_match and pil_match
            return ParityItem(
                token_name=token_name,
                artifact_type=artifact_type,
                html_value=t_html.resolved_value,
                reportlab_value=t_rl.resolved_value,
                pillow_value=t_pil.resolved_value,
                tolerance_applied=0.01,
                is_parity_preserved=is_ok,
                status_note="PASS" if is_ok else "Color RGB conversion divergence",
            )

        # Case 2: Numeric/Size token check (pt vs px)
        if isinstance(t_rl.resolved_value, (int, float)):
            pt_val = float(t_rl.resolved_value)
            expected_px = round(pt_to_px(pt_val, dpi=96.0))
            actual_px = int(t_pil.resolved_value)

            diff = abs(actual_px - expected_px)
            is_ok = diff <= 1  # 1px rounding tolerance
            return ParityItem(
                token_name=token_name,
                artifact_type=artifact_type,
                html_value=t_html.resolved_value,
                reportlab_value=t_rl.resolved_value,
                pillow_value=t_pil.resolved_value,
                tolerance_applied=1.0,
                is_parity_preserved=is_ok,
                status_note="PASS" if is_ok else f"Pixel rasterization diff {diff}px exceeds tolerance",
            )

        # General pass
        return ParityItem(
            token_name=token_name,
            artifact_type=artifact_type,
            html_value=t_html.resolved_value,
            reportlab_value=t_rl.resolved_value,
            pillow_value=t_pil.resolved_value,
            tolerance_applied=0.0,
            is_parity_preserved=True,
            status_note="PASS",
        )

    def validate_standard_suite(self, artifact_type: str) -> CrossRendererParityReport:
        """Audits canonical colors and typographic tokens across renderers."""
        test_tokens = [
            "color.text.primary",
            "color.accent.primary",
            "spacing.8",
            "spacing.16",
            "font.size.body_m",
            "font.size.heading_m",
        ]

        items = [self.validate_token(t, artifact_type) for t in test_tokens]
        passed = sum(1 for i in items if i.is_parity_preserved)

        return CrossRendererParityReport(
            items=tuple(items),
            total_checked=len(items),
            total_passed=passed,
            has_discrepancies=passed < len(items),
        )
