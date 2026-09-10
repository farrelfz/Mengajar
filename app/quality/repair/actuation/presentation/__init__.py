"""
Presentation Structural Repair Actuators.
"""

from app.quality.repair.actuation.presentation.composition import PresentationCompositionActuator
from app.quality.repair.actuation.presentation.diversity_guard import (
    PresentationDiversityActuator,
    PresentationStructuralDiversityGuard,
)
from app.quality.repair.actuation.presentation.formula import PresentationFormulaRecompositionActuator
from app.quality.repair.actuation.presentation.reflow import PresentationComponentReflowActuator
from app.quality.repair.actuation.presentation.split import PresentationSlideSplitActuator

__all__ = [
    "PresentationComponentReflowActuator",
    "PresentationFormulaRecompositionActuator",
    "PresentationCompositionActuator",
    "PresentationSlideSplitActuator",
    "PresentationDiversityActuator",
    "PresentationStructuralDiversityGuard",
]
