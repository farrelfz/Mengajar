"""
KIR AI Document Intelligence — Application Settings.

All configuration is loaded from environment variables (via .env file).
Secrets use SecretStr and are never logged.

Environment variables follow the KIR_ prefix convention.
See docs/01_FOUNDATION/ENVIRONMENT_SETUP.md and AI_SETUP.md.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _discover_9router_env() -> dict[str, str]:
    """Discover environment variables from ~/.config/9router/env if available."""
    discovered: dict[str, str] = {}
    config_env = Path.home() / ".config" / "9router" / "env"
    if config_env.exists():
        try:
            for line in config_env.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:].strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    discovered[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:
            pass
    return discovered


_ROUTER_ENV = _discover_9router_env()


def _env_get(key: str, default: str = "") -> str:
    """Retrieve an env var from os.environ or ~/.config/9router/env fallback."""
    return os.getenv(key, _ROUTER_ENV.get(key, default))


class AppSettings(BaseSettings):
    """Central application configuration.

    Loaded from environment variables with KIR_ prefix.
    All secrets use SecretStr and are not serialized to logs.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="KIR_",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────
    app_name: str = Field(default="KIR AI Document Intelligence")
    app_env: Literal["development", "production", "test"] = Field(
        default="development", alias="KIR_APP_ENV"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    log_to_file: bool = Field(default=False)

    # ── AI Provider — 9Router (Local Gateway / Cloud) ─────────────────────
    nine_router_api_key: SecretStr | None = Field(
        default_factory=lambda: SecretStr(k) if (k := _env_get("NINEROUTER_API_KEY")) else None
    )
    nine_router_base_url: str = Field(
        default_factory=lambda: _env_get("NINEROUTER_BASE_URL", "http://127.0.0.1:20128/v1")
    )
    nine_router_timeout: float = Field(default=60.0, ge=5.0, le=300.0)
    nine_router_max_retries: int = Field(default=3, ge=0, le=10)

    # ── 9Router Local Model Routing Presets ────────────────────────────────
    ai_default_model: str = Field(
        default_factory=lambda: _env_get("AI_DEFAULT_MODEL", "ag/gemini-3.7-flash-high")
    )
    ai_fast_model: str = Field(
        default_factory=lambda: _env_get("AI_FAST_MODEL", "ag/gemini-3.6-flash-medium")
    )
    ai_reasoning_model: str = Field(
        default_factory=lambda: _env_get("AI_REASONING_MODEL", "gh/gpt-5.6-luna")
    )
    ai_code_model: str = Field(
        default_factory=lambda: _env_get("AI_CODE_MODEL", "gh/gpt-5.3-codex")
    )
    ai_long_context_model: str = Field(
        default_factory=lambda: _env_get("AI_LONG_CONTEXT_MODEL", "ollama/qwen3.5")
    )
    active_model: str | None = Field(default=None)

    # ── AI Provider — Ollama ───────────────────────────────────────────────
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_timeout: float = Field(default=120.0, ge=5.0, le=600.0)
    ollama_default_model: str = Field(default="llama3.1:8b")

    # ── Model configuration ────────────────────────────────────────────────
    primary_provider: str = Field(default="auto")
    fallback_to_ollama: bool = Field(default=True)
    offline_mode: bool = Field(default=False)
    ai_timeout_seconds: float = Field(default=60.0, ge=5.0, le=300.0)

    # ── Intelligence pipeline ──────────────────────────────────────────────
    max_repair_attempts: int = Field(default=2, ge=0, le=5)
    min_confidence_threshold: float = Field(default=0.4, ge=0.0, le=1.0)
    enable_research_traceability: bool = Field(default=True)
    enable_source_fidelity_check: bool = Field(default=True)

    # ── Paths ──────────────────────────────────────────────────────────────
    prompts_dir: Path = Field(default=Path("prompts"))
    templates_dir: Path = Field(default=Path("templates"))
    themes_dir: Path = Field(default=Path("themes"))
    output_dir: Path = Field(default=Path("outputs"))
    log_dir: Path = Field(default=Path("logs"))
    data_dir: Path = Field(default=Path("data"))

    # ── Validators ────────────────────────────────────────────────────────
    @field_validator("prompts_dir", "templates_dir", "themes_dir", mode="before")
    @classmethod
    def validate_path_exists_or_create(cls, v: str | Path) -> Path:
        p = Path(v)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @model_validator(mode="after")
    def check_provider_config(self) -> AppSettings:
        if self.primary_provider == "9router" and not self.offline_mode and self.nine_router_api_key is None:
            # Check if running against local 9router gateway (localhost / 127.0.0.1)
            if "127.0.0.1" in self.nine_router_base_url or "localhost" in self.nine_router_base_url:
                self.nine_router_api_key = SecretStr("sk-9router-local")
            else:
                raise ValueError(
                    "KIR_NINE_ROUTER_API_KEY or NINEROUTER_API_KEY must be set when primary_provider='9router' "
                    "and offline_mode=False. Use primary_provider='ollama' for local-only mode."
                )
        return self

    # ── Convenience ────────────────────────────────────────────────────────
    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def nine_router_api_key_value(self) -> str | None:
        """Safely retrieve the API key value. Never log this."""
        if self.nine_router_api_key is None:
            return None
        return self.nine_router_api_key.get_secret_value()

    def set_active_model(self, model_id: str | None) -> None:
        """Dynamically override active 9Router model."""
        self.active_model = model_id

    def get_effective_model(self, capability_name: str | None = None) -> str:
        """Return the effective active model or mapped preset."""
        if self.active_model:
            return self.active_model
        if capability_name in ("fast", "content_writing", "fallback"):
            return self.ai_fast_model
        if capability_name in ("reasoning", "semantic_reasoning", "critique"):
            return self.ai_reasoning_model
        return self.ai_default_model


# Module-level singleton — imported by other modules.
# Do not instantiate AppSettings in multiple places.
_settings: AppSettings | None = None


def get_settings() -> AppSettings:
    """Return the application settings singleton.

    Instantiated on first call and cached thereafter.
    In tests, call reset_settings() before creating a new instance.
    """
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings


def reset_settings() -> None:
    """Reset the settings singleton. Intended for use in tests only."""
    global _settings
    _settings = None
