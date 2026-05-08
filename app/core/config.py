from functools import lru_cache

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Backend Template"
    app_version: str = "0.1.0"
    app_env: str = "local"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://app_user:app_password@localhost:5432/app_db"
    secret_key: str = Field(default="change-this-secret-key", min_length=16)
    access_token_expire_minutes: int = 30
    backend_cors_origins: list[AnyUrl] = Field(default_factory=list)
    redis_url: str = "redis://localhost:6379/0"
    redis_prefix: str = "backend"
    redis_default_ttl_seconds: int = 300
    log_level: str = "INFO"
    log_format: str = "json"
    service_name: str = "fastapi-backend-template"
    environment: str = "dev"
    log_output: str = "stdout"
    log_file_path: str = "logs/app.log"
    log_file_max_bytes: int = 104_857_600
    log_file_backup_count: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
