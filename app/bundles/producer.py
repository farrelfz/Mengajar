"""
Multi-Artifact Curriculum Bundle Producer.

Executes coordinated end-to-end production of multi-artifact educational bundles.
"""

from __future__ import annotations

from pathlib import Path
import uuid
import pymupdf

from app.blueprints.content import KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.bundles.allocation import ContentAllocationPolicy
from app.bundles.coherence import BundleCoherenceValidator
from app.bundles.contracts import (
    ArtifactBundleRequest,
    BundleItemResult,
    BundleResult,
)
from app.bundles.planner import BundlePlanner
from app.orchestration.production_pipeline import MaterialProductionPipeline


class ArtifactBundleProducer:
    """Orchestrates production of multi-artifact curriculum bundles."""

    def __init__(self, pipeline: MaterialProductionPipeline | None = None) -> None:
        self.pipeline = pipeline or MaterialProductionPipeline()
        self.planner = BundlePlanner()

    async def produce_bundle(
        self,
        request: ArtifactBundleRequest,
        output_dir: Path | str = "outputs/bundles",
    ) -> BundleResult:
        """Produce all coordinated artifacts requested in the bundle."""
        bundle_id = f"bundle_{uuid.uuid4().hex[:8]}"
        out_base = Path(output_dir) / bundle_id
        out_base.mkdir(parents=True, exist_ok=True)

        # 1. Plan shared objectives & coverage matrix
        objectives, matrix = self.planner.plan_bundle(request)

        # 2. Produce each artifact with role-differentiated configuration
        items: list[BundleItemResult] = []
        domain_enum = KnowledgeDomain.PHYSICS if "physic" in request.domain.lower() else KnowledgeDomain.GENERAL_SCIENCE

        for role in request.artifacts:
            role_spec = ContentAllocationPolicy.get_role_spec(role)
            fmt_id = role_spec["format_id"]
            strat = role_spec["strategy"]
            target_artifact_str = role_spec["target_artifact"]
            target_artifact_enum = (
                TargetArtifactType.TEACHING_PRESENTATION
                if "presentation" in target_artifact_str
                else TargetArtifactType.DETAILED_HANDOUT
            )

            item_filename = f"{request.concept.lower().replace(' ', '_')}_{role.value}"
            res = await self.pipeline.produce_artifact(
                raw_input=request.raw_input or f"# {request.concept}\nEducational material for {role.value}.",
                source_hint=f"{item_filename}.md",
                domain=domain_enum,
                audience=request.audience,
                target_artifact=target_artifact_enum,
                output_dir=out_base,
                output_filename=item_filename,
                target_format=fmt_id,
                director_enabled=True,
                preferred_strategy=strat,
            )

            # Inspect PDF with PyMuPDF
            page_count = 1
            if res.pdf_path and Path(res.pdf_path).exists():
                doc = pymupdf.open(res.pdf_path)
                page_count = len(doc)
                doc.close()

            stages = (
                [s.stage_type.value for s in res.material_direction.journey.stages]
                if res.material_direction
                else []
            )

            items.append(
                BundleItemResult(
                    role=role,
                    format_id=fmt_id,
                    pdf_path=res.pdf_path or "",
                    page_count=page_count,
                    objectives_covered=role_spec["objectives_focus"],
                    journey_stages=stages,
                )
            )

        # 3. Validate Cross-Artifact Coherence
        is_valid, red_score, comp_score, warnings = BundleCoherenceValidator.validate_bundle(
            items=items,
            shared_objectives=objectives,
            coverage_matrix=matrix,
        )

        trace = {
            "bundle_id": bundle_id,
            "roles_produced": [r.value for r in request.artifacts],
            "warnings": warnings,
            "redundancy_score": red_score,
            "complementarity_score": comp_score,
        }

        return BundleResult(
            bundle_id=bundle_id,
            concept=request.concept,
            audience=request.audience.value,
            duration_minutes=request.duration_minutes,
            items=items,
            shared_objectives=objectives,
            coverage_matrix=matrix,
            redundancy_score=red_score,
            complementarity_score=comp_score,
            coherence_valid=is_valid,
            trace=trace,
        )
