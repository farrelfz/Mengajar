"""
KIR AI Document Intelligence — Exception Hierarchy.

All exceptions must derive from KIRError and carry job_id + step
context for traceability in logs and error recovery.

Hierarchy
---------
KIRError
├── ConfigError
├── InputError
│   ├── NormalizationError
│   └── SegmentationError
├── ClassificationError
│   └── ResearchRoleDetectionError
├── ValidationError
│   ├── SchemaValidationError
│   └── StructuredOutputError
├── RelationshipError
├── ImportanceScoringError
├── VisualIntentError
├── BlueprintError
├── AIError
│   ├── ModelUnavailableError
│   ├── ModelTimeoutError
│   ├── ProviderError
│   └── FallbackExhaustedError
├── SourceFidelityError
└── PipelineError
    └── AgentError
"""

from __future__ import annotations

from typing import Any


class KIRError(Exception):
    """Base exception for all KIR errors.

    Every exception carries:
    - job_id: the active pipeline job identifier (None if not yet assigned)
    - step: the pipeline step where the error occurred
    - details: optional structured metadata for logging
    """

    def __init__(
        self,
        message: str,
        *,
        job_id: str | None = None,
        step: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.job_id = job_id
        self.step = step
        self.details = details or {}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={str(self)!r}, "
            f"job_id={self.job_id!r}, "
            f"step={self.step!r})"
        )


# ── Configuration ─────────────────────────────────────────────────────────────

class ConfigError(KIRError):
    """Raised when application configuration is invalid or missing."""


# ── Input layer ───────────────────────────────────────────────────────────────

class InputError(KIRError):
    """Base for errors occurring during raw input processing."""


class NormalizationError(InputError):
    """Raised when input normalization fails or produces empty output."""


class SegmentationError(InputError):
    """Raised when content segmentation fails to identify any units."""


# ── Classification layer ──────────────────────────────────────────────────────

class ClassificationError(KIRError):
    """Raised when semantic classification cannot determine a valid type."""


class ResearchRoleDetectionError(ClassificationError):
    """Raised when KTI research role detection fails for a content unit."""


# ── Validation layer ──────────────────────────────────────────────────────────

class ValidationError(KIRError):
    """Base for schema or structured output validation failures."""


class SchemaValidationError(ValidationError):
    """Raised when a Pydantic schema fails validation."""

    def __init__(
        self,
        message: str,
        *,
        pydantic_errors: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.pydantic_errors = pydantic_errors or []


class StructuredOutputError(ValidationError):
    """Raised when LLM structured output cannot be parsed or is missing
    required fields after repair attempts."""

    def __init__(
        self,
        message: str,
        *,
        raw_output: str | None = None,
        repair_attempts: int = 0,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.raw_output = raw_output
        self.repair_attempts = repair_attempts


# ── Relationship layer ────────────────────────────────────────────────────────

class RelationshipError(KIRError):
    """Raised when relationship extraction produces a conflict or invalid graph."""


# ── Scoring / intent ──────────────────────────────────────────────────────────

class ImportanceScoringError(KIRError):
    """Raised when importance scoring cannot produce a result."""


class VisualIntentError(KIRError):
    """Raised when visual intent detection produces an invalid result."""


# ── Blueprint layer ───────────────────────────────────────────────────────────

class BlueprintError(KIRError):
    """Raised when the Content-to-Blueprint algorithm cannot produce a valid proposal."""


# ── AI provider layer ─────────────────────────────────────────────────────────

class AIError(KIRError):
    """Base for AI provider errors."""


class ModelUnavailableError(AIError):
    """Raised when no model is available for the requested capability."""

    def __init__(
        self,
        message: str,
        *,
        capability: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.capability = capability


class ModelTimeoutError(AIError):
    """Raised when a model request exceeds the configured timeout."""

    def __init__(
        self,
        message: str,
        *,
        timeout_seconds: float | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds


class ProviderError(AIError):
    """Raised when a specific AI provider returns an error response."""

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        http_status: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.provider = provider
        self.http_status = http_status


class FallbackExhaustedError(AIError):
    """Raised when the entire fallback chain has been exhausted without success."""

    def __init__(
        self,
        message: str,
        *,
        tried_providers: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.tried_providers = tried_providers or []


# ── Source fidelity ───────────────────────────────────────────────────────────

class SourceFidelityError(KIRError):
    """Raised when the AI output contains content that cannot be traced to the
    source material (e.g. invented data, citations, or conclusions)."""

    def __init__(
        self,
        message: str,
        *,
        fidelity_violations: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.fidelity_violations = fidelity_violations or []


# ── Pipeline / Agent layer ────────────────────────────────────────────────────

class PipelineError(KIRError):
    """Raised for unrecoverable errors at the pipeline orchestration level."""


class AgentError(PipelineError):
    """Raised when an agent fails to complete its responsibility."""

    def __init__(
        self,
        message: str,
        *,
        agent_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.agent_name = agent_name
