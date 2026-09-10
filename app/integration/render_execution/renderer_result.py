"""
Universal Knowledge Core — Renderer Execution Result Contract.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Captures end-to-end execution outcome, rendered file locations, page counts,
traceability references, and execution metrics.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field


class RendererExecutionResult(BaseModel):
    """Authoritative outcome of executing a legacy renderer via an adapter."""
    model_config = ConfigDict(frozen=True)

    success: bool
    artifact_type: str
    html_path: Optional[Path] = None
    pdf_path: Optional[Path] = None
    total_pages: int = 0
    source_element_ids_rendered: Tuple[str, ...] = Field(default_factory=tuple)
    rendered_objects_count: int = 0
    execution_duration_ms: float = 0.0
    errors: Tuple[str, ...] = Field(default_factory=tuple)
    warnings: Tuple[str, ...] = Field(default_factory=tuple)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
