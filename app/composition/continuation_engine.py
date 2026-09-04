"""
KIR AI Document Intelligence — Continuation Engine.

Splits content blocks into multiple pages while maintaining traceability metadata.
"""
from app.composition.schemas import ContentBlock, ContinuationMetadata
import math


def split_blocks_for_continuation(
    blocks: list[ContentBlock], 
    max_blocks_per_page: int, 
    source_group_id: str
) -> list[tuple[list[ContentBlock], ContinuationMetadata]]:
    """
    Splits a list of blocks into multiple segments.
    Returns a list of tuples containing the blocks for that segment and its continuation metadata.
    """
    if len(blocks) <= max_blocks_per_page:
        return [(blocks, ContinuationMetadata(
            source_group_id=source_group_id,
            sequence_position=1,
            continuation_index=0
        ))]
        
    segments = []
    num_segments = math.ceil(len(blocks) / max_blocks_per_page)
    
    for i in range(num_segments):
        start_idx = i * max_blocks_per_page
        end_idx = start_idx + max_blocks_per_page
        page_blocks = blocks[start_idx:end_idx]
        
        meta = ContinuationMetadata(
            source_group_id=source_group_id,
            sequence_position=i + 1,
            continuation_index=i
        )
        segments.append((page_blocks, meta))
        
    return segments
