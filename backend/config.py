from functools import lru_cache
from pathlib import Path
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_env_file() -> Path:
    here = Path(__file__).resolve()
    repo_root = here.parent.parent
    explicit_str = os.environ.get("ENV_FILE") or os.environ.get("MERCURY_ENV_FILE")
    explicit = Path(explicit_str) if explicit_str else None
    if explicit and explicit.exists():
        return explicit
    candidate = repo_root / "apps" / "api" / ".env"
    if candidate.exists():
        return candidate
    fallback = repo_root / ".env"
    return fallback


class Settings(BaseSettings):
    database_url: str = Field(default="", validation_alias="SUPABASE_DATABASE_URL")
    app_env: str = Field(default="local", validation_alias="APP_ENV")

    model_config = SettingsConfigDict(
        env_file=str(_default_env_file()),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def validate_required(self) -> None:
        if not self.database_url:
            raise ValueError(
                "SUPABASE_DATABASE_URL is missing. Set it in apps/api/.env or via ENV_FILE/MERCURY_ENV_FILE, "
                "or export SUPABASE_DATABASE_URL."
            )


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_required()
    return settings


__all__ = ["Settings", "get_settings"]
