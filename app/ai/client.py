"""
KIR AI Document Intelligence — AI Client Base and Data Contracts.

All AI provider clients implement AIClient.
Structured request/response contracts are defined here.
"""

from __future__ import annotations

import abc
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AICapability(str, Enum):
    """Semantic capability requirements for model selection.

    The intelligence layer requests capabilities, not specific models.
    The router resolves the appropriate provider+model combination.
    """

    SEMANTIC_REASONING = "semantic_reasoning"       # Deep content classification
    STRUCTURED_OUTPUT = "structured_output"         # Reliable JSON output
    LONG_CONTEXT = "long_context"                   # Large document processing
    CONTENT_WRITING = "content_writing"             # Text generation/transformation
    CRITIQUE = "critique"                           # Quality evaluation
    FALLBACK = "fallback"                           # Last-resort, lower quality ok
    LOCAL_OFFLINE = "local_offline"                 # Must run without internet


class GenerationRequest(BaseModel):
    """Structured request sent to any AI provider.

    Fields
    ------
    system_prompt : str
        Role and behavioral contract for the model.
    user_prompt : str
        The actual task content.
    required_capability : AICapability
        What capability this request needs.
    max_tokens : int
        Maximum response length.
    temperature : float
        Sampling temperature [0.0, 2.0]. Use 0.1-0.3 for structured output.
    json_mode : bool
        If True, instruct the model to output valid JSON.
    schema_hint : str | None
        Optional JSON schema description to include in the prompt.
    job_id : str | None
        Active job ID for logging.
    step : str | None
        Pipeline step name for logging.
    metadata : dict[str, Any]
        Extra metadata passed through to the provider.
    """

    system_prompt: str
    user_prompt: str
    required_capability: AICapability = AICapability.SEMANTIC_REASONING
    max_tokens: int = Field(default=4096, ge=64, le=32768)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    json_mode: bool = False
    schema_hint: str | None = None
    job_id: str | None = None
    step: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GenerationResponse(BaseModel):
    """Standardized response from any AI provider.

    Fields
    ------
    content : str
        Raw text output from the model.
    model_used : str
        The actual model identifier that generated this response.
    provider : str
        Provider name ("9router", "ollama", "rule_based").
    capability_used : AICapability
        The capability that was fulfilled.
    prompt_tokens : int | None
        Input tokens (if reported by provider).
    completion_tokens : int | None
        Output tokens (if reported by provider).
    total_tokens : int | None
        Total tokens (if reported by provider).
    latency_ms : float | None
        Request latency in milliseconds.
    fallback_used : bool
        True if a fallback provider was used.
    degraded : bool
        True if response is from rule-based fallback (low quality).
    """

    model_config = {"protected_namespaces": ()}

    content: str
    model_used: str
    provider: str
    capability_used: AICapability
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    latency_ms: float | None = None
    fallback_used: bool = False
    degraded: bool = False


class AIClient(abc.ABC):
    """Abstract base class for AI provider clients.

    All providers (9Router, Ollama, future) implement this interface.
    The intelligence layer only interacts with AIClient — never directly
    with provider-specific implementations.
    """

    @abc.abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Send a generation request and return a structured response.

        Parameters
        ----------
        request:
            The generation request with prompts and parameters.

        Returns
        -------
        GenerationResponse
            Standardized response regardless of provider.

        Raises
        ------
        ModelTimeoutError
            If the request exceeds the configured timeout.
        ProviderError
            If the provider returns an error status.
        ModelUnavailableError
            If the provider is not accessible.
        """

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier."""

    @property
    @abc.abstractmethod
    def supported_capabilities(self) -> list[AICapability]:
        """List of capabilities this provider supports."""
