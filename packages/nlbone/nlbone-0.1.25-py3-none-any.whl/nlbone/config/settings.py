from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    model_config = SettingsConfigDict(
        env_prefix="NLBONE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Cached settings for fast access across the app.
    Usage:
        from nlbone.config.settings import get_settings
        settings = get_settings()
    """
    return Settings()
