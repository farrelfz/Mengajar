"""
KIR AI Document Intelligence — Composition Resolver.
"""
from app.composition.schemas import PageComposition, ContentBlock, RegionRole
from app.formats.schemas import FormatConfig
from app.formats.a4_portrait import a4_portrait_config
from app.formats.a4_landscape import a4_landscape_config, a4_config
from app.formats.presentation_16_9 import presentation_config
from app.intelligence.schemas import DocumentMode
from app.composition.region_allocator import allocate_to_regions
from app.composition.segmentation import evaluate_boundary, BoundaryStrategy
from app.composition.continuation_engine import split_blocks_for_continuation

class CompositionResolver:
    """Resolves semantic content groups into physical layout pages."""
    def __init__(self, mode: DocumentMode):
        self.mode = mode
        if mode == DocumentMode.A4_PORTRAIT:
            self.config = a4_portrait_config
        elif mode in (DocumentMode.A4_LANDSCAPE, DocumentMode.A4_TUTORIAL):
            self.config = a4_landscape_config
        else:
            self.config = presentation_config
        
    def resolve_group_to_pages(self, group, blocks: list[ContentBlock], start_page_num: int) -> list[PageComposition]:
        """
        Takes a semantic group and its mapped content blocks,
        splits them if necessary according to format config,
        and returns physical pages.
        """
        # Mock word count logic for demonstration
        word_count = len(blocks) * 40
        unit_ids = group.unit_ids
        
        boundary = evaluate_boundary(word_count, self.config, unit_ids)
        
        pages = []
        if boundary.decision == BoundaryStrategy.CREATE_CONTINUATION:
            # Determine how many blocks are safe
            safe_blocks = max(1, self.config.max_words_per_page // 40)
            segments = split_blocks_for_continuation(blocks, max_blocks_per_page=safe_blocks, source_group_id=group.group_id)
            
            for i, (segment_blocks, meta) in enumerate(segments):
                regions = allocate_to_regions(segment_blocks)
                pages.append(PageComposition(
                    page_number=start_page_num + i,
                    page_type="CONTINUATION" if i > 0 else group.blueprint_candidate.value,
                    composition_type="continuation" if i > 0 else self._select_template(group),
                    regions=regions,
                    source_unit_ids=[uid for b in segment_blocks for uid in b.source_unit_ids],
                    continuation=meta
                ))
        else:
            regions = allocate_to_regions(blocks)
            pages.append(PageComposition(
                page_number=start_page_num,
                page_type=group.blueprint_candidate.value,
                composition_type=self._select_template(group),
                regions=regions,
                source_unit_ids=unit_ids
            ))
            
        return pages
        
    def _select_template(self, group) -> str:
        if self.mode == DocumentMode.PRESENTATION_16_9:
            if group.blueprint_candidate.value == "title_block":
                return "hero"
            if group.blueprint_candidate.value == "data_evidence_block":
                return "data_focus"
            return "editorial"
        else:
            return "editorial"
