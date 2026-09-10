"""
Universal Document Intelligence System V5 — Repair Actuation & Structural Recomposition.

Phase 4: Physical actuation layer enabling causal artifact transformations.
"""

from app.quality.repair.actuation.contracts import (
    RepairActuationRequest,
    RepairActuationResult,
    RepairActuator,
)
from app.quality.repair.actuation.mutation_layers import TransformationLayer
from app.quality.repair.actuation.registry import RepairActuatorRegistry

__all__ = [
    "TransformationLayer",
    "RepairActuationRequest",
    "RepairActuationResult",
    "RepairActuator",
    "RepairActuatorRegistry",
]
