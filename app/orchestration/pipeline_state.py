"""
Authoritative Pipeline State & Artifact Dependency Graph.

Provides the single source of truth for pipeline artifacts, versioning,
deterministic dependency invalidation, quality round tracking, and
strict export invariants.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.orchestration.failures import PipelineStateSynchronizationError


class PipelineStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    PARSING = "PARSING"
    CLASSIFYING = "CLASSIFYING"
    REASONING = "REASONING"
    MANIFESTING = "MANIFESTING"
    ARCHITECTING = "ARCHITECTING"
    COMPOSING = "COMPOSING"
    RENDERING = "RENDERING"
    EVALUATING = "EVALUATING"
    REPAIRING = "REPAIRING"
    CONVERGED = "CONVERGED"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExportDecisionStatus(str, Enum):
    EXPORT_APPROVED = "EXPORT_APPROVED"
    EXPORT_APPROVED_WITH_WARNINGS = "EXPORT_APPROVED_WITH_WARNINGS"
    REPAIR_REQUIRED = "REPAIR_REQUIRED"
    BLOCKED = "BLOCKED"


class ExportDecision(BaseModel):
    status: ExportDecisionStatus
    authoritative_qa_round: int
    qa_artifact_version: int
    pdf_artifact_version: int
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class ArtifactVersionTracker(BaseModel):
    """Tracks version numbers for all core pipeline artifacts."""
    versions: dict[str, int] = Field(
        default_factory=lambda: {
            "source": 1,
            "semantic_ir": 1,
            "manifest": 1,
            "blueprint": 1,
            "composition": 1,
            "html": 1,
            "pdf": 1,
            "qa": 1,
        }
    )

    def get_version(self, artifact_name: str) -> int:
        return self.versions.get(artifact_name, 1)

    def bump_version(self, artifact_name: str) -> int:
        self.versions[artifact_name] = self.versions.get(artifact_name, 0) + 1
        return self.versions[artifact_name]


class ArtifactDependencyGraph:
    """Deterministic dependency graph for pipeline artifact invalidation.

    Graph Topology:
    SOURCE -> SEMANTIC_IR -> MANIFEST -> BLUEPRINT -> COMPOSITION -> HTML -> PDF -> QA
    """

    DEPENDENTS: dict[str, list[str]] = {
        "source": ["semantic_ir", "manifest", "blueprint", "composition", "html", "pdf", "qa"],
        "semantic_ir": ["manifest", "blueprint", "composition", "html", "pdf", "qa"],
        "manifest": ["blueprint", "composition", "html", "pdf", "qa"],
        "blueprint": ["composition", "html", "pdf", "qa"],
        "composition": ["html", "pdf", "qa"],
        "html": ["pdf", "qa"],
        "pdf": ["qa"],
        "qa": [],
    }

    @classmethod
    def get_invalidated_dependents(cls, changed_artifact: str) -> list[str]:
        """Returns ordered list of all downstream artifacts transitively invalidated."""
        return cls.DEPENDENTS.get(changed_artifact, [])


class PipelineState(BaseModel):
    """The single authoritative state machine for pipeline execution and quality evidence."""

    job_id: str
    status: PipelineStatus = PipelineStatus.INITIALIZED

    # Core Artifacts
    source_artifact: Optional[Any] = None
    semantic_artifact: Optional[Any] = None
    manifest: Optional[Any] = None
    presentation_blueprint: Optional[Any] = None
    composed_document: Optional[Any] = None
    rendered_pdf: Optional[Any] = None
    pdf_path: Optional[str] = None

    # Version Tracking
    version_tracker: ArtifactVersionTracker = Field(default_factory=ArtifactVersionTracker)

    # QA & Convergence Tracking (Strict Quality Rounds)
    qa_history: list[Any] = Field(default_factory=list)
    active_qa_result: Optional[Any] = None
    repair_history: list[Any] = Field(default_factory=list)

    # Authoritative Final Export Decision
    export_decision: Optional[ExportDecision] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def set_active_qa(self, qa_round: Any) -> None:
        """Sets the active QA round and records it into history.

        Old QA results immediately cease being the active authoritative state.
        """
        # Ensure round matches current PDF version
        current_pdf_version = self.version_tracker.get_version("pdf")
        if hasattr(qa_round, "artifact_version"):
            qa_round_version = qa_round.artifact_version
            if qa_round_version != current_pdf_version:
                raise PipelineStateSynchronizationError(
                    f"QA round version ({qa_round_version}) does not match current PDF artifact version ({current_pdf_version})",
                    diagnostics={
                        "qa_round_version": qa_round_version,
                        "current_pdf_version": current_pdf_version,
                        "qa_round_id": getattr(qa_round, "round_id", None),
                    },
                )
        self.active_qa_result = qa_round
        self.qa_history.append(qa_round)
        self.version_tracker.bump_version("qa")

    def invalidate_after_repair(self, mutated_artifact: str = "blueprint") -> list[str]:
        """Invalidates all dependent artifacts after a repair mutation.

        CRITICAL INVARIANT: Immediately resets active_qa_result to None.
        Old QA evidence CAN NEVER be used as final export evidence.
        """
        invalidated = ArtifactDependencyGraph.get_invalidated_dependents(mutated_artifact)
        for art in invalidated:
            self.version_tracker.bump_version(art)

        # Clear active dependent artifacts
        if "composition" in invalidated:
            self.composed_document = None
        if "pdf" in invalidated:
            self.rendered_pdf = None
        if "qa" in invalidated:
            self.active_qa_result = None

        return invalidated

    def record_repair_result(self, repair_res: Any) -> None:
        """Records a repair iteration result."""
        self.repair_history.append(repair_res)

    def verify_export_invariants(self) -> None:
        """Enforces all 8 strict final state invariants before permitting export."""
        # INVARIANT 1: Active QA must exist
        if self.active_qa_result is None:
            raise PipelineStateSynchronizationError(
                "Invariant 1 Violated: active_qa_result is None. Export cannot occur without active QA evidence."
            )

        active = self.active_qa_result

        # INVARIANT 2: QA artifact version == final PDF artifact version
        qa_ver = getattr(active, "artifact_version", None)
        pdf_ver = self.version_tracker.get_version("pdf")
        if qa_ver != pdf_ver:
            raise PipelineStateSynchronizationError(
                f"Invariant 2 Violated: QA artifact version ({qa_ver}) != final PDF artifact version ({pdf_ver}). Stale QA detected.",
                diagnostics={"qa_artifact_version": qa_ver, "pdf_artifact_version": pdf_ver},
            )

        # INVARIANT 3: No CRITICAL_FAILURE gates in active QA
        critical_failures = getattr(active, "critical_failures", 0)
        if critical_failures > 0:
            blocking = getattr(active, "blocking_reasons", [])
            raise PipelineStateSynchronizationError(
                f"Invariant 3 Violated: Active QA has {critical_failures} critical gate failures: {blocking}",
                diagnostics={"critical_failures": critical_failures, "blocking_reasons": blocking},
            )

        # INVARIANT 4 & 5: Check GateResult statuses
        gate_results = getattr(active, "gate_results", [])
        for g in gate_results:
            status_val = getattr(g, "status", None)
            status_str = status_val.value if hasattr(status_val, "value") else str(status_val)
            if status_str == "STALE":
                raise PipelineStateSynchronizationError(
                    f"Invariant 4 Violated: Gate {getattr(g, 'gate_id', '')} is in STALE state.",
                    diagnostics={"stale_gate": getattr(g, "gate_id", "")},
                )
            if status_str == "NOT_EVALUATED" and getattr(g, "is_blocking", True):
                raise PipelineStateSynchronizationError(
                    f"Invariant 5 Violated: Critical gate {getattr(g, 'gate_id', '')} was NOT_EVALUATED.",
                    diagnostics={"unevaluated_gate": getattr(g, "gate_id", "")},
                )

        # INVARIANT 6: Export decision must be derived from active QA only
        if self.export_decision is None:
            raise PipelineStateSynchronizationError(
                "Invariant 6 Violated: Export decision has not been evaluated."
            )
        active_round_id = getattr(active, "round_id", None)
        if self.export_decision.authoritative_qa_round != active_round_id:
            raise PipelineStateSynchronizationError(
                f"Invariant 6 Violated: Export decision round ({self.export_decision.authoritative_qa_round}) "
                f"does not match active QA round ({active_round_id}).",
                diagnostics={
                    "decision_round": self.export_decision.authoritative_qa_round,
                    "active_round": active_round_id,
                },
            )

        # INVARIANT 7: If repair occurred, qa_history length must be >= 2
        if len(self.repair_history) > 0 and len(self.qa_history) < 2:
            raise PipelineStateSynchronizationError(
                f"Invariant 7 Violated: Repairs were performed ({len(self.repair_history)}), but QA history contains fewer than 2 rounds ({len(self.qa_history)}). Missing revalidation evidence.",
                diagnostics={"repairs": len(self.repair_history), "qa_rounds": len(self.qa_history)},
            )

        # INVARIANT 8: If repair occurred, active QA must have revalidated the mutation
        if len(self.repair_history) > 0:
            if pdf_ver < 2:
                raise PipelineStateSynchronizationError(
                    f"Invariant 8 Violated: Repairs were applied but final PDF version ({pdf_ver}) was not regenerated.",
                    diagnostics={"pdf_artifact_version": pdf_ver},
                )
