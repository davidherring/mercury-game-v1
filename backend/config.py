from functools import lru_cache
from pathlib import Path
import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_env_file() -> Path | None:
    here = Path(__file__).resolve()
    repo_root = here.parent.parent
    mercury_env = (os.environ.get("MERCURY_ENV") or "").strip().lower()
    explicit_str = os.environ.get("ENV_FILE") or os.environ.get("MERCURY_ENV_FILE")
    explicit = Path(explicit_str) if explicit_str else None
    if explicit and explicit.exists():
        return explicit
    if mercury_env == "test":
        return None
    candidate = repo_root / "apps" / "api" / ".env"
    if candidate.exists():
        return candidate
    fallback = repo_root / ".env"
    return fallback


class Settings(BaseSettings):
    database_url: str = Field(default="", validation_alias="SUPABASE_DATABASE_URL")
    app_env: str = Field(default="local", validation_alias="APP_ENV")
    mercury_env: str = Field(default="dev", validation_alias="MERCURY_ENV")
    llm_provider: str | None = Field(default=None, validation_alias="LLM_PROVIDER")
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str | None = Field(default=None, validation_alias="OPENAI_MODEL")
    openai_round3_debate_speeches: bool = Field(
        default=False, validation_alias="OPENAI_ROUND3_DEBATE_SPEECHES"
    )

    _env_file = _default_env_file()
    model_config = SettingsConfigDict(
        env_file=str(_env_file) if _env_file else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def validate_required(self) -> None:
        if not self.database_url:
            if self.mercury_env == "test":
                raise ValueError(
                    "SUPABASE_DATABASE_URL is missing for tests. Export SUPABASE_DATABASE_URL, "
                    "or create apps/api/.env.test, or set MERCURY_ENV_FILE/ENV_FILE to a file containing "
                    "SUPABASE_DATABASE_URL."
                )
            raise ValueError(
                "SUPABASE_DATABASE_URL is missing. Set it in apps/api/.env or via ENV_FILE/MERCURY_ENV_FILE, "
                "or export SUPABASE_DATABASE_URL."
            )

        # No validation for optional OpenAI fields; acceptance is enough to avoid extra_forbidden errors

    @field_validator("mercury_env")
    @classmethod
    def _validate_mercury_env(cls, value: str) -> str:
        normalized = value.strip().lower() if isinstance(value, str) else ""
        allowed = {"test", "dev", "prod"}
        if normalized not in allowed:
            raise ValueError("MERCURY_ENV must be one of: test, dev, prod")
        return normalized


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_required()
    return settings


__all__ = ["Settings", "get_settings"]
