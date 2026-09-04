"""
KIR AI Document Intelligence — Composition Bridge.

Bridges semantic intelligence blueprints (Level A/B/C) to physical page compositions.
Decoupled architecture: orchestrates page structure and delegates parameter extraction
and rendering to registered capabilities.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.blueprints.contracts import SemanticMaterialBlueprint
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.resolver import LibraryResolver
from app.composition.schemas import (
    ContentBlock,
    DocumentComposition,
    PageComposition,
    PageRegion,
    RegionRole,
)
from app.design.schemas import ComponentFamily
from app.formats.resolution import resolve_format
from app.intelligence.schemas import DocumentMode
from app.libraries import register_all_default_capabilities
from app.rendering.schemas import AssetMetadata, RenderTarget

log = logging.getLogger(__name__)


class CompositionBridge:
    """Transforms a SemanticMaterialBlueprint into a concrete DocumentComposition."""

    def __init__(
        self,
        registry: CapabilityRegistry | None = None,
        resolver: LibraryResolver | None = None,
    ) -> None:
        self.registry = registry or register_all_default_capabilities()
        self.resolver = resolver or LibraryResolver(self.registry)

    def compose_material(
        self,
        material: SemanticMaterialBlueprint,
        output_dir: Path | None = None,
        assets_dir: Path | None = None,
        target_format: str | None = None,
        target_format_override: str | None = None,
    ) -> tuple[DocumentComposition, list[AssetMetadata]]:
        """Map semantic material sequence to layout pages and render capabilities."""
        resolved_assets_dir = assets_dir or (output_dir / "assets" if output_dir else Path("/tmp/kir_assets"))
        resolved_assets_dir.mkdir(parents=True, exist_ok=True)

        # 1. Resolve capabilities for all pedagogical steps
        resolution_map = self.resolver.resolve(material.production, material.content)

        # 2. Authoritative Physical Format Resolution
        requested_format = target_format or target_format_override or material.production.target_format
        resolved_fmt = resolve_format(
            explicit_format=requested_format,
            artifact_type=material.production.target_artifact,
        )
        mode = resolved_fmt.legacy_document_mode

        pages: list[PageComposition] = []
        generated_assets: list[AssetMetadata] = []

        # 3. Deterministic Page Allocation & Capability Execution
        for page_idx, step in enumerate(material.pedagogy.sequence, start=1):
            resolution = resolution_map.get(step.id)
            cap_id = resolution.selected_capability_id if resolution else "presentation.concept_introduction"
            cap = self.registry.get(cap_id)

            block_id = f"step_{step.id[:8]}_{page_idx}"

            # Derive component family and render target directly from capability metadata
            if cap:
                comp_family = cap.metadata.component_family
                render_target = cap.metadata.render_target
            else:
                comp_family = ComponentFamily.TEXT_BLOCK
                render_target = RenderTarget.HTML

            rendered_html: str | None = None

            # Execute capability renderer
            if cap:
                try:
                    spec_params = resolution.resolved_parameters if resolution else {}

                    # Auto-extract parameters via decentralized capability extractor if missing
                    if not spec_params or len(spec_params) <= 1:
                        spec_params = cap.extract_parameters(step, material)

                    spec_model = cap.spec_model
                    try:
                        spec_instance = spec_model(**spec_params)
                    except Exception as err:
                        log.debug("Fallback to default spec for %s: %s", cap_id, err)
                        spec_instance = spec_model()

                    cap_output = cap.renderer.render(spec_instance)

                    if cap.metadata.preferred_renderer in ["svg", "reportlab", "matplotlib"]:
                        asset_file = resolved_assets_dir / f"{block_id}.svg"
                        asset_file.write_text(cap_output.rendered_content, encoding="utf-8")

                        asset_meta = AssetMetadata(
                            asset_id=block_id,
                            asset_type=cap.metadata.category,
                            source_component_id=block_id,
                            render_engine=render_target,
                            format="svg",
                            path=str(asset_file.resolve()),
                            width=cap_output.width_px,
                            height=cap_output.height_px,
                        )
                        generated_assets.append(asset_meta)
                        rendered_html = f'<div class="svg-visual-container">{cap_output.rendered_content}</div>'
                    else:
                        rendered_html = cap_output.rendered_content

                except Exception as exc:
                    log.warning("Failed to render capability %s: %s", cap_id, exc)
                    rendered_html = f'<div class="card error-card"><h3>{step.purpose}</h3><p>{material.content.metadata.title}</p></div>'

            # Build content block
            content_block = ContentBlock(
                block_id=block_id,
                component_family=comp_family,
                source_unit_ids=step.content_ref_ids or [step.id],
                rendered_html=rendered_html,
            )

            primary_region = PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[content_block],
            )

            page = PageComposition(
                page_number=page_idx,
                page_type="slide" if mode == DocumentMode.PRESENTATION_16_9 else "document_page",
                composition_type="capability_driven",
                regions={RegionRole.PRIMARY: primary_region},
                source_unit_ids=step.content_ref_ids or [step.id],
                metadata={
                    "step_purpose": step.purpose,
                    "semantic_type": step.semantic_type.value,
                    "capability_id": cap_id,
                },
            )
            pages.append(page)

        composition = DocumentComposition(
            mode=mode,
            format_id=resolved_fmt.id,
            theme_reference="default",
            source_blueprint_id=material.material_id,
            pages=pages,
            metadata={
                "title": material.content.metadata.title,
                "domain": material.content.metadata.domain.value,
                "audience": material.content.metadata.audience.value,
                "format_id": resolved_fmt.id,
                "format_name": resolved_fmt.display_name,
            },
        )

        return composition, generated_assets
