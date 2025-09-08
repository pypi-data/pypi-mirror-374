import os
from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic import AnyHttpUrl, Field, SecretStr, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


def _guess_env_file() -> str | None:
    explicit = os.getenv("NLBONE_ENV_FILE")
    if explicit:
        return explicit

    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        return str(cwd_env)

    for i in range(1, 8):
        p = Path(__file__).resolve().parents[i]
        f = p / ".env"
        if f.exists():
            return str(f)


class Settings(BaseSettings):
    # ---------------------------
    # App
    # ---------------------------
    ENV: Literal["local", "dev", "staging", "prod"] = Field(default="local")
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = Field(default="INFO")
    LOG_JSON: bool = Field(default=True)

    # ---------------------------
    # HTTP / Timeouts
    # ---------------------------
    HTTP_TIMEOUT_SECONDS: float = Field(default=10.0)

    # ---------------------------
    # Keycloak / Auth
    # ---------------------------
    KEYCLOAK_SERVER_URL: AnyHttpUrl = Field(default="https://keycloak.local/auth")
    KEYCLOAK_REALM_NAME: str = Field(default="numberland")
    KEYCLOAK_CLIENT_ID: str = Field(default="nlbone")
    KEYCLOAK_CLIENT_SECRET: SecretStr = Field(default=SecretStr("dev-secret"))

    # ---------------------------
    # Database
    # ---------------------------
    POSTGRES_DB_DSN: str = Field(default="postgresql+asyncpg://user:pass@localhost:5432/nlbone")

    # ---------------------------
    # Messaging / Cache
    # ---------------------------
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # ---------------------------
    # UPLOADCHI 
    # ---------------------------
    UPLOADCHI_BASE_URL: AnyHttpUrl = Field(default="https://uploadchi.numberland.ir/v1/files")
    UPLOADCHI_TOKEN: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("NLBONE_UPLOADCHI_TOKEN", "UPLOADCHI_TOKEN"),
    )

    model_config = SettingsConfigDict(
        env_prefix="NLBONE_",
        env_file=None,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=4)
def get_settings(env_file: str | None = None) -> Settings:
    """
    Cached settings for fast access across the app.
    Usage:
        from nlbone.config.settings import get_settings
        settings = get_settings()
    """
    env_file = env_file or _guess_env_file()
    return Settings(_env_file=env_file)
