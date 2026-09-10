"""Universal Design System Format Profiles Export."""

from app.design_system.profiles.presentation import get_presentation_profile
from app.design_system.profiles.handout import get_handout_profile
from app.design_system.profiles.worksheet import get_worksheet_profile
from app.design_system.profiles.scientific_document import get_scientific_document_profile
from app.design_system.registry.profile_registry import ProfileRegistry


def get_standard_profile_registry() -> ProfileRegistry:
    """Instantiates and registers the four canonical format profiles."""
    reg = ProfileRegistry()
    reg.register_profile(get_presentation_profile())
    reg.register_profile(get_handout_profile())
    reg.register_profile(get_worksheet_profile())
    reg.register_profile(get_scientific_document_profile())
    return reg


__all__ = [
    "get_presentation_profile",
    "get_handout_profile",
    "get_worksheet_profile",
    "get_scientific_document_profile",
    "get_standard_profile_registry",
]
