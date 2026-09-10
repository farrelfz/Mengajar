"""
Universal Document Intelligence System V5 — Canonical Artifact Production Context.

Phase 3D: Unified, traceable runtime context tracking the full generation lifecycle,
source-to-render lineage, quality authority evaluations, and versioned repair histories.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.integration.artifact_bridge.contracts import RenderArtifact
from app.integration.render_execution.renderer_result import RendererExecutionResult
from app.intelligence.schemas import UniversalKnowledgeManifest
from app.intelligence.transformation.intent import ResolvedArtifactIntent
from app.orchestration.production_state import ProductionState, ProductionStateMachine
from app.quality.contracts.authority import UnifiedQualityReport
from app.quality.repair.contracts import ConvergenceState
from app.quality.repair.transaction import RepairTransactionRecord


@dataclass
class ArtifactProductionContext:
    """Canonical runtime context for an individual artifact production execution."""

    job_id: str
    artifact_type: str  # PRESENTATION, HANDOUT, WORKSHEET, SCIENTIFIC_DOCUMENT
    source_input: str
    output_dir: Path
    source_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Lifecycle progression artifacts
    source_manifest: Optional[UniversalKnowledgeManifest] = None
    artifact_intent: Optional[ResolvedArtifactIntent] = None
    selected_knowledge: Optional[Any] = None
    semantic_blueprint: Optional[Any] = None
    render_artifact: Optional[RenderArtifact] = None
    render_result: Optional[RendererExecutionResult] = None
    quality_authority_result: Optional[UnifiedQualityReport] = None
    
    # Repair and convergence state
    iteration: int = 0
    repair_history: List[RepairTransactionRecord] = field(default_factory=list)
    convergence_state: ConvergenceState = ConvergenceState.IN_PROGRESS
    
    # State tracking and metrics
    state_machine: ProductionStateMachine = field(default_factory=ProductionStateMachine)
    timing_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def state(self) -> ProductionState:
        """Convenience property returning current lifecycle state."""
        return self.state_machine.current_state

    def record_stage_time(self, stage_name: str, duration_sec: float) -> None:
        """Records deterministic timing metric for a completed stage."""
        self.timing_metrics[stage_name] = round(duration_sec, 4)

    def transition_state(
        self,
        target_state: ProductionState,
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Invokes state machine transition and keeps context synchronized."""
        self.state_machine.transition(
            target_state=target_state,
            iteration=self.iteration,
            reason=reason,
            metadata=metadata,
        )

    def get_source_references(self) -> Tuple[str, ...]:
        """Extracts all source references presently retained in the blueprint."""
        if not self.semantic_blueprint:
            return ()
        bp = self.semantic_blueprint
        refs: List[str] = []
        if hasattr(bp, "slides"):
            for s in bp.slides:
                refs.extend(getattr(s, "source_refs", []))
        elif hasattr(bp, "sections"):
            for sec in bp.sections:
                refs.extend(getattr(sec, "source_unit_ids", []))
                refs.extend(getattr(sec, "source_refs", []))
        elif hasattr(bp, "activities"):
            for act in bp.activities:
                refs.extend(getattr(act, "target_knowledge_unit_ids", []))
                refs.extend(getattr(act, "source_refs", []))
        elif hasattr(bp, "arguments"):
            for arg in bp.arguments:
                refs.append(getattr(arg, "claim_unit_id", ""))
                refs.extend(getattr(arg, "supporting_evidence_unit_ids", []))
        return tuple(dict.fromkeys(r for r in refs if r))
