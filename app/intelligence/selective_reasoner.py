"""
Selective AI Reasoner for Ambiguous Blocks & Complex Conceptual Relationships.

Batches only low-confidence or highly ambiguous semantic blocks into a single
structured LLM call rather than making individual calls per block.
"""

from __future__ import annotations

import time
from typing import Any
from pydantic import BaseModel, Field

from app.ai.client import AICapability, GenerationRequest
from app.core.logging import get_logger
from app.intelligence.ai_usage_policy import AIUsagePolicy
from app.intelligence.output_validator import OutputValidator
from app.intelligence.schemas import (
    AIClassificationOutput,
    ConfidenceLevel,
    ContentType,
    ContentUnit,
)

log = get_logger(__name__)


class BatchedClassificationRequest(BaseModel):
    document_context: dict[str, Any]
    ambiguous_blocks: list[dict[str, Any]]


class BatchedClassificationResponse(BaseModel):
    resolved_blocks: list[AIClassificationOutput] = Field(default_factory=list)


_SELECTIVE_SYSTEM_PROMPT = (
    "You are an expert instructional scientist and document intelligence reasoner.\n"
    "You are given a small batch of ambiguous content blocks from a document.\n"
    "Classify their true semantic ContentType and determine if they represent a causal mechanism, "
    "theoretical explanation, procedure, or research role.\n"
    "Return valid JSON matching the BatchedClassificationResponse schema."
)


class SelectiveReasoner:
    """Selectively resolves ambiguous concepts using batched AI reasoning."""

    def __init__(
        self,
        validator: OutputValidator | None = None,
        policy: AIUsagePolicy | None = None,
    ) -> None:
        self.validator = validator or OutputValidator()
        self.policy = policy or AIUsagePolicy()

    async def resolve_ambiguous_blocks(
        self,
        ambiguous_units: list[ContentUnit],
        document_title: str,
        domain: str = "general",
        job_id: str | None = None,
    ) -> dict[str, AIClassificationOutput]:
        """Resolve a batch of ambiguous units in exactly ONE LLM call."""
        if not ambiguous_units:
            return {}

        start_time = time.time()
        blocks_payload = [
            {
                "unit_id": u.unit_id,
                "heading": u.title or "General Section",
                "text": u.normalized_text[:400],
            }
            for u in ambiguous_units
        ]

        user_prompt = (
            f"DOCUMENT TITLE: {document_title}\n"
            f"DOMAIN: {domain}\n"
            f"AMBIGUOUS BLOCKS TO CLASSIFY:\n"
            + "\n---\n".join(
                f"ID: {b['unit_id']}\nHEADING: {b['heading']}\nTEXT: {b['text']}"
                for b in blocks_payload
            )
        )

        request = GenerationRequest(
            system_prompt=_SELECTIVE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            required_capability=AICapability.SEMANTIC_REASONING,
            json_mode=True,
            job_id=job_id,
            step="selective_ai_reasoning",
        )

        resolved_map: dict[str, AIClassificationOutput] = {}
        try:
            res: BatchedClassificationResponse = await self.validator.generate_and_validate(
                request=request,
                schema=BatchedClassificationResponse,
            )
            elapsed = time.time() - start_time
            self.policy.record_call(
                task_name="Task 3: Selective AI Reasoning",
                purpose="Resolve ambiguous semantic blocks",
                model="gateway",
                latency=elapsed,
                input_count=len(ambiguous_units),
                output_count=len(res.resolved_blocks),
                success=True,
            )
            for item in res.resolved_blocks:
                resolved_map[item.unit_id] = item

        except Exception as exc:
            elapsed = time.time() - start_time
            log.warning("selective_reasoner.fallback: %s", exc)
            self.policy.record_call(
                task_name="Task 3: Selective AI Reasoning",
                purpose="Resolve ambiguous semantic blocks",
                model="gateway",
                latency=elapsed,
                input_count=len(ambiguous_units),
                output_count=0,
                success=False,
                error=str(exc),
            )
            # Safe deterministic fallback
            for u in ambiguous_units:
                resolved_map[u.unit_id] = AIClassificationOutput(
                    unit_id=u.unit_id,
                    content_type=ContentType.EXPLANATION,
                    confidence=ConfidenceLevel.MEDIUM,
                    reasons=["Local deterministic fallback on AI exception"],
                )

        return resolved_map
