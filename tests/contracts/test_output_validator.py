"""Unit tests for OutputValidator."""

import pytest
from pydantic import BaseModel, Field

from app.ai.client import AICapability, AIClient, GenerationRequest, GenerationResponse
from app.ai.fallback import FallbackChain
from app.ai.model_registry import ModelRegistry
from app.ai.model_selector import ModelSelector
from app.config.settings import AppSettings
from app.core.exceptions import StructuredOutputError
from app.intelligence.output_validator import OutputValidator


class SampleSchema(BaseModel):
    title: str
    count: int
    is_valid: bool = True
    tags: list[str] = Field(default_factory=list)


class MockAIClient(AIClient):
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.call_count = 0

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def supported_capabilities(self) -> list[AICapability]:
        return [AICapability.SEMANTIC_REASONING, AICapability.STRUCTURED_OUTPUT]

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        idx = min(self.call_count, len(self.responses) - 1)
        resp_text = self.responses[idx]
        self.call_count += 1
        return GenerationResponse(
            content=resp_text,
            model_used="mock-model",
            provider=self.provider_name,
            capability_used=request.required_capability,
        )


def make_validator_with_responses(responses: list[str]) -> tuple[OutputValidator, MockAIClient]:
    mock_client = MockAIClient(responses)
    registry = ModelRegistry()
    registry.register(mock_client)
    settings = AppSettings(
        primary_provider="mock",  # type: ignore
        fallback_to_ollama=False,
        offline_mode=False,
        nine_router_api_key="mock_key",
        max_repair_attempts=2,
    )
    selector = ModelSelector(registry=registry, settings=settings)
    fallback_chain = FallbackChain(selector=selector, registry=registry, settings=settings)
    validator = OutputValidator(fallback_chain=fallback_chain, settings=settings)
    return validator, mock_client


@pytest.mark.asyncio
async def test_validator_valid_json_success():
    """Verify standard valid JSON parses directly without repair."""
    validator, mock_client = make_validator_with_responses([
        '{"title": "Test Title", "count": 42, "is_valid": true, "tags": ["a", "b"]}'
    ])
    req = GenerationRequest(system_prompt="sys", user_prompt="usr", json_mode=True)
    res = await validator.generate_and_validate(req, SampleSchema)

    assert res.title == "Test Title"
    assert res.count == 42
    assert res.tags == ["a", "b"]
    assert mock_client.call_count == 1


@pytest.mark.asyncio
async def test_validator_strips_markdown_fences():
    """Verify markdown code fences ```json ... ``` are stripped and parsed."""
    validator, _ = make_validator_with_responses([
        '```json\n{"title": "Fenced Title", "count": 10, "is_valid": false}\n```'
    ])
    req = GenerationRequest(system_prompt="sys", user_prompt="usr", json_mode=True)
    res = await validator.generate_and_validate(req, SampleSchema)

    assert res.title == "Fenced Title"
    assert res.count == 10
    assert res.is_valid is False


@pytest.mark.asyncio
async def test_validator_auto_repair_loop_success():
    """Verify invalid JSON on first attempt triggers repair request and succeeds on second attempt."""
    validator, mock_client = make_validator_with_responses([
        "Not valid JSON {title: broken}",  # 1st attempt: bad
        '{"title": "Repaired Title", "count": 99}',  # 2nd attempt: fixed
    ])
    req = GenerationRequest(system_prompt="sys", user_prompt="usr", json_mode=True)
    res = await validator.generate_and_validate(req, SampleSchema)

    assert res.title == "Repaired Title"
    assert res.count == 99
    assert mock_client.call_count == 2


@pytest.mark.asyncio
async def test_validator_unrepairable_raises_error():
    """Verify persistent invalid JSON exhausts repair attempts and raises StructuredOutputError."""
    validator, mock_client = make_validator_with_responses([
        "Invalid 1",
        "Invalid 2",
        "Invalid 3",
    ])
    req = GenerationRequest(system_prompt="sys", user_prompt="usr", json_mode=True)
    with pytest.raises(StructuredOutputError) as exc_info:
        await validator.generate_and_validate(req, SampleSchema)

    assert "Failed to produce valid structured output" in str(exc_info.value)
    assert mock_client.call_count == 3  # Initial + 2 retries
