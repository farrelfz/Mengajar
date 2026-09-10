"""
Universal Design System — Quality Authority Bridge.

Phase 3B.0: Adapts design system validation findings into canonical
QualityFinding objects consumed by UnifiedQualityAuthority (INV-DESIGN-012).
"""

from __future__ import annotations

import uuid
from typing import List, Union
from app.quality.contracts.signals import QualityDomain, SignalSeverity
from app.quality.contracts.findings import QualityFinding

from app.design_system.validation.typography_validator import TypographyValidationFinding
from app.design_system.validation.color_validator import ColorContrastFinding
from app.design_system.validation.geometry_validator import GeometryValidationFinding
from app.design_system.validation.asset_validator import AssetValidationFinding
from app.design_system.validation.token_validator import TokenValidationFinding


class DesignSystemQualityBridge:
    """Translates design system findings into canonical Level-0 QualityFindings."""

    @staticmethod
    def map_typography_finding(fnd: TypographyValidationFinding) -> QualityFinding:
        return QualityFinding(
            finding_id=f"fnd_ds_typo_{uuid.uuid4().hex[:8]}",
            failure_code="MINIMUM_FONT_SIZE_VIOLATION",
            domain=QualityDomain.RENDERED,
            severity=SignalSeverity.MAJOR,
            artifact_type=fnd.artifact_type,
            message=fnd.message,
            causal_hypothesis="Font scale set below artifact minimum legibility threshold.",
            affected_elements=(fnd.element_id,),
            repairability=True,
            repair_class="CLASS_A",  # Parameter modification (increase font size)
            evidence={
                "role": fnd.role,
                "actual_size_pt": fnd.actual_size_pt,
                "min_required_pt": fnd.min_required_pt,
            },
        )

    @staticmethod
    def map_color_contrast_finding(fnd: ColorContrastFinding) -> QualityFinding:
        severity = (
            SignalSeverity.MAJOR
            if fnd.contrast_ratio < 3.0
            else SignalSeverity.WARNING
        )
        return QualityFinding(
            finding_id=f"fnd_ds_color_{uuid.uuid4().hex[:8]}",
            failure_code="COLOR_CONTRAST_LOW",
            domain=QualityDomain.RENDERED,
            severity=severity,
            artifact_type="all",
            message=fnd.message,
            causal_hypothesis="Foreground text color lacks sufficient luminance difference against container background.",
            affected_elements=(fnd.element_id,),
            repairability=True,
            repair_class="CLASS_A",
            evidence={
                "foreground_hex": fnd.foreground_hex,
                "background_hex": fnd.background_hex,
                "contrast_ratio": fnd.contrast_ratio,
                "min_required_ratio": fnd.min_required_ratio,
            },
        )

    @staticmethod
    def map_geometry_finding(fnd: GeometryValidationFinding) -> QualityFinding:
        severity = (
            SignalSeverity.CRITICAL
            if fnd.violation_type == "CANVAS_OVERFLOW"
            else SignalSeverity.MAJOR
        )
        return QualityFinding(
            finding_id=f"fnd_ds_geom_{uuid.uuid4().hex[:8]}",
            failure_code=fnd.violation_type,
            domain=QualityDomain.RENDERED,
            severity=severity,
            artifact_type=fnd.artifact_type,
            message=fnd.message,
            causal_hypothesis="Block dimensions or layout offset extend beyond canvas printable bounds.",
            affected_elements=(fnd.element_id,),
            repairability=True,
            repair_class="CLASS_B",  # Layout structural modification
            evidence={
                "bounding_box": fnd.bounding_box,
                "canvas_limits": fnd.canvas_limits,
            },
        )

    @staticmethod
    def map_asset_finding(fnd: AssetValidationFinding) -> QualityFinding:
        severity = SignalSeverity.BLOCKING if fnd.is_critical else SignalSeverity.WARNING
        return QualityFinding(
            finding_id=f"fnd_ds_asset_{uuid.uuid4().hex[:8]}",
            failure_code=fnd.violation_type,
            domain=QualityDomain.ARTIFACT,
            severity=severity,
            artifact_type=fnd.artifact_type,
            message=fnd.message,
            causal_hypothesis="Missing asset, unregistered font face, or incompatible component category used.",
            affected_elements=(fnd.target_id,),
            repairability=True,
            repair_class="CLASS_D",  # Content substitution or asset fallback
            evidence={
                "target_id": fnd.target_id,
                "is_critical": fnd.is_critical,
            },
        )

    @staticmethod
    def map_token_finding(fnd: TokenValidationFinding) -> QualityFinding:
        return QualityFinding(
            finding_id=f"fnd_ds_token_{uuid.uuid4().hex[:8]}",
            failure_code="DESIGN_TOKEN_UNRESOLVED",
            domain=QualityDomain.ARTIFACT,
            severity=SignalSeverity.MINOR,
            artifact_type=fnd.artifact_type,
            message=fnd.message,
            causal_hypothesis="Requested token is missing from registry and required safe fallback.",
            affected_elements=(fnd.token_name,),
            repairability=True,
            repair_class="CLASS_A",
            evidence={
                "token_name": fnd.token_name,
                "renderer": fnd.renderer,
            },
        )
