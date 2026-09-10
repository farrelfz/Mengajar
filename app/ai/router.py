"""
KIR AI Document Intelligence — 9Router AI Provider Client.

9Router is the primary cloud AI provider.
All requests go through httpx with tenacity retry logic.
API key is read from settings.nine_router_api_key (SecretStr).
"""

from __future__ import annotations

import json
import time

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from typing import Any

from app.ai.client import AICapability, AIClient, GenerationRequest, GenerationResponse
from app.config.settings import get_settings
from app.core.exceptions import ModelTimeoutError, ProviderError
from app.core.logging import get_logger

log = get_logger(__name__)

# Default fallback model capabilities
_CAPABILITY_FALLBACK_MAP: dict[AICapability, str] = {
    AICapability.SEMANTIC_REASONING: "reasoning",
    AICapability.STRUCTURED_OUTPUT: "reasoning",
    AICapability.LONG_CONTEXT: "long_context",
    AICapability.CONTENT_WRITING: "fast",
    AICapability.CRITIQUE: "reasoning",
    AICapability.FALLBACK: "fast",
    AICapability.LOCAL_OFFLINE: "fast",
}

_SUPPORTED = list(_CAPABILITY_FALLBACK_MAP.keys())


class NineRouterClient(AIClient):
    """HTTP client for the 9Router AI routing service (OpenAI-compatible).

    Connects to the local or cloud 9Router gateway (default: http://127.0.0.1:20128/v1),
    routing requests to configured models (Gemini, Codex, Qwen, Kimi, etc.).
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._settings = settings
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

    @property
    def chat_url(self) -> str:
        """Construct the chat completions endpoint."""
        if self._base_url.endswith("/v1"):
            return f"{self._base_url}/chat/completions"
        return f"{self._base_url}/v1/chat/completions"

    @property
    def models_url(self) -> str:
        """Construct the models endpoint."""
        if self._base_url.endswith("/v1"):
            return f"{self._base_url}/models"
        return f"{self._base_url}/v1/models"

    def resolve_model(self, capability: AICapability) -> str:
        """Resolve model name from settings or capability preset."""
        # 1. Direct active model override
        if self._settings.active_model:
            return self._settings.active_model

        # 2. Capability based preset
        cap_type = _CAPABILITY_FALLBACK_MAP.get(capability, "default")
        if cap_type == "fast" and self._settings.ai_fast_model:
            return self._settings.ai_fast_model
        if cap_type == "reasoning" and self._settings.ai_reasoning_model:
            return self._settings.ai_reasoning_model
        if cap_type == "long_context" and self._settings.ai_long_context_model:
            return self._settings.ai_long_context_model

        # 3. Default model
        return self._settings.ai_default_model or "ag/gemini-3.7-flash-high"

    async def ping(self) -> tuple[bool, float, str]:
        """Check gateway reachability and response latency."""
        start = time.monotonic()
        headers = {}
        api_key = self._api_key_getter
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(self.models_url, headers=headers)
                elapsed_ms = (time.monotonic() - start) * 1000
                if resp.status_code == 200:
                    return True, elapsed_ms, "Gateway OK"
                return False, elapsed_ms, f"HTTP {resp.status_code}"
        except Exception as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            return False, elapsed_ms, str(exc)

    async def list_models(self) -> list[dict]:
        """Fetch available models from the 9Router gateway."""
        headers = {}
        api_key = self._api_key_getter
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(self.models_url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("data", [])
        except Exception as exc:
            log.warning("9router.list_models_failed", error=str(exc))
        return []

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        model = self.resolve_model(request.required_capability)
        api_key = self._api_key_getter

        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.user_prompt})

        payload: dict = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "stream": False,
        }

        if request.json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Content-Type": "application/json",
            "X-Job-ID": request.job_id or "unknown",
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        log.info(
            "9router.request",
            model=model,
            capability=request.required_capability,
            job_id=request.job_id,
            step=request.step,
        )

        start = time.monotonic()

        try:
            response = await self._post_with_retry(
                self.chat_url,
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

        content: str = ""
        prompt_tokens: int | None = None
        completion_tokens: int | None = None
        total_tokens: int | None = None

        resp_text = response.text.strip()
        if resp_text.startswith("data:") or "text/event-stream" in response.headers.get("content-type", ""):
            chunks: list[str] = []
            for line in resp_text.splitlines():
                line = line.strip()
                if not line or line.startswith(":") or line == "data: [DONE]":
                    continue
                if line.startswith("data:"):
                    raw_chunk = line[5:].strip()
                    try:
                        chunk_data: dict[str, Any] = json.loads(raw_chunk)
                        if "choices" in chunk_data and chunk_data["choices"]:
                            delta = chunk_data["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                chunks.append(str(delta["content"]))
                        usage_chunk = chunk_data.get("usage")
                        if isinstance(usage_chunk, dict):
                            prompt_tokens = usage_chunk.get("prompt_tokens")
                            completion_tokens = usage_chunk.get("completion_tokens")
                    except Exception:
                        pass
            content = "".join(chunks)
            if prompt_tokens is not None and completion_tokens is not None:
                total_tokens = prompt_tokens + completion_tokens
        else:
            try:
                data: dict[str, Any] = response.json()
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
                fallback_model = self._settings.ai_default_model or "ag/gemini-3.7-flash-high"
                if response.status_code == 400 and model != fallback_model:
                    log.warning(
                        "9router.model_fallback",
                        attempted_model=model,
                        fallback_model=fallback_model,
                        job_id=request.job_id,
                        error=error_msg,
                    )
                    payload["model"] = fallback_model
                    model = fallback_model
                    response = await self._post_with_retry(
                        self.chat_url,
                        headers=headers,
                        payload=payload,
                    )
                    resp_text = response.text.strip()
                    try:
                        data = response.json()
                    except Exception:
                        data = {}
                    if response.status_code >= 400:
                        error_msg = data.get("error", {}).get("message", response.text[:200])
                        raise ProviderError(
                            f"9Router error {response.status_code}: {error_msg}",
                            provider=self.provider_name,
                            http_status=response.status_code,
                            job_id=request.job_id,
                            step=request.step,
                        )
                else:
                    raise ProviderError(
                        f"9Router error {response.status_code}: {error_msg}",
                        provider=self.provider_name,
                        http_status=response.status_code,
                        job_id=request.job_id,
                        step=request.step,
                    )

            # Parse OpenAI chat completions format
            if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                choice = data["choices"][0]
                if isinstance(choice, dict):
                    if "message" in choice and isinstance(choice["message"], dict):
                        content = str(choice["message"].get("content") or "")
                    elif "text" in choice:
                        content = str(choice.get("text") or "")
            elif "content" in data and isinstance(data["content"], list) and data["content"]:
                # Fallback for Anthropic style responses
                block = data["content"][0]
                if isinstance(block, dict):
                    content = str(block.get("text", ""))

            usage = data.get("usage", {})
            if isinstance(usage, dict):
                prompt_tokens = usage.get("prompt_tokens") or usage.get("input_tokens")
                completion_tokens = usage.get("completion_tokens") or usage.get("output_tokens")
                total_tokens = usage.get("total_tokens") or (
                    (prompt_tokens or 0) + (completion_tokens or 0)
                )

        log.info(
            "9router.response",
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
            total_tokens=total_tokens,
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
