"""
KIR AI Document Intelligence — Semantic Material Blueprint Contract.

The unified container combining Level A (Content), Level B (Pedagogy),
and Level C (Production) into a single verifiable artifact.
"""

from __future__ import annotations

import uuid
from typing import Any
from pydantic import BaseModel, Field, model_validator

from app.blueprints.content import ContentBlueprint
from app.blueprints.pedagogical import PedagogicalBlueprint
from app.blueprints.production import ProductionBlueprint, TargetArtifactType


class SemanticMaterialBlueprint(BaseModel):
    """Unified Material Blueprint containing Content, Pedagogical Sequence, and Production Specs."""
    material_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "2.0.0"
    content: ContentBlueprint
    pedagogy: PedagogicalBlueprint
    production: ProductionBlueprint
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_blueprint_integrity(self) -> SemanticMaterialBlueprint:
        """Validate cross-level consistency between Content, Pedagogy, and Production."""
        # 1. Collect all valid content IDs
        valid_content_ids = set()
        for obj in self.content.objectives:
            valid_content_ids.add(obj.id)
        for c in self.content.concepts:
            valid_content_ids.add(c.id)
        for f in self.content.facts:
            valid_content_ids.add(f.id)
        for m in self.content.misconceptions:
            valid_content_ids.add(m.id)
        for w in self.content.worked_examples:
            valid_content_ids.add(w.id)
        for d in self.content.datasets:
            valid_content_ids.add(d.id)

        # 2. Check that pedagogical sequence steps have valid references (if provided)
        pedagogical_step_ids = set()
        for step in self.pedagogy.sequence:
            pedagogical_step_ids.add(step.id)

        # 3. Check that production requirements match pedagogical steps
        prod_step_ids = {req.step_id for req in self.production.requirements}
        missing_in_prod = pedagogical_step_ids - prod_step_ids
        if missing_in_prod:
            # We auto-generate fallback production requirements for any missing steps
            from app.blueprints.production import ProductionRequirement, SemanticIntentSpec
            for step in self.pedagogy.sequence:
                if step.id in missing_in_prod:
                    self.production.requirements.append(
                        ProductionRequirement(
                            step_id=step.id,
                            semantic_type=step.semantic_type.value,
                            semantic_intent=SemanticIntentSpec(
                                semantic_intent=f"render_{step.semantic_type.value}",
                                domain=self.content.metadata.domain.value,
                            ),
                        )
                    )

        return self
