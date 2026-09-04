"""
Base ProductionStage abstract class and contract.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any
from app.orchestration.contracts import (
    FailureCategory,
    FailureSeverity,
    ProductionFailure,
    ProductionJobContext,
    StageExecutionResult,
    StageState,
    WorkflowStageType,
)


class ProductionStage(ABC):
    """Abstract base class for all orchestrator workflow stages."""

    @property
    @abstractmethod
    def stage_id(self) -> str:
        """Unique stage identifier."""
        pass

    @property
    @abstractmethod
    def stage_type(self) -> WorkflowStageType:
        """Categorical stage type."""
        pass

    def should_execute(self, context: ProductionJobContext) -> bool:
        """Evaluates whether the stage should run given current context."""
        return True

    def validate_input(self, context: ProductionJobContext) -> list[str]:
        """Validates that prerequisite data exists in context."""
        return []

    @abstractmethod
    def run(self, context: ProductionJobContext) -> StageExecutionResult:
        """Execute stage logic."""
        pass

    def execute(self, context: ProductionJobContext) -> StageExecutionResult:
        """Template method wrapping validation, execution, and timing."""
        start_time = time.perf_counter()

        if not self.should_execute(context):
            return StageExecutionResult(
                stage_id=self.stage_id,
                state=StageState.SKIPPED,
                duration_ms=0.0,
            )

        val_errors = self.validate_input(context)
        if val_errors:
            duration = (time.perf_counter() - start_time) * 1000.0
            return StageExecutionResult(
                stage_id=self.stage_id,
                state=StageState.FAILED,
                failure=ProductionFailure(
                    stage_id=self.stage_id,
                    category=FailureCategory.INPUT,
                    severity=FailureSeverity.FATAL,
                    message=f"Input validation failed: {'; '.join(val_errors)}",
                    retryable=False,
                ),
                duration_ms=round(duration, 2),
            )

        try:
            res = self.run(context)
            duration = (time.perf_counter() - start_time) * 1000.0
            res.duration_ms = round(duration, 2)
            return res
        except Exception as ex:
            duration = (time.perf_counter() - start_time) * 1000.0
            return StageExecutionResult(
                stage_id=self.stage_id,
                state=StageState.FAILED,
                failure=ProductionFailure(
                    stage_id=self.stage_id,
                    category=FailureCategory.INTERNAL,
                    severity=FailureSeverity.FATAL,
                    message=str(ex),
                    retryable=False,
                ),
                duration_ms=round(duration, 2),
            )
