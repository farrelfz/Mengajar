"""
Authoritative Pipeline Stage Registry & Centralized Progress Reporter.

Single authoritative source of truth for:
- Pipeline stage definitions and count (strictly 10 stages)
- Stage start, completion, and transition formatting
- Stage progress invariants
- Repair iteration & QA round dimensional separation
- Pipeline terminal state classification
"""

from __future__ import annotations

import time
import inspect
import asyncio
from enum import Enum
from dataclasses import dataclass
from typing import Any, Callable, Awaitable

from app.orchestration.failures import PipelineProgressSynchronizationError


@dataclass(frozen=True)
class PipelineStageDefinition:
    number: int
    key: str
    name: str
    description: str

    @property
    def stage_number(self) -> int:
        """Backward compatibility alias for number."""
        return self.number

    @property
    def stage_id(self) -> str:
        """Backward compatibility alias for key."""
        return self.key


class PipelineStage(str, Enum):
    STRUCTURAL_PARSING = "STRUCTURAL_PARSING"
    LOCAL_SEMANTIC_CLASSIFICATION = "LOCAL_SEMANTIC_CLASSIFICATION"
    SELECTIVE_AI_REASONING = "SELECTIVE_AI_REASONING"
    CONTENT_MANIFEST = "CONTENT_MANIFEST"
    PRESENTATION_ARCHITECTURE = "PRESENTATION_ARCHITECTURE"
    VISUAL_GRAMMAR = "VISUAL_GRAMMAR"
    DETERMINISTIC_COMPOSITION = "DETERMINISTIC_COMPOSITION"
    PDF_RENDERING = "PDF_RENDERING"
    QUALITY_ASSURANCE = "QUALITY_ASSURANCE"
    REPAIR_REFINEMENT = "REPAIR_REFINEMENT"


PIPELINE_STAGES: tuple[PipelineStageDefinition, ...] = (
    PipelineStageDefinition(
        number=1,
        key=PipelineStage.STRUCTURAL_PARSING.value,
        name="Structural Parsing & Source Integrity",
        description="Parsing Markdown structural tree and raw block isolation",
    ),
    PipelineStageDefinition(
        number=2,
        key=PipelineStage.LOCAL_SEMANTIC_CLASSIFICATION.value,
        name="Local Semantic Classification",
        description="Applying deterministic semantic taxonomy and heuristic scoring",
    ),
    PipelineStageDefinition(
        number=3,
        key=PipelineStage.SELECTIVE_AI_REASONING.value,
        name="Selective AI Reasoning",
        description="Resolving ambiguous semantic relationships via AI Gateway",
    ),
    PipelineStageDefinition(
        number=4,
        key=PipelineStage.CONTENT_MANIFEST.value,
        name="Content Manifest & Coverage Planning",
        description="Planning content coverage and extracting critical/important concepts",
    ),
    PipelineStageDefinition(
        number=5,
        key=PipelineStage.PRESENTATION_ARCHITECTURE.value,
        name="Presentation Architecture",
        description="Building presentation narrative architecture and cognitive load distribution",
    ),
    PipelineStageDefinition(
        number=6,
        key=PipelineStage.VISUAL_GRAMMAR.value,
        name="Visual Grammar & Semantic Layout",
        description="Assigning visual intent and canonical layouts via visual grammar matrix",
    ),
    PipelineStageDefinition(
        number=7,
        key=PipelineStage.DETERMINISTIC_COMPOSITION.value,
        name="Deterministic HTML Composition",
        description="Composing semantic presentation layout and responsive grid templates",
    ),
    PipelineStageDefinition(
        number=8,
        key=PipelineStage.PDF_RENDERING.value,
        name="High-Precision PDF Rendering",
        description="Rendering presentation artifact via headless Chromium and PyMuPDF",
    ),
    PipelineStageDefinition(
        number=9,
        key=PipelineStage.QUALITY_ASSURANCE.value,
        name="Semantic + Visual Quality Assurance",
        description="Evaluating 25 quality gates across semantic and visual dimensions",
    ),
    PipelineStageDefinition(
        number=10,
        key=PipelineStage.REPAIR_REFINEMENT.value,
        name="Repair & Refinement Loop",
        description="Deterministic convergence loop, artifact invalidation, and revalidation",
    ),
)

TOTAL_PIPELINE_STAGES: int = len(PIPELINE_STAGES)
TOTAL_STAGES: int = TOTAL_PIPELINE_STAGES  # Backward compatibility alias
StageDefinition = PipelineStageDefinition  # Backward compatibility alias
CANONICAL_STAGES = list(PIPELINE_STAGES)  # Backward compatibility alias

STAGE_BY_NUMBER: dict[int, PipelineStageDefinition] = {s.number: s for s in PIPELINE_STAGES}
STAGE_BY_KEY: dict[str, PipelineStageDefinition] = {s.key: s for s in PIPELINE_STAGES}


class PipelineTerminalStatus(str, Enum):
    PIPELINE_SUCCEEDED = "PIPELINE_SUCCEEDED"
    PIPELINE_SUCCEEDED_WITH_WARNINGS = "PIPELINE_SUCCEEDED_WITH_WARNINGS"
    PIPELINE_BLOCKED_QUALITY = "PIPELINE_BLOCKED_QUALITY"
    PIPELINE_FAILED_SYSTEM = "PIPELINE_FAILED_SYSTEM"
    PIPELINE_CANCELLED = "PIPELINE_CANCELLED"


@dataclass(frozen=True)
class ProgressEvent:
    """Canonical runtime progress contract shared across pipeline, server, and frontend."""
    stage_number: int
    total_stages: int
    stage_key: str
    title: str
    status: str  # "start" | "done" | "transition"
    detail: str = ""
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        if self.total_stages != TOTAL_PIPELINE_STAGES:
            raise PipelineProgressSynchronizationError(
                f"ProgressEvent invariant violated: total_stages={self.total_stages} (must be {TOTAL_PIPELINE_STAGES})"
            )
        if not (1 <= self.stage_number <= self.total_stages):
            raise PipelineProgressSynchronizationError(
                f"ProgressEvent invariant violated: stage_number={self.stage_number} (must be 1..{self.total_stages})"
            )


class PipelineStageRegistry:
    """Authoritative helper for querying canonical pipeline stages."""

    @classmethod
    def get_stage(cls, stage: int | str | PipelineStage | PipelineStageDefinition) -> PipelineStageDefinition:
        if isinstance(stage, PipelineStageDefinition):
            return stage
        if isinstance(stage, PipelineStage):
            return STAGE_BY_KEY[stage.value]
        if isinstance(stage, int):
            if stage not in STAGE_BY_NUMBER:
                raise PipelineProgressSynchronizationError(
                    f"Invalid stage number {stage}. Allowed: 1..{TOTAL_PIPELINE_STAGES}"
                )
            return STAGE_BY_NUMBER[stage]
        if isinstance(stage, str):
            if stage in STAGE_BY_KEY:
                return STAGE_BY_KEY[stage]
            # Check TASK_X string format
            if stage.startswith("TASK_"):
                try:
                    num = int(stage.split("_")[1])
                    if num in STAGE_BY_NUMBER:
                        return STAGE_BY_NUMBER[num]
                except Exception:
                    pass
            raise PipelineProgressSynchronizationError(
                f"Unknown stage key '{stage}'. Must be one of: {list(STAGE_BY_KEY.keys())}"
            )
        raise PipelineProgressSynchronizationError(f"Unsupported stage identifier type: {type(stage)}")

    @classmethod
    def total_stages(cls) -> int:
        return TOTAL_PIPELINE_STAGES

    @classmethod
    def format_header(cls, stage: int | str | PipelineStage | PipelineStageDefinition) -> str:
        defn = cls.get_stage(stage)
        return f"TASK {defn.number}/{TOTAL_PIPELINE_STAGES} — {defn.name}"

    @classmethod
    async def notify_progress(
        cls,
        callback: Callable[..., Awaitable[None] | None] | None,
        stage: int | str | PipelineStage | PipelineStageDefinition,
        status: str,
        message: str,
        extra: dict[str, Any] | None = None,
    ) -> None:
        if not callback:
            return
        defn = cls.get_stage(stage)
        now = time.time()
        event = ProgressEvent(
            stage_number=defn.number,
            total_stages=TOTAL_PIPELINE_STAGES,
            stage_key=defn.key,
            title=defn.name,
            status=status,
            detail=message,
            timestamp=now,
        )

        sig = inspect.signature(callback)
        param_count = len(sig.parameters)
        if param_count == 1:
            res = callback(event)
        else:
            res = callback(defn.number, TOTAL_PIPELINE_STAGES, defn.name, status, message)
        if inspect.iscoroutine(res):
            await res


class PipelineProgressReporter:
    """
    Centralized progress reporter enforcing invariant-verified logging.
    
    Guarantees:
    1. Start, Complete, and Transition messages strictly share stage.number and TOTAL_PIPELINE_STAGES.
    2. Progress denominator is always derived from TOTAL_PIPELINE_STAGES (strictly 10).
    3. Stage progression order and completion invariants are enforced at runtime.
    4. Repair iterations and QA rounds are tracked in their own dimensions without mutating task numbers.
    5. Terminal status distinguishes between expected quality block and system crashes.
    """

    def __init__(
        self,
        listener: Callable[..., Awaitable[None] | None] | None = None,
        log_sink: Callable[[str], None] | None = None,
    ) -> None:
        self.listener = listener
        self.log_sink = log_sink or print
        self.active_stage: PipelineStageDefinition | None = None
        self.completed_stages: list[PipelineStageDefinition] = []
        self.stage_start_times: dict[int, float] = {}

    def _validate_stage(self, stage: PipelineStageDefinition) -> None:
        if not (1 <= stage.number <= TOTAL_PIPELINE_STAGES):
            raise PipelineProgressSynchronizationError(
                f"Invalid progress state: {stage.number}/{TOTAL_PIPELINE_STAGES}"
            )

    # ─────────────────────────────────────────────────────────────
    # Stage Lifecycle (Synchronous Core)
    # ─────────────────────────────────────────────────────────────

    def stage_started(self, stage: PipelineStageDefinition, detail: str = "") -> dict[str, Any]:
        self._validate_stage(stage)
        self.active_stage = stage
        self.stage_start_times[stage.number] = time.time()

        start_line = f"TASK {stage.number}/{TOTAL_PIPELINE_STAGES}\n{stage.name}"
        if detail:
            start_line += f"\n└─ {detail}"
        self.log_sink(start_line)

        if self.listener:
            evt = ProgressEvent(
                stage_number=stage.number,
                total_stages=TOTAL_PIPELINE_STAGES,
                stage_key=stage.key,
                title=stage.name,
                status="running",
                detail=detail,
            )
            res = self.listener(evt)
            if inspect.iscoroutine(res):
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(res)
                except RuntimeError:
                    asyncio.run(res)

        return {
            "type": "stage_start",
            "stage_number": stage.number,
            "total_stages": TOTAL_PIPELINE_STAGES,
            "stage_name": stage.name,
            "detail": detail,
            "formatted": start_line,
        }

    def stage_completed(
        self,
        stage: PipelineStageDefinition,
        message: str = "",
        duration: float = 0.0,
    ) -> dict[str, Any]:
        self._validate_stage(stage)
        if self.active_stage and stage.number != self.active_stage.number:
            raise PipelineProgressSynchronizationError(
                f"Cannot complete stage {stage.number} while active stage is {self.active_stage.number}"
            )

        if not message:
            message = f"{stage.name} selesai"

        if not duration and stage.number in self.stage_start_times:
            duration = time.time() - self.stage_start_times[stage.number]

        completion_line = f"✓ [SELESAI {stage.number}/{TOTAL_PIPELINE_STAGES}] {message}"
        if duration > 0:
            completion_line += f" ({duration:.2f}s)"
        self.log_sink(completion_line)

        if self.listener:
            evt = ProgressEvent(
                stage_number=stage.number,
                total_stages=TOTAL_PIPELINE_STAGES,
                stage_key=stage.key,
                title=stage.name,
                status="completed",
                detail=message,
            )
            res = self.listener(evt)
            if inspect.iscoroutine(res):
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(res)
                except RuntimeError:
                    asyncio.run(res)

        self.completed_stages.append(stage)
        self.active_stage = None

        return {
            "type": "stage_complete",
            "stage_number": stage.number,
            "total_stages": TOTAL_PIPELINE_STAGES,
            "stage_name": stage.name,
            "message": message,
            "duration": duration,
            "formatted": completion_line,
        }

    def stage_transition(
        self,
        next_stage: PipelineStageDefinition,
        is_retry: bool = False,
    ) -> dict[str, Any]:
        self._validate_stage(next_stage)
        if not is_retry and self.completed_stages:
            last_completed = self.completed_stages[-1]
            if next_stage.number != last_completed.number + 1:
                raise PipelineProgressSynchronizationError(
                    f"Invalid stage transition from {last_completed.number} to {next_stage.number}. Expected {last_completed.number + 1}"
                )

        transition_line = f"⏩ Lanjut ke: [{next_stage.number}/{TOTAL_PIPELINE_STAGES}] {next_stage.name}..."
        self.log_sink(transition_line)

        return {
            "type": "stage_transition",
            "next_stage_number": next_stage.number,
            "total_stages": TOTAL_PIPELINE_STAGES,
            "next_stage_name": next_stage.name,
            "formatted": transition_line,
        }

    # ─────────────────────────────────────────────────────────────
    # Sub-step Dimensions: QA Rounds & Repair Iterations
    # ─────────────────────────────────────────────────────────────

    def qa_round_started(self, round_idx: int, pdf_version: int, detail: str = "") -> str:
        line = f"└─ QA ROUND {round_idx} (Artifact Version: PDF v{pdf_version})"
        if detail:
            line += f"\n└─ {detail}"
        self.log_sink(line)
        return line

    def qa_round_completed(
        self,
        round_idx: int,
        passed_gates: int,
        total_gates: int = 25,
        critical_failures: int = 0,
        repairable_issues: int = 0,
    ) -> str:
        line = (
            f"✓ QA ROUND {round_idx} selesai:\n"
            f"{passed_gates}/{total_gates} gates passed\n"
            f"{critical_failures} critical failures\n"
            f"{repairable_issues} repairable issues"
        )
        self.log_sink(line)
        return line

    def repair_iteration_started(self, iteration: int, max_iterations: int = 2, plan_summary: str = "") -> str:
        line = f"└─ REPAIR ITERATION {iteration}/{max_iterations}"
        if plan_summary:
            line += f"\nRepair plan: {plan_summary}"
        self.log_sink(line)
        return line

    def repair_iteration_completed(
        self,
        iteration: int,
        attempted: int,
        successful: int = 0,
        verified: int = 0,
        unresolved: int = 0,
        invalidated_artifacts: list[str] | None = None,
    ) -> str:
        line = f"Repair Execution (Iteration {iteration}):\n{attempted} attempted, {verified} verified by QA, {unresolved} unresolved"
        if invalidated_artifacts:
            line += f"\nArtifacts invalidated: {', '.join(invalidated_artifacts)}"
        self.log_sink(line)
        return line

    # ─────────────────────────────────────────────────────────────
    # Terminal Pipeline Decisions
    # ─────────────────────────────────────────────────────────────

    def terminal_decision(
        self,
        status: PipelineTerminalStatus,
        reason: str,
        final_qa_round: int = 1,
        artifact_version: int = 1,
        export_approved: bool = True,
    ) -> str:
        if status == PipelineTerminalStatus.PIPELINE_BLOCKED_QUALITY:
            block_msg = (
                "⛔ PIPELINE BLOCKED — QUALITY GATES NOT CONVERGED\n"
                f"Status: {status.value}\n"
                f"Reason: {reason}\n"
                f"Final QA: Round {final_qa_round}\n"
                f"Artifact: PDF v{artifact_version}\n"
                "Export: BLOCKED"
            )
            self.log_sink(block_msg)
            return block_msg

        if status == PipelineTerminalStatus.PIPELINE_FAILED_SYSTEM:
            fail_msg = (
                "❌ PIPELINE SYSTEM ERROR\n"
                f"Status: {status.value}\n"
                f"Reason: {reason}"
            )
            self.log_sink(fail_msg)
            return fail_msg

        success_msg = (
            "✓ Pipeline selesai\n"
            f"Status: {status.value}\n"
            f"Reason: {reason}\n"
            f"Final QA: Round {final_qa_round}\n"
            f"Artifact: PDF v{artifact_version}\n"
            f"Export: {'APPROVED' if export_approved else 'BLOCKED'}"
        )
        self.log_sink(success_msg)
        return success_msg

    # ─────────────────────────────────────────────────────────────
    # Async Bridge for Event Dispatch
    # ─────────────────────────────────────────────────────────────

    async def notify_stage_started(self, stage: PipelineStageDefinition, detail: str = "") -> None:
        self.stage_started(stage, detail)
        if self.listener:
            await PipelineStageRegistry.notify_progress(
                self.listener, stage, "start", detail
            )

    async def notify_stage_completed(
        self,
        stage: PipelineStageDefinition,
        message: str,
        duration: float = 0.0,
    ) -> None:
        self.stage_completed(stage, message, duration)
        if self.listener:
            await PipelineStageRegistry.notify_progress(
                self.listener, stage, "done", message
            )

    async def notify_stage_transition(
        self,
        next_stage: PipelineStageDefinition,
        is_retry: bool = False,
    ) -> None:
        self.stage_transition(next_stage, is_retry)
        if self.listener:
            await PipelineStageRegistry.notify_progress(
                self.listener, next_stage, "transition", f"Transitioning to {next_stage.name}"
            )
