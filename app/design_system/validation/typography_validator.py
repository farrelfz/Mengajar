"""
Universal Design System — Typography Validator.

Phase 3B.0: Enforces minimum font size floors and typographic hierarchy
invariants per artifact format (INV-DESIGN-006).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.design_system.registry.profile_registry import ProfileRegistry
from app.design_system.profiles import get_standard_profile_registry


class TypographyValidationFinding:
    """Design-level finding for typography issues."""
    def __init__(
        self,
        element_id: str,
        role: str,
        actual_size_pt: float,
        min_required_pt: float,
        artifact_type: str,
        message: str,
    ) -> None:
        self.element_id = element_id
        self.role = role
        self.actual_size_pt = actual_size_pt
        self.min_required_pt = min_required_pt
        self.artifact_type = artifact_type
        self.message = message


class TypographyValidator:
    """Validates typographic elements against format design profiles."""

    def __init__(self, profile_registry: Optional[ProfileRegistry] = None) -> None:
        self.profile_registry = profile_registry or get_standard_profile_registry()

    def validate_font_size(
        self,
        element_id: str,
        role: str,
        size_pt: float,
        artifact_type: str,
    ) -> Optional[TypographyValidationFinding]:
        """
        Validates whether an element's font size satisfies the artifact floor.
        Returns a finding if violated, None otherwise.
        """
        profile = self.profile_registry.get_profile_for_artifact(artifact_type)
        if not profile:
            return None

        is_valid, min_req, msg = profile.validate_font_size(role, size_pt)
        if not is_valid:
            return TypographyValidationFinding(
                element_id=element_id,
                role=role,
                actual_size_pt=size_pt,
                min_required_pt=min_req,
                artifact_type=artifact_type,
                message=msg,
            )
        return None

    def validate_elements(
        self,
        elements: List[Dict[str, Any]],
        artifact_type: str,
    ) -> List[TypographyValidationFinding]:
        """Validates a batch of typographic elements."""
        findings = []
        for el in elements:
            el_id = el.get("element_id", "unknown")
            role = el.get("role", "body")
            size_pt = float(el.get("font_size_pt", 10.0))
            fnd = self.validate_font_size(el_id, role, size_pt, artifact_type)
            if fnd:
                findings.append(fnd)
        return findings
