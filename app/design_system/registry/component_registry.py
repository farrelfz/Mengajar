"""
Universal Design System — Component Registry.

Phase 3B.0: Canonical component specifications with artifact compatibility enforcement,
slot validation, and token bindings (INV-DESIGN-010).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from app.design_system.contracts.components import (
    ComponentCategory,
    SlotSpec,
    ComponentSpec,
)


class ComponentRegistry:
    """Registry maintaining typed document components and artifact compatibility."""

    def __init__(self) -> None:
        self._components: Dict[str, ComponentSpec] = {}
        self._initialize_standard_components()

    def _initialize_standard_components(self) -> None:
        """Registers canonical base components across document types."""
        standard_components = [
            # 1. Presentation Slide Header
            ComponentSpec(
                component_id="presentation_slide_header",
                category=ComponentCategory.HEADER,
                allowed_artifacts=("PRESENTATION",),
                slots=(
                    SlotSpec(name="title", is_required=True, allowed_content_types=("text",)),
                    SlotSpec(name="subtitle", is_required=False, allowed_content_types=("text",)),
                ),
                min_width_pt=400.0,
                min_height_pt=40.0,
                token_bindings={
                    "title": "typography.presentation.title",
                    "subtitle": "typography.presentation.subtitle",
                },
                density_weight=1.0,
                description="Slide title header with optional category tag or subtitle",
            ),

            # 2. Presentation Card
            ComponentSpec(
                component_id="presentation_card",
                category=ComponentCategory.CARD,
                allowed_artifacts=("PRESENTATION",),
                slots=(
                    SlotSpec(name="heading", is_required=True, allowed_content_types=("text",)),
                    SlotSpec(name="body", is_required=True, allowed_content_types=("text",)),
                    SlotSpec(name="icon", is_required=False, allowed_content_types=("icon",)),
                ),
                min_width_pt=180.0,
                min_height_pt=120.0,
                token_bindings={
                    "heading": "typography.presentation.card_title",
                    "body": "typography.presentation.body",
                },
                density_weight=1.5,
                description="High-contrast modular card for 16:9 presentation slides",
            ),

            # 3. Handout Section Header
            ComponentSpec(
                component_id="handout_section_header",
                category=ComponentCategory.HEADER,
                allowed_artifacts=("HANDOUT", "SCIENTIFIC_DOCUMENT"),
                slots=(
                    SlotSpec(name="numbering", is_required=False, allowed_content_types=("text",)),
                    SlotSpec(name="title", is_required=True, allowed_content_types=("text",)),
                ),
                min_width_pt=300.0,
                min_height_pt=24.0,
                token_bindings={
                    "title": "typography.handout.h1",
                },
                density_weight=0.8,
                description="Monotonic reading hierarchy section header",
            ),

            # 4. Handout Callout Box
            ComponentSpec(
                component_id="handout_callout",
                category=ComponentCategory.CALLOUT_BOX,
                allowed_artifacts=("HANDOUT", "WORKSHEET"),
                slots=(
                    SlotSpec(name="title", is_required=False, allowed_content_types=("text",)),
                    SlotSpec(name="content", is_required=True, allowed_content_types=("text",)),
                ),
                min_width_pt=250.0,
                min_height_pt=50.0,
                token_bindings={
                    "content": "typography.handout.body",
                },
                density_weight=1.2,
                description="Didactic callout box for key concepts, notes, or tips",
            ),

            # 5. Worksheet Response Workspace (STRICT: WORKSHEET ONLY)
            ComponentSpec(
                component_id="worksheet_response_workspace",
                category=ComponentCategory.RESPONSE_WORKSPACE,
                allowed_artifacts=("WORKSHEET",),
                slots=(
                    SlotSpec(name="prompt", is_required=True, allowed_content_types=("text",)),
                    SlotSpec(name="workspace_lines", is_required=False, allowed_content_types=("workspace",)),
                ),
                min_width_pt=250.0,
                min_height_pt=60.0,
                token_bindings={
                    "prompt": "typography.worksheet.prompt",
                },
                density_weight=1.0,
                is_anti_spoiling_sensitive=True,
                description="Student writing or drawing space with anti-spoiling guarantees",
            ),

            # 6. Scientific Evidence Card (SCIENTIFIC_DOCUMENT & HANDOUT ONLY)
            ComponentSpec(
                component_id="scientific_evidence_card",
                category=ComponentCategory.EVIDENCE_CARD,
                allowed_artifacts=("SCIENTIFIC_DOCUMENT", "HANDOUT"),
                slots=(
                    SlotSpec(name="claim", is_required=True, allowed_content_types=("text",)),
                    SlotSpec(name="evidence_source", is_required=True, allowed_content_types=("text",)),
                    SlotSpec(name="confidence", is_required=False, allowed_content_types=("text",)),
                ),
                min_width_pt=300.0,
                min_height_pt=45.0,
                token_bindings={
                    "claim": "typography.scientific.claim",
                    "evidence_source": "typography.scientific.citation",
                },
                density_weight=1.2,
                description="Evidence-backed assertion card referencing explicit data citations",
            ),

            # 7. Stat Callout
            ComponentSpec(
                component_id="stat_callout",
                category=ComponentCategory.STAT_CALLOUT,
                allowed_artifacts=("PRESENTATION", "HANDOUT"),
                slots=(
                    SlotSpec(name="stat_value", is_required=True, allowed_content_types=("text",)),
                    SlotSpec(name="label", is_required=True, allowed_content_types=("text",)),
                ),
                min_width_pt=100.0,
                min_height_pt=60.0,
                token_bindings={
                    "stat_value": "typography.presentation.stat_number",
                    "label": "typography.presentation.caption",
                },
                density_weight=1.0,
                description="High-impact numeric metric display",
            ),
        ]

        for comp in standard_components:
            self.register_component(comp)

    def register_component(self, spec: ComponentSpec) -> None:
        """Registers a component specification."""
        self._components[spec.component_id] = spec

    def get_component(self, component_id: str) -> Optional[ComponentSpec]:
        """Retrieves component spec by ID."""
        return self._components.get(component_id)

    def list_components_for_artifact(self, artifact_type: str) -> List[ComponentSpec]:
        """Lists all components permitted for the specified artifact type."""
        return [c for c in self._components.values() if c.is_allowed_for(artifact_type)]

    def validate_component_usage(
        self, component_id: str, artifact_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates whether a component can be legally rendered in the specified artifact.
        Enforces INV-DESIGN-010.
        """
        spec = self.get_component(component_id)
        if not spec:
            return False, f"Unknown component '{component_id}'"
        if not spec.is_allowed_for(artifact_type):
            return False, (
                f"Component '{component_id}' (category {spec.category.value}) is not allowed "
                f"in artifact type '{artifact_type}'. Allowed in: {list(spec.allowed_artifacts)}"
            )
        return True, None

    def list_components(self) -> List[ComponentSpec]:
        """Returns all registered component specs."""
        return list(self._components.values())
