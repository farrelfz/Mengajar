"""
Base Refinement Patch and Concrete Transformation Implementations.
"""

from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import Any

from app.blueprints.contracts import SemanticMaterialBlueprint
from app.composition.schemas import (
    ContentBlock,
    DocumentComposition,
    PageComposition,
    PageRegion,
    RegionRole,
)
from app.design.schemas import ComponentFamily
from app.director.contracts import LearningJourney, LearningStageType
from app.refinement.contracts import (
    RefinedArtifactBundle,
    RefinementAction,
    RefinementPatch,
    RefinementTargetLayer,
)


class BaseRefinementPatch(ABC):
    """Abstract base class for all localized refinement patches."""

    def __init__(self, action: RefinementAction) -> None:
        self.action = action

    @abstractmethod
    def apply(self, bundle: RefinedArtifactBundle) -> tuple[RefinedArtifactBundle, RefinementPatch]:
        """Applies transformation immutably to bundle, returning new bundle and patch metadata."""
        pass


class PedagogicalSequencePatch(BaseRefinementPatch):
    """Reorders learning journey stages so concept formalization precedes worked examples/practice."""

    def apply(self, bundle: RefinedArtifactBundle) -> tuple[RefinedArtifactBundle, RefinementPatch]:
        new_bundle = copy.deepcopy(bundle)
        before_stages = []
        after_stages = []

        if new_bundle.journey and new_bundle.journey.stages:
            stages = new_bundle.journey.stages
            before_stages = [s.stage_type.value for s in stages]

            # Invariant fix: If WORKED_EXAMPLE or PRACTICE is before CONCEPT_FORMALIZATION, reorder
            concept_stages = [s for s in stages if s.stage_type == LearningStageType.CONCEPT_FORMALIZATION]
            other_stages = [s for s in stages if s.stage_type != LearningStageType.CONCEPT_FORMALIZATION]

            if concept_stages:
                # Place concept formalization early (after hook/phenomenon if present)
                hook_stages = [s for s in other_stages if s.stage_type in [LearningStageType.HOOK, LearningStageType.SURFACE_INTUITION, LearningStageType.PHENOMENON if hasattr(LearningStageType, "PHENOMENON") else LearningStageType.HOOK]]
                rem_stages = [s for s in other_stages if s not in hook_stages]
                new_bundle.journey.stages = hook_stages + concept_stages + rem_stages
                after_stages = [s.stage_type.value for s in new_bundle.journey.stages]

        patch = RefinementPatch(
            patch_id=f"patch_seq_{self.action.action_id}",
            target_layer=RefinementTargetLayer.DIRECTOR,
            target_identifier="journey.stages",
            change_summary="Reordered learning stages so concept formalization precedes worked examples.",
            source_action_ids=[self.action.action_id],
            before_state={"stages": before_stages},
            after_state={"stages": after_stages},
        )
        return new_bundle, patch


class DensitySplitPatch(BaseRefinementPatch):
    """Splits overloaded text blocks across multiple pages or regions."""

    def apply(self, bundle: RefinedArtifactBundle) -> tuple[RefinedArtifactBundle, RefinementPatch]:
        new_bundle = copy.deepcopy(bundle)
        pages = new_bundle.composition.pages
        before_count = len(pages)

        # Check for pages with > 1200 characters on presentation
        new_pages: list[PageComposition] = []
        p_num = 1
        for p in pages:
            total_text = ""
            blocks_to_keep = []
            blocks_to_split = []

            for r in p.regions.values():
                for b in r.blocks:
                    content = str(b.raw_content or "")
                    if len(content) > 1200:
                        # Split into two parts
                        half = len(content) // 2
                        part1 = content[:half].rstrip()
                        part2 = content[half:].lstrip()
                        b1 = copy.deepcopy(b)
                        b1.raw_content = part1
                        b2 = copy.deepcopy(b)
                        b2.raw_content = part2
                        blocks_to_keep.append(b1)
                        blocks_to_split.append(b2)
                    else:
                        blocks_to_keep.append(b)

            p_copy = copy.deepcopy(p)
            p_copy.page_number = p_num
            if p_copy.regions and RegionRole.PRIMARY in p_copy.regions:
                p_copy.regions[RegionRole.PRIMARY].blocks = blocks_to_keep
            new_pages.append(p_copy)
            p_num += 1

            if blocks_to_split:
                # Add secondary overflow page
                overflow_page = PageComposition(
                    page_number=p_num,
                    page_type="content",
                    composition_type="single_region",
                    regions={
                        RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=blocks_to_split)
                    },
                )
                new_pages.append(overflow_page)
                p_num += 1

        new_bundle.composition.pages = new_pages

        patch = RefinementPatch(
            patch_id=f"patch_density_{self.action.action_id}",
            target_layer=RefinementTargetLayer.DENSITY,
            target_identifier="composition.pages",
            change_summary=f"Rebalanced density by splitting overloaded blocks ({before_count} -> {len(new_pages)} pages).",
            source_action_ids=[self.action.action_id],
            before_state={"page_count": before_count},
            after_state={"page_count": len(new_pages)},
        )
        return new_bundle, patch


class CapabilityReplacementPatch(BaseRefinementPatch):
    """Replaces inappropriate component families (e.g. COMPARISON_BLOCK -> STEP_BLOCK)."""

    def apply(self, bundle: RefinedArtifactBundle) -> tuple[RefinedArtifactBundle, RefinementPatch]:
        new_bundle = copy.deepcopy(bundle)
        replaced_count = 0

        for p in new_bundle.composition.pages:
            for r in p.regions.values():
                for b in r.blocks:
                    raw_lower = str(b.raw_content or "").lower()
                    if "step 1" in raw_lower and "step 2" in raw_lower:
                        if b.component_family in [ComponentFamily.COMPARISON_BLOCK, ComponentFamily.REFERENCE_BLOCK]:
                            b.component_family = ComponentFamily.STEP_BLOCK
                            replaced_count += 1

        patch = RefinementPatch(
            patch_id=f"patch_cap_{self.action.action_id}",
            target_layer=RefinementTargetLayer.CAPABILITY_SELECTION,
            target_identifier="component_family",
            change_summary=f"Replaced {replaced_count} parallel blocks with STEP_BLOCK for sequential processes.",
            source_action_ids=[self.action.action_id],
            before_state={"replaced_count": 0},
            after_state={"replaced_count": replaced_count},
        )
        return new_bundle, patch


class RedundancyDeduplicationPatch(BaseRefinementPatch):
    """Removes duplicate substantive blocks across distinct pages."""

    def apply(self, bundle: RefinedArtifactBundle) -> tuple[RefinedArtifactBundle, RefinementPatch]:
        new_bundle = copy.deepcopy(bundle)
        seen_spans = set()
        removed_count = 0

        for p in new_bundle.composition.pages:
            for r in p.regions.values():
                deduped_blocks = []
                for b in r.blocks:
                    content = str(b.raw_content or "").strip()
                    if len(content) > 50 and content in seen_spans:
                        # Replace duplicate with concise summary note
                        b_condensed = copy.deepcopy(b)
                        b_condensed.raw_content = f"[Recall: Summary of {content[:40]}...]"
                        b_condensed.component_family = ComponentFamily.CALLOUT
                        deduped_blocks.append(b_condensed)
                        removed_count += 1
                    else:
                        if len(content) > 50:
                            seen_spans.add(content)
                        deduped_blocks.append(b)
                r.blocks = deduped_blocks

        patch = RefinementPatch(
            patch_id=f"patch_red_{self.action.action_id}",
            target_layer=RefinementTargetLayer.COMPOSITION,
            target_identifier="redundant_blocks",
            change_summary=f"Condensed {removed_count} duplicate content blocks across pages.",
            source_action_ids=[self.action.action_id],
            before_state={"duplicates": removed_count},
            after_state={"duplicates": 0},
        )
        return new_bundle, patch
