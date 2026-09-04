"""
KIR AI Document Intelligence — Domain Packs Index.

Exports registration functions for all domain packs.
"""

from app.libraries.packs.academic_writing_pack import register_academic_writing_pack
from app.libraries.packs.data_literacy_pack import register_data_literacy_pack
from app.libraries.packs.experiment_pack import register_experiment_pack
from app.libraries.packs.pedagogy_pack import register_pedagogy_pack
from app.libraries.packs.presentation_pack import register_presentation_pack
from app.libraries.packs.research_education_pack import register_research_education_pack
from app.libraries.packs.scientific_thinking_pack import register_scientific_thinking_pack
from app.libraries.packs.universal_pack import register_universal_pack

__all__ = [
    "register_universal_pack",
    "register_pedagogy_pack",
    "register_scientific_thinking_pack",
    "register_research_education_pack",
    "register_academic_writing_pack",
    "register_experiment_pack",
    "register_data_literacy_pack",
    "register_presentation_pack",
]
