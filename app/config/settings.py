"""
KIR AI Document Intelligence — Application Settings.

All configuration is loaded from environment variables (via .env file).
Secrets use SecretStr and are never logged.

Environment variables follow the KIR_ prefix convention.
See docs/01_FOUNDATION/ENVIRONMENT_SETUP.md and AI_SETUP.md.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # ── AI Provider — 9Router ──────────────────────────────────────────────
    nine_router_api_key: SecretStr | None = Field(default=None)
    nine_router_base_url: str = Field(default="https://api.9router.io/v1")
    nine_router_timeout: float = Field(default=60.0, ge=5.0, le=300.0)
    nine_router_max_retries: int = Field(default=3, ge=0, le=10)

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
            raise ValueError(
                "KIR_NINE_ROUTER_API_KEY must be set when primary_provider='9router' "
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
