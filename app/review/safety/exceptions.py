"""
Universal Document Intelligence System V5 — Review Safety Exceptions.
"""

from __future__ import annotations


class IllegalDirectiveException(ValueError):
    """Raised when a human directive attempts to violate non-negotiable safety rules."""

    def __init__(self, directive_id: str, violation: str, responsible_subsystem: str = "safety_gateway") -> None:
        super().__init__(f"Illegal review directive '{directive_id}': {violation} (Subsystem: {responsible_subsystem})")
        self.directive_id = directive_id
        self.violation = violation
        self.responsible_subsystem = responsible_subsystem


class SovereignAuthorityBypassAttemptError(RuntimeError):
    """Raised when an action attempts to bypass UnifiedQualityAuthority or AuthorizedExportGate."""
    pass
