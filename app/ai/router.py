"""
KIR AI Document Intelligence — 9Router AI Provider Client.

9Router is the primary cloud AI provider.
All requests go through httpx with tenacity retry logic.
API key is read from settings.nine_router_api_key (SecretStr).
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

# Models available via 9Router and their capabilities
# Specific model IDs are configured by 9Router; we map by capability here.
_CAPABILITY_MODEL_MAP: dict[AICapability, str] = {
    AICapability.SEMANTIC_REASONING: "claude-sonnet-4-5",
    AICapability.STRUCTURED_OUTPUT: "claude-sonnet-4-5",
    AICapability.LONG_CONTEXT: "claude-sonnet-4-5",
    AICapability.CONTENT_WRITING: "claude-haiku-3-5",
    AICapability.CRITIQUE: "claude-sonnet-4-5",
    AICapability.FALLBACK: "claude-haiku-3-5",
    AICapability.LOCAL_OFFLINE: "claude-haiku-3-5",  # won't be used for offline
}

_SUPPORTED = list(_CAPABILITY_MODEL_MAP.keys())


class NineRouterClient(AIClient):
    """HTTP client for the 9Router AI routing service.

    9Router routes requests to the appropriate underlying model
    (Claude Sonnet, Haiku, etc.) based on the model field.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.nine_router_base_url.rstrip("/")
        self._timeout = settings.nine_router_timeout
        self._max_retries = settings.nine_router_max_retries
        self._api_key_getter = settings.nine_router_api_key_value

    @property
    def provider_name(self) -> str:
        return "9router"

    @property
    def supported_capabilities(self) -> list[AICapability]:
        return _SUPPORTED

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        model = _CAPABILITY_MODEL_MAP.get(request.required_capability, "claude-haiku-3-5")
        api_key = self._api_key_getter

        if not api_key:
            raise ProviderError(
                "9Router API key not configured",
                provider=self.provider_name,
                job_id=request.job_id,
                step=request.step,
            )

        messages = [
            {"role": "user", "content": request.user_prompt},
        ]

        payload: dict = {
            "model": model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "system": request.system_prompt,
            "messages": messages,
        }

        if request.json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Job-ID": request.job_id or "unknown",
        }

        log.debug(
            "9router.request",
            model=model,
            capability=request.required_capability,
            job_id=request.job_id,
            step=request.step,
        )

        start = time.monotonic()

        try:
            response = await self._post_with_retry(
                f"{self._base_url}/messages",
                headers=headers,
                payload=payload,
            )
        except httpx.TimeoutException as exc:
            elapsed = (time.monotonic() - start) * 1000
            raise ModelTimeoutError(
                f"9Router request timed out after {elapsed:.0f}ms",
                timeout_seconds=self._timeout,
                job_id=request.job_id,
                step=request.step,
            ) from exc

        elapsed_ms = (time.monotonic() - start) * 1000

        try:
            data = response.json()
        except Exception as exc:
            raise ProviderError(
                f"9Router returned non-JSON response: {response.text[:200]}",
                provider=self.provider_name,
                http_status=response.status_code,
                job_id=request.job_id,
                step=request.step,
            ) from exc

        if response.status_code >= 400:
            error_msg = data.get("error", {}).get("message", response.text[:200])
            raise ProviderError(
                f"9Router error {response.status_code}: {error_msg}",
                provider=self.provider_name,
                http_status=response.status_code,
                job_id=request.job_id,
                step=request.step,
            )

        content = ""
        if "content" in data and data["content"]:
            block = data["content"][0]
            content = block.get("text", "")

        usage = data.get("usage", {})
        log.info(
            "9router.response",
            model=model,
            latency_ms=elapsed_ms,
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
            job_id=request.job_id,
        )

        return GenerationResponse(
            content=content,
            model_used=model,
            provider=self.provider_name,
            capability_used=request.required_capability,
            prompt_tokens=usage.get("input_tokens"),
            completion_tokens=usage.get("output_tokens"),
            total_tokens=(usage.get("input_tokens", 0) + usage.get("output_tokens", 0)),
            latency_ms=elapsed_ms,
        )

    @retry(
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def _post_with_retry(
        self,
        url: str,
        headers: dict,
        payload: dict,
    ) -> httpx.Response:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code in (429, 502, 503, 504):
                response.raise_for_status()
            return response
