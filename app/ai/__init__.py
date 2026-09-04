"""KIR AI Provider package."""

from app.ai.client import AICapability, AIClient, GenerationRequest, GenerationResponse
from app.ai.fallback import FallbackChain
from app.ai.model_registry import ModelRegistry, get_registry
from app.ai.model_selector import ModelSelector
from app.ai.ollama_client import OllamaClient
from app.ai.router import NineRouterClient

__all__ = [
    "AICapability",
    "AIClient",
    "GenerationRequest",
    "GenerationResponse",
    "FallbackChain",
    "ModelRegistry",
    "get_registry",
    "ModelSelector",
    "NineRouterClient",
    "OllamaClient",
]
