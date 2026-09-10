"""Unit tests for local 9Router client, OpenAI-compatible formatting, and router manager."""
import pytest
from unittest.mock import AsyncMock, patch
import httpx

from app.ai.client import AICapability, GenerationRequest
from app.ai.router import NineRouterClient
from app.cli.router_manager import RouterStatus, get_router_status
from app.cli.router_manager import test_single_model as run_test_single_model
from app.config.settings import AppSettings, reset_settings


@pytest.fixture(autouse=True)
def clean_settings():
    reset_settings()
    yield
    reset_settings()


def test_settings_auto_discover_local_9router():
    """Verify settings defaults to local 9Router on port 20128."""
    settings = AppSettings(
        nine_router_base_url="http://127.0.0.1:20128/v1",
        ai_default_model="ag/gemini-3.7-flash-high",
    )
    assert settings.nine_router_base_url == "http://127.0.0.1:20128/v1"
    assert settings.ai_default_model == "ag/gemini-3.7-flash-high"
    assert settings.get_effective_model() == "ag/gemini-3.7-flash-high"

    # Test override
    settings.set_active_model("ollama/kimi-k2.5")
    assert settings.get_effective_model() == "ollama/kimi-k2.5"


def test_ninerouter_client_resolves_openai_urls():
    """Verify client constructs /chat/completions and /models endpoints."""
    client = NineRouterClient()
    assert client.chat_url.endswith("/chat/completions")
    assert client.models_url.endswith("/models")


@pytest.mark.asyncio
async def test_ninerouter_generate_openai_format():
    """Verify client sends OpenAI chat payload and parses response correctly."""
    client = NineRouterClient()

    openai_response_payload = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1700000000,
        "model": "ag/gemini-3.7-flash-high",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Halo dari 9Router lokal!",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 15,
            "completion_tokens": 8,
            "total_tokens": 23,
        },
    }

    mock_resp = httpx.Response(
        status_code=200,
        json=openai_response_payload,
        request=httpx.Request("POST", client.chat_url),
    )

    req = GenerationRequest(
        user_prompt="Uji coba 9Router",
        system_prompt="Kamu asisten AI",
        required_capability=AICapability.SEMANTIC_REASONING,
    )

    with patch.object(client, "_post_with_retry", new=AsyncMock(return_value=mock_resp)) as mock_post:
        result = await client.generate(req)

        assert result.content == "Halo dari 9Router lokal!"
        assert result.prompt_tokens == 15
        assert result.completion_tokens == 8
        assert result.total_tokens == 23

        # Verify sent payload
        call_args = mock_post.call_args
        payload = call_args.kwargs["payload"]
        assert payload["messages"][0] == {"role": "system", "content": "Kamu asisten AI"}
        assert payload["messages"][1] == {"role": "user", "content": "Uji coba 9Router"}


@pytest.mark.asyncio
async def test_test_single_model_success():
    """Verify test_single_model returns latency and response content."""
    fake_response = {
        "choices": [
            {
                "message": {"content": "Metode ilmiah adalah proses sistematis."}
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 6, "total_tokens": 16},
    }
    mock_resp = httpx.Response(
        status_code=200,
        json=fake_response,
        request=httpx.Request("POST", "http://127.0.0.1:20128/v1/chat/completions"),
    )

    with patch("app.ai.router.NineRouterClient._post_with_retry", new=AsyncMock(return_value=mock_resp)):
        res = await run_test_single_model("ag/gemini-3.7-flash-high")
        assert res["success"] is True
        assert res["response"] == "Metode ilmiah adalah proses sistematis."
        assert res["tokens"] == 16
        assert res["latency"] >= 0.0
