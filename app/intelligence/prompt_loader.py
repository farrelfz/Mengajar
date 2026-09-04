"""
KIR AI Document Intelligence — Prompt Loader.

Loads, validates, and caches modular YAML prompt specifications from prompts_dir.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from app.config.settings import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)


class PromptTemplate(BaseModel):
    """Parsed YAML prompt contract."""

    name: str
    description: str
    version: str = "1.0"
    capabilities: list[str] = Field(default_factory=list)
    system_prompt: str
    schema_hint: str | None = None


class PromptLoader:
    """Loads and caches YAML prompts from the configured directory."""

    def __init__(self, prompts_dir: Path | None = None) -> None:
        self.prompts_dir = prompts_dir or get_settings().prompts_dir
        self._cache: dict[str, PromptTemplate] = {}

    def get_prompt(self, prompt_name: str, fallback_system_prompt: str = "") -> PromptTemplate:
        """Retrieve a prompt template by name (with optional .yaml extension).

        If file is missing or invalid, returns a default PromptTemplate with fallback_system_prompt.
        """
        key = prompt_name.replace(".yaml", "").replace(".yml", "")
        if key in self._cache:
            return self._cache[key]

        yaml_path = self.prompts_dir / f"{key}.yaml"
        if not yaml_path.exists():
            yaml_path = self.prompts_dir / f"{key}.yml"

        if yaml_path.exists():
            try:
                with open(yaml_path, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if isinstance(data, dict) and "system_prompt" in data:
                    template = PromptTemplate(
                        name=data.get("name", key),
                        description=data.get("description", ""),
                        version=str(data.get("version", "1.0")),
                        capabilities=data.get("capabilities", []),
                        system_prompt=data["system_prompt"].strip(),
                        schema_hint=data.get("schema_hint"),
                    )
                    self._cache[key] = template
                    log.debug("prompt_loader.loaded", name=key, path=str(yaml_path))
                    return template
            except Exception as exc:
                log.warning("prompt_loader.error", name=key, error=str(exc))

        # Return fallback
        fallback = PromptTemplate(
            name=key,
            description="Fallback prompt",
            system_prompt=fallback_system_prompt.strip() or "You are an expert document AI.",
        )
        self._cache[key] = fallback
        return fallback


# Singleton loader instance
_loader: PromptLoader | None = None


def get_prompt_loader() -> PromptLoader:
    global _loader
    if _loader is None:
        _loader = PromptLoader()
    return _loader
