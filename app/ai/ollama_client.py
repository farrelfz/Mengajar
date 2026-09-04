"""
KIR AI Document Intelligence — Ollama AI Provider Client.

Ollama is the local/offline AI provider.
Used as a fallback or as the primary provider when offline_mode is True.
"""

from __future__ import annotations

import time

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.ai.client import AICapability, AIClient, GenerationRequest, GenerationResponse
from app.config.settings import get_settings
from app.core.exceptions import ModelTimeoutError, ProviderError
from app.core.logging import get_logger

log = get_logger(__name__)

# Ollama local models capability mapping.
# For local models, we typically route everything to the default model (e.g. llama3).
_SUPPORTED = [
    AICapability.SEMANTIC_REASONING,
    AICapability.STRUCTURED_OUTPUT,
    AICapability.LONG_CONTEXT,
    AICapability.CONTENT_WRITING,
    AICapability.CRITIQUE,
    AICapability.FALLBACK,
    AICapability.LOCAL_OFFLINE,
]


class OllamaClient(AIClient):
    """HTTP client for local Ollama service."""

    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._timeout = settings.ollama_timeout
        self._default_model = settings.ollama_default_model

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def supported_capabilities(self) -> list[AICapability]:
        return _SUPPORTED

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        model = self._default_model

        messages = [
            {"role": "system", "content": request.system_prompt},
            {"role": "user", "content": request.user_prompt},
        ]

        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": request.temperature,
            },
        }

        if request.json_mode:
            payload["format"] = "json"

        log.debug(
            "ollama.request",
            model=model,
            capability=request.required_capability,
            job_id=request.job_id,
            step=request.step,
        )

        start = time.monotonic()

        try:
            response = await self._post_with_retry(
                f"{self._base_url}/api/chat",
                payload=payload,
            )
        except httpx.TimeoutException as exc:
            elapsed = (time.monotonic() - start) * 1000
            raise ModelTimeoutError(
                f"Ollama request timed out after {elapsed:.0f}ms",
                timeout_seconds=self._timeout,
                job_id=request.job_id,
                step=request.step,
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderError(
                f"Failed to connect to Ollama at {self._base_url}: {exc}",
                provider=self.provider_name,
                job_id=request.job_id,
                step=request.step,
            ) from exc

        elapsed_ms = (time.monotonic() - start) * 1000

        try:
            data = response.json()
        except Exception as exc:
            raise ProviderError(
                f"Ollama returned non-JSON response: {response.text[:200]}",
                provider=self.provider_name,
                http_status=response.status_code,
                job_id=request.job_id,
                step=request.step,
            ) from exc

        if response.status_code >= 400:
            error_msg = data.get("error", response.text[:200])
            raise ProviderError(
                f"Ollama error {response.status_code}: {error_msg}",
                provider=self.provider_name,
                http_status=response.status_code,
                job_id=request.job_id,
                step=request.step,
            )

        content = data.get("message", {}).get("content", "")
        
        # Ollama provides eval_count and prompt_eval_count
        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)

        log.info(
            "ollama.response",
            model=model,
            latency_ms=elapsed_ms,
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            job_id=request.job_id,
        )

        return GenerationResponse(
            content=content,
            model_used=model,
            provider=self.provider_name,
            capability_used=request.required_capability,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=elapsed_ms,
        )

    @retry(
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=4),
    )
    async def _post_with_retry(
        self,
        url: str,
        payload: dict,
    ) -> httpx.Response:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(url, json=payload)
            if response.status_code in (429, 502, 503, 504):
                response.raise_for_status()
            return response
